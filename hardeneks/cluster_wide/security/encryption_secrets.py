from ...resources import Resources
from ...report import print_storage_class_table, print_persistent_volume_table


def use_encryption_with_ebs(resources: Resources):
    offenders = []

    for storage_class in resources.storage_classes:
        if storage_class.provisioner == "ebs.csi.aws.com":
            encrypted = storage_class.parameters.get("encrypted")
            if not encrypted:
                offenders.append(storage_class)
            elif encrypted == "false":
                offenders.append(storage_class)

    if offenders:
        print_storage_class_table(
            offenders,
            "[red]EBS Storage Classes should have encryption parameter",
        )
    return offenders


def use_encryption_with_efs(resources: Resources):
    offenders = []

    for persistent_volume in resources.persistent_volumes:
        csi = persistent_volume.spec.csi
        if csi and csi.driver == "efs.csi.aws.com":
            mount_options = persistent_volume.spec.mount_options
            if not mount_options:
                offenders.append(persistent_volume)
            else:
                if "tls" not in mount_options:
                    offenders.append(persistent_volume)

    if offenders:
        print_persistent_volume_table(
            offenders,
            "[red]EFS Persistent volumes should have tls mount option",
        )
    return offenders


def use_efs_access_points(resources: Resources):
    offenders = []

    for persistent_volume in resources.persistent_volumes:
        csi = persistent_volume.spec.csi
        if csi and csi.driver == "efs.csi.aws.com":
            if "::" not in csi.volume_handle:
                offenders.append(persistent_volume)

    if offenders:
        print_persistent_volume_table(
            offenders,
            "[red]EFS Persistent volumes should leverage access points",
        )
    return offenders
