import boto3
from kubernetes import client

from hardeneks.rules import Rule, Result
from ...resources import Resources


class restrict_wildcard_for_cluster_roles(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "iam"
    message = "ClusterRoles should not have '*' in Verbs or Resources."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#employ-least-privileged-access-when-creating-rolebindings-and-clusterrolebindings"

    def check(self, resources: Resources):

        offenders = []
        self.result = Result(status=True, resource_type="Cluster Role")

        allow_list = [
            "aws-node",
            "cluster-admin",
            "eks:addon-manager",
            "eks:cloud-controller-manager",
            "eks:service-operations"
        ]

        for role in resources.cluster_roles:
            role_name = role.metadata.name
            if not (role_name.startswith("system:") or role_name in allow_list):
                if role.rules:
                    for rule in role.rules:
                        if rule.verbs and "*" in rule.verbs:
                            offenders.append(role_name)
                            break
                        if rule.resources and "*" in rule.resources:
                            offenders.append(role_name)
                            break

        if offenders:
            self.result = Result(
                status=False,
                resources=offenders,
                resource_type="Cluster Role",
            )


class check_endpoint_public_access(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "iam"
    message = "EKS Cluster Endpoint is Public."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#make-the-eks-cluster-endpoint-private"

    def check(self, resources: Resources):
        client = boto3.client("eks", region_name=resources.region)
        cluster_metadata = client.describe_cluster(name=resources.cluster)
        endpoint_access = cluster_metadata["cluster"]["resourcesVpcConfig"][
            "endpointPublicAccess"
        ]
        self.result = Result(status=True, resource_type="Cluster Endpoint")

        if endpoint_access:
            self.result = Result(
                status=False, resource_type="Cluster Endpoint"
            )


class check_aws_node_daemonset_service_account(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "iam"
    message = "aws-node daemonset should use IRSA or EKS Pod Identity."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#update-the-aws-node-daemonset-to-use-irsa"

    def check(self, resources: Resources):

        daemonset = client.AppsV1Api().read_namespaced_daemon_set(
            name="aws-node", namespace="kube-system"
        )

        service_account_name = daemonset.spec.template.spec.service_account_name
        service_account = client.CoreV1Api().read_namespaced_service_account(
            name=service_account_name,
            namespace="kube-system",
        )

        self.result = Result(status=False, resources=["aws-node"], resource_type="Daemonset")

        # Check for Pod Identity
        try:
            eks_client = boto3.client("eks", region_name=resources.region)
            pod_identity_associations = eks_client.list_pod_identity_associations(
                clusterName=resources.cluster
            )
            
            for association in pod_identity_associations.get("associations", []):
                if (
                    association.get("namespace") == "kube-system"
                    and association.get("serviceAccount") == service_account_name
                ):
                    self.result = Result(status=True, resource_type="Daemonset")
                    return
        except Exception:
            # If Pod Identity API fails, fall back to IRSA-only check
            pass

        # Check for IRSA
        if service_account.metadata.annotations:
            if "eks.amazonaws.com/role-arn" in service_account.metadata.annotations:
                self.result = Result(status=True, resource_type="Daemonset")


class check_access_to_instance_profile(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "iam"
    message = "Restrict access to the instance profile assigned to nodes."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#restrict-access-to-the-instance-profile-assigned-to-the-worker-node"

    def check(self, resources: Resources):
        client = boto3.client("ec2", region_name=resources.region)
        offenders = []

        paginator = client.get_paginator('describe_instances')
        page_iterator = paginator.paginate(PaginationConfig={'PageSize': 1000},
            Filters=[
                {
                    "Name": "tag:aws:eks:cluster-name",
                    "Values": [
                        resources.cluster,
                    ],
                },
            ]
        )

        for page in page_iterator:
            for reservation in page["Reservations"]:
                metadata_options = reservation["Instances"][0]["MetadataOptions"]
                hop_limit = metadata_options["HttpPutResponseHopLimit"]
                http_tokens = metadata_options.get("HttpTokens", "optional")
                
                if hop_limit != 1 or http_tokens != "required":
                    offenders.append(reservation)

        self.result = Result(status=True, resource_type="Node")

        if offenders:
            self.result = Result(
                status=False,
                resource_type="Node",
                resources=[i["Instances"][0]["InstanceId"] for i in offenders],
            )


class disable_anonymous_access_for_cluster_roles(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "iam"
    message = "Don't bind clusterroles to anonymous/unauthenticated groups."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#review-and-revoke-unnecessary-anonymous-access"

    def check(self, resources: Resources):
        offenders = []

        ignored = ["system:public-info-viewer"]

        for cluster_role_binding in resources.cluster_role_bindings:
            if (
                cluster_role_binding.subjects
                and cluster_role_binding.metadata.name not in ignored
            ):
                for subject in cluster_role_binding.subjects:
                    if (
                        subject.name == "system:unauthenticated"
                        or subject.name == "system:anonymous"
                    ):
                        offenders.append(cluster_role_binding.metadata.name)
                        break

        self.result = Result(status=True, resource_type="ClusterRoleBinding")
        if offenders:
            self.result = Result(
                status=False,
                resource_type="ClusterRoleBinding",
                resources=offenders,
            )
