import boto3
from kubernetes import client

from hardeneks.rules import Rule, Result
from ...resources import Resources


def _get_role_arn_for_service_account(cluster, region, namespace, service_account_name):
    try:
        eks_client = boto3.client("eks", region_name=region)
        pod_identity_associations = eks_client.list_pod_identity_associations(clusterName=cluster)
        for association in pod_identity_associations.get("associations", []):
            if (
                association.get("namespace") == namespace
                and association.get("serviceAccount") == service_account_name
            ):
                described = eks_client.describe_pod_identity_association(
                    clusterName=cluster, associationId=association.get("associationId")
                )
                return described.get("association", {}).get("roleArn")
    except Exception:
        pass

    sa = client.CoreV1Api().read_namespaced_service_account(name=service_account_name, namespace=namespace)
    if sa.metadata.annotations:
        return sa.metadata.annotations.get("eks.amazonaws.com/role-arn")

    return None


def _get_policy_documents_for_role(role_name, iam_client):
    attached_policies = iam_client.list_attached_role_policies(
        RoleName=role_name
    )["AttachedPolicies"]
    inline_policies = iam_client.list_role_policies(RoleName=role_name)[
        "PolicyNames"
    ]
    actions = []
    for policy_arn in [x["PolicyArn"] for x in attached_policies]:
        version_id = iam_client.get_policy(PolicyArn=policy_arn)["Policy"][
            "DefaultVersionId"
        ]
        response = iam_client.get_policy_version(
            PolicyArn=policy_arn, VersionId=version_id
        )["PolicyVersion"]["Document"]["Statement"]
        for statement in response:
            if statement.get("Effect") == "Allow":
                action = statement.get("Action")
                if isinstance(action, str):
                    actions.append(action)
                elif isinstance(action, list):
                    actions.extend(action)
    for policy_name in inline_policies:
        response = iam_client.get_role_policy(
            RoleName=role_name, PolicyName=policy_name
        )["PolicyDocument"]["Statement"]
        for statement in response:
            if statement.get("Effect") == "Allow":
                action = statement.get("Action")
                if isinstance(action, str):
                    actions.append(action)
                elif isinstance(action, list):
                    actions.extend(action)
    return actions


class check_any_cluster_autoscaler_exists(Rule):
    _type = "cluster_wide"
    pillar = "cluster_autoscaling"
    section = "cluster_autoscaler"
    message = "Deploy Cluster Autoscaler or Karpenter."
    url = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/"

    def check(self, resources: Resources):
        deployments = [i.metadata.name for i in resources.deployments]

        if not any(keyword in d for d in deployments for keyword in ["cluster-autoscaler", "karpenter"]):
            self.result = Result(status=False, resources=["cluster-autoscaler,karpenter"], resource_type="Deployment")
        else:
            self.result = Result(status=True, resource_type="Deployment")


class ensure_cluster_autoscaler_and_cluster_versions_match(Rule):
    _type = "cluster_wide"
    pillar = "cluster_autoscaling"
    section = "cluster_autoscaler"
    message = "Match Cluster Autoscaler version to cluster version."
    url = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#operating-the-cluster-autoscaler"

    def check(self, resources):
        eks_client = boto3.client("eks", region_name=resources.region)
        cluster_metadata = eks_client.describe_cluster(name=resources.cluster)

        cluster_version = cluster_metadata["cluster"]["version"]

        self.result = Result(status=True, resource_type="Deployment")

        for deployment in resources.deployments:
            if "cluster-autoscaler" in deployment.metadata.name:
                ca_containers = deployment.spec.template.spec.containers
                ca_image = ca_containers[0].image
                ca_image_version = ca_image.split(":")[-1]
                if cluster_version not in ca_image_version:
                    self.result = Result(status=False, resources=[deployment.metadata.name], resource_type="Deployment")
                return


class ensure_cluster_autoscaler_has_autodiscovery_mode(Rule):
    _type = "cluster_wide"
    pillar = "cluster_autoscaling"
    section = "cluster_autoscaler"
    message = "Enable auto discovery for Cluster Autoscaler."
    url = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#operating-the-cluster-autoscaler"

    def check(self, resources):
        self.result = Result(status=True, resource_type="Deployment")

        for deployment in resources.deployments:
            if "cluster-autoscaler" in deployment.metadata.name:
                ca_containers = deployment.spec.template.spec.containers
                ca_command = ca_containers[0].command
                if not any("node-group-auto-discovery" in item for item in ca_command):
                    self.result = Result(status=False, resources=[deployment.metadata.name], resource_type="Deployment")
                return


