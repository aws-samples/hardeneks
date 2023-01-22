import boto3

from ...resources import Resources


def use_immutable_tags_with_ecr(resources: Resources):
    status = None
    message = ""
    objectType = "Repository"
    objectsList = []


    ecrclient = boto3.client("ecr", region_name=resources.region)
    repositories = ecrclient.describe_repositories()
    for repository in repositories["repositories"]:
        if repository["imageTagMutability"] != "IMMUTABLE":
            objectsList.append(repository)

    if objectsList:
        status = False
        message = "Make image tags immutable"
    else:
        status = True
        message = "Image tags are immutable"
    
    return (status, message, objectsList, objectType)
    
