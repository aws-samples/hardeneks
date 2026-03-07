from ...resources import Resources
from hardeneks.rules import Rule, Result


class use_encryption_with_ebs(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "encryption_secrets"
    message = "EBS Storage Classes should have encryption parameter."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/data/#encryption-at-rest"

    def check(self, resources: Resources):
        offenders = []

        for storage_class in resources.storage_classes:
            if storage_class.provisioner in ["ebs.csi.aws.com", "ebs.csi.eks.amazonaws.com"]:
                if storage_class.parameters:
                    encrypted = storage_class.parameters.get("encrypted")
                    if not encrypted:
                        offenders.append(storage_class)
                    elif encrypted == "false":
                        offenders.append(storage_class)
                else:
                    # No parameters means no encryption specified
                    offenders.append(storage_class)

        self.result = Result(status=True, resource_type="StorageClass")

        if offenders:
            self.result = Result(
                status=False,
                resource_type="StorageClass",
                resources=[i.metadata.name for i in offenders],
            )


class use_encryption_with_efs(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "encryption_secrets"
    message = "EFS Persistent volumes should have encryptInTransit enabled."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/data/#encryption-at-rest"

    def check(self, resources: Resources):
        offenders = []

        for persistent_volume in resources.persistent_volumes:
            csi = persistent_volume.spec.csi
            if csi and csi.driver == "efs.csi.aws.com":
                volume_attributes = getattr(csi, 'volume_attributes', None)
                if volume_attributes:
                    encrypt_in_transit = volume_attributes.get("encryptInTransit")
                    if encrypt_in_transit == "false":
                        offenders.append(persistent_volume)

        self.result = Result(status=True, resource_type="PersistentVolume")

        if offenders:
            self.result = Result(
                status=False,
                resource_type="PersistentVolume",
                resources=[i.metadata.name for i in offenders],
            )


class use_efs_access_points(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "encryption_secrets"
    message = "EFS Persistent volumes should leverage access points."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/data/#use-efs-access-points-to-simplify-access-to-shared-datasets"

    def check(self, resources: Resources):

        offenders = []

        for persistent_volume in resources.persistent_volumes:
            csi = persistent_volume.spec.csi
            if csi and csi.driver == "efs.csi.aws.com":
                if "::" not in csi.volume_handle:
                    offenders.append(persistent_volume)

        self.result = Result(status=True, resource_type="PersistentVolume")

        if offenders:
            self.result = Result(
                status=False,
                resource_type="PersistentVolume",
                resources=[i.metadata.name for i in offenders],
            )
