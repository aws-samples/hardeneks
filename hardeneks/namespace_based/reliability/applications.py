from ...resources import NamespacedResources


def check_horizontal_pod_autoscaling_exists(namespaced_resources: NamespacedResources,):
    
    status = None
    message = ""
    objectType = "Service"
    objectsList = []
    
    hpas = [i.spec.scale_target_ref.name for i in namespaced_resources.hpas]

    for deployment in namespaced_resources.deployments:
        if deployment.metadata.name not in hpas:
            objectsList.append(deployment)

    if objectsList:
        status = False
        message = "Deploy horizontal pod autoscaler for deployments"
    else:
        status = True
        message = "horizontal pod autoscaler for deployments is deployed"
    
    return (status, message, objectsList, objectType)

def schedule_replicas_across_nodes(namespaced_resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Service"
    objectsList = []

    for deployment in namespaced_resources.deployments:
        spread = deployment.spec.template.spec.topology_spread_constraints
        if not spread:
            objectsList.append(deployment)
        else:
            topology_keys = set([i.topology_key for i in spread])
            if not set(["topology.kubernetes.io/zone"]).issubset(
                topology_keys
            ):
                objectsList.append(deployment)

    if objectsList:
        status = False
        message = "Spread replicas across AZs and Nodes"
    else:
        status = True
        message = " replicas Spread across AZs and Nodes"
    
    return (status, message, objectsList, objectType)


def run_multiple_replicas(namespaced_resources: NamespacedResources):
    
    status = None
    message = ""
    objectsList = []
    objectType = "Deployment"
    
    for deployment in namespaced_resources.deployments:
        if deployment.spec.replicas < 2:
            objectsList.append(deployment)

    if objectsList:
        status = False
        message = "Avoid running single replica deployments"
    else:
        status = True
        message = "There are no single replica deployments"
    
    return (status, message, objectsList, objectType)


def avoid_running_singleton_pods(namespaced_resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Pod"
    objectsList = []
    
    for pod in namespaced_resources.pods:
        owner = pod.metadata.owner_references
        if not owner:
            objectsList.append(pod)

    if objectsList:
        status = False
        message = "Avoid running pods without deployments."
    else:
        status = True
        message = "There no singleton pods"
    
    return (status, message, objectsList, objectType)



def check_readiness_probes(namespaced_resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Pod"
    objectsList = []

    for pod in namespaced_resources.pods:
        for container in pod.spec.containers:
            if not container.readiness_probe:
                objectsList.append(pod)

    if objectsList:
        status = False
        message = "Define readiness probes for pods."
    else:
        status = True
        message = "readiness probes exists for pods."
    
    return (status, message, objectsList, objectType)
    
    

def check_liveness_probes(namespaced_resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Pod"
    objectsList = []
    

    for pod in namespaced_resources.pods:
        for container in pod.spec.containers:
            if not container.liveness_probe:
                objectsList.append(pod)

    if objectsList:
        status = False
        message = "Define liveness probes for pods."
    else:
        status = True
        message = "liveness probes for exists for pods."
    
    return (status, message, objectsList, objectType)