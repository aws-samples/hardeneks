import boto3
from kubernetes import client
from rich import print
import sys


from ...resources import Resources
from ...report import print_console_message
from ...helper_functions import is_deployment_exists_in_namespace

def use_aws_lb_controller(resources: Resources):


    status = True
    objectsList = None
    objectType = None
    message = ""
    
    (ret, deploymentData) = is_deployment_exists_in_namespace("aws-load-balancer-controller", "kube-system")
    if ret:
        message = "AWS LB Controller is deployed in the cluster"
    else:
        message = "AWS LB Controller is not deployed in the cluster"
        status = False
        
    return (status, message, objectsList, objectType)
    
    
