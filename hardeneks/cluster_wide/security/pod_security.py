import kubernetes

from ...resources import Resources

def ensure_namespace_psa_exist(resources: Resources):
    
    status = None
    message = ""
    objectType = "Namespace"
    objectsList = []
    
    for namespace in resources.namespaceObjList:
        if namespace.metadata.name not in resources.namespaces:
            if namespace.metadata.labels:
                labels = namespace.metadata.labels.keys()
                if "pod-security.kubernetes.io/enforce" not in labels:
                    objectsList.append(namespace.metadata.name)
                elif "pod-security.kubernetes.io/warn" not in labels:
                    objectsList.append(namespace.metadata.name)

    if objectsList:
        status = False
        message = "Namespaces should have psa modes"
    else:
        status = True
        message = "Namespaces have psa modes"
    
    return (status, message, objectsList, objectType)
    
