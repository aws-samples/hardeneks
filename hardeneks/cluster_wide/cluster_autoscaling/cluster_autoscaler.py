import boto3
from kubernetes import client

from hardeneks.rules import Rule, Result
from ...resources import Resources


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
            if type(statement["Action"]) == str:
                actions.append(statement["Action"])
            elif type(statement["Action"]) == list:
                actions.extend(statement["Action"])
    for policy_name in inline_policies:
        response = iam_client.get_role_policy(
            RoleName=role_name, PolicyName=policy_name
        )["PolicyDocument"]["Statement"]
        for statement in response:
            if type(statement["Action"]) == str:
                actions.append(statement["Action"])
            elif type(statement["Action"]) == list:
                actions.extend(statement["Action"])
    return actions


class check_any_cluster_autoscaler_exists(Rule):
    _type = "cluster_wide"
    pillar = "cluster_autoscaling"
    section = "cluster_autoscaler"
    message = "Cluster Autoscaler or Karpenter is not deployed."
    url = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/"

    def check(self, resources: Resources):
        deployments = [
            i.metadata.name
            for i in client.AppsV1Api()
            .list_deployment_for_all_namespaces()
            .items
        ]
        if not (
            "cluster-autoscaler" in deployments or "karpenter" in deployments
        ):
            self.result = Result(status=False, resource_type="Deployment")
        else:
            self.result = Result(status=True, resource_type="Deployment")

        return self.result


class ensure_cluster_autoscaler_and_cluster_versions_match(Rule):
    _type = "cluster_wide"
    pillar = "cluster_autoscaling"
    section = "cluster_autoscaler"
    message = (
        "Cross version compatibility between CA and k8s is not recommended."
    )
    url = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#operating-the-cluster-autoscaler"

    def check(self, resources):
        eks_client = boto3.client("eks", region_name=resources.region)
        cluster_metadata = eks_client.describe_cluster(name=resources.cluster)

        cluster_version = cluster_metadata["cluster"]["version"]

        deployments = (
            client.AppsV1Api().list_deployment_for_all_namespaces().items
        )

        self.result = Result(status=True, resource_type="Deployment")

        for deployment in deployments:
            if deployment.metadata.name == "cluster-autoscaler":
                ca_containers = deployment.spec.template.spec.containers
                ca_image = ca_containers[0].image
                ca_image_version = ca_image.split(":")[-1]
                if cluster_version not in ca_image_version:
                    self.result = Result(
                        status=False, resource_type="Deployment"
                    )


class ensure_cluster_autoscaler_has_autodiscovery_mode(Rule):
    _type = "cluster_wide"
    pillar = "cluster_autoscaling"
    section = "cluster_autoscaler"
    message = "Auto discovery is not enabled for Cluster Autoscaler."
    url = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#operating-the-cluster-autoscaler"

    def check(self, resources):
        deployments = (
            client.AppsV1Api().list_deployment_for_all_namespaces().items
        )

        self.result = Result(status=True, resource_type="Deployment")

        for deployment in deployments:
            if deployment.metadata.name == "cluster-autoscaler":
                ca_containers = deployment.spec.template.spec.containers
                ca_command = ca_containers[0].command
                if not any(
                    "node-group-auto-discover" in item for item in ca_command
                ):
                    self.result = Result(
                        status=False, resource_type="Deployment"
                    )
                else:
                    break


class use_separate_iam_role_for_cluster_autoscaler(Rule):
    _type = "cluster_wide"
    pillar = "cluster_autoscaling"
    section = "cluster_autoscaler"
    message = "Cluster-autoscaler deployment does not use a dedicated IAM Role (IRSA)."
    url = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#employ-least-privileged-access-to-the-iam-role"

    def check(self, resources):
        deployments = (
            client.AppsV1Api().list_deployment_for_all_namespaces().items
        )

        self.result = Result(status=True, resource_type="Deployment")

        for deployment in deployments:
            if deployment.metadata.name == "cluster-autoscaler":
                service_account = (
                    deployment.spec.template.spec.service_account_name
                )
                sa_data = client.CoreV1Api().read_namespaced_service_account(
                    service_account, "kube-system", pretty="true"
                )
                if (
                    "eks.amazonaws.com/role-arn"
                    not in sa_data.metadata.annotations.keys()
                ):
                    self.result = Result(
                        status=False, resource_type="Deployment"
                    )
                else:
                    break


class employ_least_privileged_access_cluster_autoscaler_role(Rule):
    _type = "cluster_wide"
    pillar = "cluster_autoscaling"
    section = "cluster_autoscaler"
    message = "Cluster autoscaler role has unnecessary actions assigned."
    url = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#employ-least-privileged-access-to-the-iam-role"

    def check(self, resources):

        deployments = (
            client.AppsV1Api().list_deployment_for_all_namespaces().items
        )

        iam_client = boto3.client("iam", region_name=resources.region)

        ACTIONS = {
            "autoscaling:DescribeAutoScalingGroups",
            "autoscaling:DescribeAutoScalingInstances",
            "autoscaling:DescribeLaunchConfigurations",
            "autoscaling:DescribeScalingActivities",
            "autoscaling:DescribeTags",
            "ec2:DescribeImages",
            "ec2:DescribeInstanceTypes",
            "ec2:DescribeLaunchTemplateVersions",
            "ec2:GetInstanceTypesFromInstanceRequirements",
            "eks:DescribeNodegroup",
            "autoscaling:SetDesiredCapacity",
            "autoscaling:TerminateInstanceInAutoScalingGroup",
        }
        self.result = Result(status=True, resource_type="IAM Role Action")

        for deployment in deployments:
            if deployment.metadata.name == "cluster-autoscaler":
                service_account = (
                    deployment.spec.template.spec.service_account_name
                )
                sa_data = client.CoreV1Api().read_namespaced_service_account(
                    service_account, "kube-system", pretty="true"
                )
                if (
                    "eks.amazonaws.com/role-arn"
                    not in sa_data.metadata.annotations.keys()
                ):
                    break
                else:

                    sa_iam_role_arn = sa_data.metadata.annotations[
                        "eks.amazonaws.com/role-arn"
                    ]
                    sa_iam_role = sa_iam_role_arn.split("/")[-1]
                    actions = _get_policy_documents_for_role(
                        sa_iam_role, iam_client
                    )

                    if len(set(actions) - ACTIONS) > 0:
                        self.result = Result(
                            status=False,
                            resource_type="IAM Role Action",
                            resources=(set(actions) - ACTIONS),
                        )
                    else:
                        self.result = Result(
                            status=True, resource_type="IAM Role Action"
                        )


class use_managed_nodegroups(Rule):
    _type = "cluster_wide"
    pillar = "cluster_autoscaling"
    section = "cluster_autoscaler"
    message = "Nodes are recommended to be part of a managed node group."
    url = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#configuring-your-node-groups"

    def check(self, resources):
        offenders = []
        nodes = client.CoreV1Api().list_node().items

        for node in nodes:
            labels = node.metadata.labels
            if "eks.amazonaws.com/nodegroup" in labels.keys():
                pass
            elif "alpha.eksctl.io/nodegroup-name" in labels.keys():
                offenders.append(node)
            elif "karpenter.sh/provisioner-name" in labels.keys():
                pass
            else:
                offenders.append(node)

        self.result = Result(status=True, resource_type="Node")

        if offenders:
            self.result = Result(
                status=False,
                resource_type="Node",
                resources=[i.metadata.name for i in offenders],
            )