class use_separate_iam_role_for_cluster_autoscaler(Rule):
    _type = "cluster_wide"
    pillar = "cluster_autoscaling"
    section = "cluster_autoscaler"
    message = "Use a dedicated IAM Role (IRSA/Pod Identities) for Cluster Autoscaler."
    url = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#employ-least-privileged-access-to-the-iam-role"

    def check(self, resources):
        self.result = Result(status=True, resource_type="Deployment")

        for deployment in resources.deployments:
            if "cluster-autoscaler" in deployment.metadata.name:
                service_account_name = deployment.spec.template.spec.service_account_name
                sa_namespace = deployment.metadata.namespace

                self.result = Result(status=False, resources=[deployment.metadata.name], resource_type="Deployment")

                role_arn = _get_role_arn_for_service_account(resources.cluster, resources.region, sa_namespace, service_account_name)
                if role_arn:
                    self.result = Result(status=True, resource_type="Deployment")
                return


class employ_least_privileged_access_cluster_autoscaler_role(Rule):
    _type = "cluster_wide"
    pillar = "cluster_autoscaling"
    section = "cluster_autoscaler"
    message = "Use least privilege IAM actions for Cluster Autoscaler role."
    url = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#employ-least-privileged-access-to-the-iam-role"

    def check(self, resources):
        iam_client = boto3.client("iam", region_name=resources.region)

        ACTIONS = {
            "autoscaling:DescribeAutoScalingGroups",
            "autoscaling:DescribeAutoScalingInstances",
            "autoscaling:DescribeLaunchConfigurations",
            "autoscaling:DescribeScalingActivities",
            "ec2:DescribeImages",
            "ec2:DescribeInstanceTypes",
            "ec2:DescribeLaunchTemplateVersions",
            "ec2:GetInstanceTypesFromInstanceRequirements",
            "eks:DescribeNodegroup",
            "autoscaling:SetDesiredCapacity",
            "autoscaling:TerminateInstanceInAutoScalingGroup",
        }
        self.result = Result(status=True, resource_type="IAM Role Action")

        role_arn = None
        for deployment in resources.deployments:
            if "cluster-autoscaler" in deployment.metadata.name:
                service_account_name = deployment.spec.template.spec.service_account_name
                sa_namespace = deployment.metadata.namespace

                role_arn = _get_role_arn_for_service_account(resources.cluster, resources.region, sa_namespace, service_account_name)
                break

        # If we found a role (either Pod Identity or IRSA), check permissions
        if role_arn:
            role_name = role_arn.split("/")[-1]
            actions = _get_policy_documents_for_role(role_name, iam_client)

            if len(set(actions) - ACTIONS) > 0:
                self.result = Result(
                    status=False,
                    resource_type="IAM Role Action",
                    resources=list(set(actions) - ACTIONS),
                )
        else:
            self.result = Result(status=False, resources=["cluster-autoscaler"], resource_type="IAM Role Action")


class use_managed_nodegroups(Rule):
    _type = "cluster_wide"
    pillar = "cluster_autoscaling"
    section = "cluster_autoscaler"
    message = "Use managed node groups for worker nodes."
    url = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#configuring-your-node-groups"

    def check(self, resources):
        offenders = []

        for node in resources.nodes:
            labels = node.metadata.labels
            if "eks.amazonaws.com/nodegroup" in labels.keys():
                pass
            elif "alpha.eksctl.io/nodegroup-name" in labels.keys():
                offenders.append(node.metadata.name)
            elif "karpenter.sh/provisioner-name" in labels.keys():
                pass
            elif "karpenter.sh/nodepool" in labels.keys():
                pass
            else:
                offenders.append(node.metadata.name)

        self.result = Result(status=True, resource_type="Node")

        if offenders:
            self.result = Result(
                status=False,
                resource_type="Node",
                resources=offenders,
            )
