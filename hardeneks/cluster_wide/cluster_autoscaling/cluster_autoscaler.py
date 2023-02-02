import boto3
from kubernetes import client
from rich.panel import Panel

from hardeneks import console
from ...resources import Resources
from ...report import print_role_action_table, print_node_table


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


def check_any_cluster_autoscaler_exists(resources: Resources):

    deployments = [
        i.metadata.name
        for i in client.AppsV1Api().list_deployment_for_all_namespaces().items
    ]

    if not ("cluster-autoscaler" in deployments or "karpenter" in deployments):
        console.print(
            Panel(
                "[red]Cluster Autoscaler or Karpeneter is not deployed.",
                subtitle="[link=https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/]Click to see the guide[/link]",
            )
        )
        console.print()
        return False
    else:
        return True


def ensure_cluster_autoscaler_and_cluster_versions_match(resources: Resources):
    eks_client = boto3.client("eks", region_name=resources.region)
    cluster_metadata = eks_client.describe_cluster(name=resources.cluster)

    cluster_version = cluster_metadata["cluster"]["version"]

    deployments = client.AppsV1Api().list_deployment_for_all_namespaces().items

    for deployment in deployments:
        if deployment.metadata.name == "cluster-autoscaler":
            ca_containers = deployment.spec.template.spec.containers
            ca_image = ca_containers[0].image
            ca_image_version = ca_image.split(":")[-1]
            if cluster_version not in ca_image_version:
                console.print(
                    Panel(
                        f"[red]CA({ca_image_version})-k8s({cluster_version}) Cross version compatibility is not recommended.",
                        subtitle="[link=https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#operating-the-cluster-autoscaler]Click to see the guide[/link]",
                    )
                )
                console.print()
                return False
            else:
                return True


def ensure_cluster_autoscaler_has_autodiscovery_mode(resources: Resources):

    deployments = client.AppsV1Api().list_deployment_for_all_namespaces().items

    for deployment in deployments:
        if deployment.metadata.name == "cluster-autoscaler":
            ca_containers = deployment.spec.template.spec.containers
            ca_command = ca_containers[0].command
            if not any(
                "node-group-auto-discover" in item for item in ca_command
            ):
                console.print(
                    Panel(
                        "[red]Auto discovery is not enabled for Cluster Autoscaler",
                        subtitle="[link=https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#operating-the-cluster-autoscaler]Click to see the guide[/link]",
                    )
                )
                console.print()
                return False
            else:
                break

    return True


def use_separate_iam_role_for_cluster_autoscaler(resources: Resources):
    deployments = client.AppsV1Api().list_deployment_for_all_namespaces().items

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
                console.print(
                    Panel(
                        "[red]Cluster-autoscaler deployment does not use a dedicated IAM Role (IRSA)",
                        subtitle="[link=https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#employ-least-privileged-access-to-the-iam-role]Click to see the guide[/link]",
                    )
                )
                console.print()
                return False
            else:
                break

    return True


def employ_least_privileged_access_cluster_autoscaler_role(
    resources: Resources,
):
    deployments = client.AppsV1Api().list_deployment_for_all_namespaces().items

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
                    print_role_action_table(
                        set(actions) - ACTIONS,
                        "[red]Cluster autoscaler role has unnecessary actions assigned.",
                        "[link=https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#employ-least-privileged-access-to-the-iam-role]Click to see the guide[/link]",
                    )
                    return False
                else:
                    return True

    return False


def use_managed_nodegroups(resources: Resources):

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

    if offenders:
        print_node_table(
            offenders,
            "[red]Following nodes are not part of a managed noge group.",
            "[link=https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#configuring-your-node-groups]Click to see the guide[/link]",
        )
    return offenders
