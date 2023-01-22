from ...resources import NamespacedResources

def disallow_secrets_from_env_vars(resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Pod"
    objectsList = []
    
    for pod in resources.pods:
        for container in pod.spec.containers:
            if container.env:
                for env in container.env:
                    if env.value_from and env.value_from.secret_key_ref:
                        objectsList.append(pod)
            if container.env_from:
                for env_from in container.env_from:
                    if env_from.secret_ref:
                        objectsList.append(pod)

    if objectsList:
        status = False
        message = "Disallow secrets from env vars"
    else:
        status = True
        message = "secrets are not allowed env vars"
    
    return (status, message, objectsList, objectType)

