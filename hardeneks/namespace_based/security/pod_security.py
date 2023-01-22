from rich.console import Console

from ...resources import NamespacedResources


console = Console()


def disallow_container_socket_mount(namespaced_resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Pod"
    objectsList = []
    
    sockets = [
        "/var/run/docker.sock",
        "/var/run/containerd.sock",
        "/var/run/crio.sock",
    ]

    for pod in namespaced_resources.pods:
        for volume in pod.spec.volumes:
            if volume.host_path and volume.host_path.path in sockets:
                objectsList.append(pod)

    if objectsList:
        status = False
        message = "Container socket mounts are not allowed"
    else:
        status = True
        message = "There are no Container socket mounted"
    
    return (status, message, objectsList, objectType)
    
    

def disallow_host_path_or_make_it_read_only(namespaced_resources: NamespacedResources):
  
    status = None
    message = ""
    objectType = "Pod"
    objectsList = []

    
    for pod in namespaced_resources.pods:
        for volume in pod.spec.volumes:
            if volume.host_path:
                objectsList.append(pod)

    if objectsList:
        status = False
        message = "Restrict the use of hostpath"
    else:
        status = True
        message = "hostpath are not mounted"
    
    return (status, message, objectsList, objectType)
    
    
def set_requests_limits_for_containers(namespaced_resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Pod"
    objectsList = []

    for pod in namespaced_resources.pods:
        for container in pod.spec.containers:
            if not (
                container.resources.limits and container.resources.requests
            ):
                objectsList.append(pod)

    if objectsList:
        status = False
        message = "Set requests and limits for each container."
    else:
        status = True
        message = "requests and limits are set for each containers"
    
    return (status, message, objectsList, objectType)
    
    

def disallow_privilege_escalation(namespaced_resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Pod"
    objectsList = []
        
    for pod in namespaced_resources.pods:
        for container in pod.spec.containers:
            if (
                container.security_context
                and container.security_context.allow_privilege_escalation
            ):
                objectsList.append(pod)

    if objectsList:
        status = False
        message = "Set allowPrivilegeEscalation in the pod spec to false"
    else:
        status = True
        message = "allowPrivilegeEscalation in the pod spec is to true"
    
    return (status, message, objectsList, objectType)
    
    

def check_read_only_root_file_system(namespaced_resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Pod"
    objectsList = []
    
    for pod in namespaced_resources.pods:
        for container in pod.spec.containers:
            if (
                container.security_context
                and not container.security_context.read_only_root_filesystem
            ):
                objectsList.append(pod)
    
    if objectsList:
        status = False
        message = "Configure your images with a read-only root file system"
    else:
        status = True
        message = "Images are configured with a read-only root file system"
    
    return (status, message, objectsList, objectType)
    