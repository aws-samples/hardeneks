from rich.console import Console

import copy

from ...resources import Resources

console = Console()


def ensure_namespace_quotas_exist(resources: Resources):

    status = None
    message = ""
    objectType = "Namespace"
    objectsList = []
    
    objectsList = copy.deepcopy(resources.namespaces)
    
    for quota in resources.resource_quotas:
        if quota.metadata.namespace in objectsList:
            objectsList.remove(quota.metadata.namespace)        
    
    if objectsList:
        status = False
        message = "Namespaces does not have quotas assigned"
    else:
        status = True
        message = "Namespaces have quotas assigned"
    
    return (status, message, objectsList, objectType)