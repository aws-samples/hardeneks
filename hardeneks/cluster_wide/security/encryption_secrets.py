from ...resources import Resources

def use_encryption_with_ebs(resources: Resources):
    
    status = None
    message = ""
    objectType = "StorageClass"
    objectsList = []
    

    for storage_class in resources.storage_classes:
        if storage_class.provisioner == "ebs.csi.aws.com":
            encrypted = storage_class.parameters.get("encrypted")
            if not encrypted:
                objectsList.append(storage_class)
            elif encrypted == "false":
                objectsList.append(storage_class)

    if objectsList:
        status = False
        message = "EBS Storage Classes should have encryption parameter"
    else:
        status = True
        message = "EBS Storage Classes have encrypted parameters"
    
    return (status, message, objectsList, objectType)
    


def use_encryption_with_efs(resources: Resources):
    
    status = None
    message = ""
    objectType = "PersistentVolume"
    objectsList = []
    
    for persistent_volume in resources.persistent_volumes:
        csi = persistent_volume.spec.csi
        if csi and csi.driver == "efs.csi.aws.com":
            mount_options = persistent_volume.spec.mount_options
            if not mount_options:
                objectsList.append(persistent_volume)
            else:
                if "tls" not in mount_options:
                    objectsList.append(persistent_volume)

    if objectsList:
        status = False
        message = "EFS Persistent volumes should have tls mount option"
    else:
        status = True
        message = "EFS Persistent volumes have tls mount option"
    
    return (status, message, objectsList, objectType)
    

def use_efs_access_points(resources: Resources):
    status = None
    message = ""
    objectType = "PersistentVolume"
    objectsList = []

    
    for persistent_volume in resources.persistent_volumes:
        csi = persistent_volume.spec.csi
        if csi and csi.driver == "efs.csi.aws.com":
            if "::" not in csi.volume_handle:
                objectsList.append(persistent_volume)

    if objectsList:
        status = False
        message = "EFS Persistent volumes should leverage access points"
    else:
        status = True
        message = "EFS Persistent volumes are leveraging access points"
    
    return (status, message, objectsList, objectType)

    
    