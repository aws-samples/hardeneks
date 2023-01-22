from collections import Counter

from rich.console import Console

from ...resources import NamespacedResources


console = Console()


def disable_anonymous_access_for_roles(resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "RoleBinding"
    objectsList = []
    rolenameslist = ""
    
    for role_binding in resources.role_bindings:
        if role_binding.subjects:
            for subject in role_binding.subjects:
                if (
                    subject.name == "system:unauthenticated"
                    or subject.name == "system:anonymous"
                ):
                    objectsList.append(role_binding)
                    rolenameslist += role_binding.metadata.name

    if objectsList:
        status = False
        message = "Roles bound to to anonymous/unauthenticated groups: " + rolenameslist
    else:
        status = True
        message = "There are no Roles bound to to anonymous/unauthenticated groups"
    
    return (status, message, objectsList, objectType)
    
    
    
def restrict_wildcard_for_roles(resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Role"
    objectsList = []
    rolenameslist = ""

    if resources.roles:
        for role in resources.roles:
            if role.rules:
                for rule in role.rules:
                    if "*" in rule.verbs:
                        objectsList.append(role)
                    if "*" in rule.resources:
                        objectsList.append(role)

    if objectsList:
        status = False
        message = "Roles with '*' in Verbs or Resources are: " + rolenameslist
    else:
        status = True
        message = "There are no Roles with '*' in Verbs or Resources"
    
    return (status, message, objectsList, objectType)
    
    

def disable_service_account_token_mounts(resources: NamespacedResources):

    status = None
    message = ""
    objectType = "Pod"
    objectsList = []
    rolenameslist = ""

    for pod in resources.pods:
        if pod.spec.automount_service_account_token:
            objectsList.append(pod)

    if objectsList:
        status = False
        message = "Auto-mounting of Service Account tokens is not allowed"
    else:
        status = True
        message = "There is no Auto-mounting of Service Account tokens"
    
    return (status, message, objectsList, objectType)
    
    
def disable_run_as_root_user(resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Pod"
    objectsList = []

    for pod in resources.pods:
        security_context = pod.spec.security_context
        if (
            not security_context.run_as_group
            and not security_context.run_as_user
        ):
            objectsList.append(pod)

    if objectsList:
        status = False
        message = "Running as root is not allowed"
    else:
        status = True
        message = "There are no pod running as root"
    
    return (status, message, objectsList, objectType)


def use_dedicated_service_accounts_for_each_deployment(resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Deployment"
    objectsList = []
    
    count = Counter(
        [
            i.spec.template.spec.service_account_name
            for i in resources.deployments
        ]
    )
    repeated_service_accounts = {
        x: count for x, count in count.items() if count > 1
    }

    for k, v in repeated_service_accounts.items():
        for deployment in resources.deployments:
            if k == deployment.spec.template.spec.service_account_name:
                objectsList.append(deployment)

    if objectsList:
        status = False
        message = "Don't share service accounts between Deployments"
    else:
        status = True
        message = "There are no shared service accounts between Deployments"
    
    return (status, message, objectsList, objectType)

def use_dedicated_service_accounts_for_each_stateful_set(resources: NamespacedResources):


    status = None
    message = ""
    objectType = "StatefulSet"
    objectsList = []
    
    count = Counter(
        [
            i.spec.template.spec.service_account_name
            for i in resources.stateful_sets
        ]
    )
    repeated_service_accounts = {
        x: count for x, count in count.items() if count > 1
    }

    for k, v in repeated_service_accounts.items():
        for deployment in resources.stateful_sets:
            if k == deployment.spec.template.spec.service_account_name:
                objectsList.append(deployment)

    if objectsList:
        status = False
        message = "Don't share service accounts between StatefulSets"
    else:
        status = True
        message = "There are no shared service accounts between StatefulSets"
    
    return (status, message, objectsList, objectType)



def use_dedicated_service_accounts_for_each_daemon_set(resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "DaemonSet"
    objectsList = []
    
    count = Counter(
        [
            i.spec.template.spec.service_account_name
            for i in resources.daemon_sets
        ]
    )
    repeated_service_accounts = {
        x: count for x, count in count.items() if count > 1
    }

    for k, v in repeated_service_accounts.items():
        for deployment in resources.daemon_sets:
            if k == deployment.spec.template.spec.service_account_name:
                objectsList.append(deployment)

    if objectsList:
        status = False
        message = "Don't share service accounts between DaemonSet"
    else:
        status = True
        message = "There are no shared service accounts between DaemonSet"
    
    return (status, message, objectsList, objectType)
    
