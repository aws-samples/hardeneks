from collections import Counter
import sys

import boto3
from kubernetes import client
from rich import print

from rich.console import Console

from ...resources import NamespacedResources
from ...report import (
    print_console_message,
)


console = Console()



def use_IP_target_type_service_load_balancers(namespaced_resources: NamespacedResources,):
    
    status = None
    objectsList = None
    objectType = None
    succes_message = "Target Group Mode IP configured for services :"
    error_message = "Target Group Mode IP is NOT configured for services :"
    objectsList = []
    
    for service in namespaced_resources.services:
        
        serviceName = service.metadata.name
        serviceType = service.spec.type
        
        if serviceType == "LoadBalancer":
            annotations = service.metadata.annotations
            #print("service name={} type={} annotations={}".format(serviceName, serviceType, annotations))
            
            if annotations:
            
                target_group_mode_exists = (
                    "service.beta.kubernetes.io/aws-load-balancer-nlb-target-type"
                    in annotations
                )
                target_group_mode_type = annotations.get(
                    "service.beta.kubernetes.io/aws-load-balancer-nlb-target-type"
                )
                #print("target_group_mode_exists={} target_group_mode_type={}".format(target_group_mode_exists, target_group_mode_type))
                
                if target_group_mode_exists and target_group_mode_type == "ip":
                    succes_message += serviceName + " "
                    status = True
                else:
                    status = False
                    error_message += serviceName + " "
                    objectsList.append(service)
            else:
                status = False
                error_message += serviceName + " "
                objectsList.append(service)                
            
                    
    if status == True:
        message = succes_message
    elif status == False:
        message = error_message
    else:
        message = "Note this Rule is NOT applicable since there are no Loadbalamcer types"
        
    return (status, message, objectsList, "Service")


def use_IP_target_type_ingress_load_balancers(namespaced_resources: NamespacedResources,):
    
    status = None
    objectsList = None
    objectType = None
    succes_message = "Target Group Mode IP configured for ingresses :"
    error_message = "Target Group Mode IP is NOT configured for ingresses :"
    objectsList = []
    
    ingressList = client.NetworkingV1Api().list_namespaced_ingress(namespaced_resources.namespace).items
    
    #print("ingressList={}".format(ingressList))
    
    
    for ingress in ingressList:
        
        ingressName = ingress.metadata.name
        annotations = ingress.metadata.annotations
        
        if annotations:
            
            target_group_mode_exists = (
                "alb.ingress.kubernetes.io/target-type"
                in annotations
            )

            if target_group_mode_exists:
                
                target_group_mode_type = annotations.get(
                    "alb.ingress.kubernetes.io/target-type"
                )
                
                if target_group_mode_type == "ip":
                    status = True
                    succes_message += ingressName + " "
                else:
                    status = False
                    error_message += ingressName + " "
                    objectsList.append(ingress)
            else:
                status = False
                error_message += ingressName + " "
                objectsList.append(ingress)
        else:
            status = False
            error_message += ingressName + " "
            objectsList.append(ingress)                
            
                    
    if status == True:
        message = succes_message
    elif status == False:
        message = error_message
    else:
        message = "Note this Rule is NOT applicable since there are no Loadbalancer Services"
        
    return (status, message, objectsList, "Ingress")

def utilize_pod_readiness_gates(namespaced_resources: NamespacedResources,):
    
    status = None
    objectsList = None
    objectType = None
    succes_message = "Target Group Mode IP configured for services :"
    error_message = "Target Group Mode IP is NOT configured for services :"
    serviceNames = ''
    ingressNames = ''
    objectsList = []
    serviceNameList = []
    serviceObjOffendersList = []
    ingressObjOffendersList = []
    ingressNameList = []
    ingressObjNameList = []
    
    for service in namespaced_resources.services:
        
        serviceName = service.metadata.name
        serviceType = service.spec.type
        
        isServiceCompliant = False
        if serviceType == "LoadBalancer":
            annotations = service.metadata.annotations
            #print("service name={} type={} annotations={}".format(serviceName, serviceType, annotations))
            if annotations:
                target_group_mode_exists = (
                    "service.beta.kubernetes.io/aws-load-balancer-nlb-target-type"
                    in annotations
                )
                #print("target_group_mode_exists={} target_group_mode_type={}".format(target_group_mode_exists, target_group_mode_type))
                if target_group_mode_exists:
                    target_group_mode_type = annotations.get(
                        "service.beta.kubernetes.io/aws-load-balancer-nlb-target-type"
                    )                    
                    if target_group_mode_type == "ip":
                        isServiceCompliant = True
                        
                        
            
    
        if isServiceCompliant:
            serviceNameList.append(serviceName)
        else:    
            serviceObjOffendersList.append(service)
    
    
    ingressList = client.NetworkingV1Api().list_namespaced_ingress(namespaced_resources.namespace).items
    
    #print("ingressList={}".format(ingressList))
    
    for ingress in ingressList:
        
        isIngressCompliant = False
        
        ingressName = ingress.metadata.name
        annotations = ingress.metadata.annotations
        
        if annotations:
            target_group_mode_exists = (
                "alb.ingress.kubernetes.io/target-type"
                in annotations
            )
            if target_group_mode_exists:
                
                target_group_mode_type = annotations.get(
                    "alb.ingress.kubernetes.io/target-type"
                )
                if target_group_mode_type == "ip":
                    isIngressCompliant = True
                
            
        if isIngressCompliant:
            ingressNameList.append(ingressName)
        else:
            ingressObjOffendersList.append(ingress)
            
                    
    if len(serviceNameList) >=1 or len(ingressNameList) >=1:
        ns = client.CoreV1Api().read_namespace(name=namespaced_resources.namespace)
        #print("ns={}".format(ns))
        labels = ns.metadata.labels
        #print("labels={}".format(labels))
        if labels:
            if 'elbv2.k8s.aws/pod-readiness-gate-inject' in labels.keys():
                readinessgatesstatus = labels['elbv2.k8s.aws/pod-readiness-gate-inject']
                
                if readinessgatesstatus ==  'enabled':
                    status =  True
                else:
                    status = False
                    objectsList.extend(serviceObjOffendersList)
                    objectsList.extend(ingressObjOffendersList)
            else:
                status = False
                
    
    if len(serviceNameList) >=1:
        serviceNames = "Service List: " + ' '.join(serviceNameList)
        

    if len(ingressNameList) >=1:
        ingressNames = "Ingress List: " + ' '.join(ingressNameList)
        
        
    message = serviceNames + "  " + ingressNames
        

    if status is None:
        message = "Note this Rule is NOT applicable since there are no Loadbalaccer Services or Ingress"
        
    return (status, message, objectsList, "Service")



def ensure_pods_deregister_from_LB_before_termination(namespaced_resources: NamespacedResources,):
    
    status = None
    objectsList = None
    objectType = None
    succes_message = "Target Group Mode IP configured for services :"
    error_message = "Target Group Mode IP is NOT configured for services :"
    complianceServiceNames = ''
    nonComplianceServiceNames = ''
    complianceServiceNamesList = []
    nonComplianceServiceNamesList = []
    nonComplianceServiceObjList = []
    objectsList = []
    serviceObjList = []
    ingressObjList = []
    
    for service in namespaced_resources.services:
        
        serviceName = service.metadata.name
        serviceType = service.spec.type
        
        if serviceType == "LoadBalancer":
            annotations = service.metadata.annotations
            #print("service name={} type={} annotations={}".format(serviceName, serviceType, annotations))
            if annotations:
                target_group_mode_exists = (
                    "service.beta.kubernetes.io/aws-load-balancer-nlb-target-type"
                    in annotations
                )
                #print("target_group_mode_exists={} target_group_mode_type={}".format(target_group_mode_exists, target_group_mode_type))
                if target_group_mode_exists:
                    target_group_mode_type = annotations.get(
                        "service.beta.kubernetes.io/aws-load-balancer-nlb-target-type"
                    )                    
                    if target_group_mode_type == "ip":
                        serviceObjList.append(service)
            
    
    
    
    ingressList = client.NetworkingV1Api().list_namespaced_ingress(namespaced_resources.namespace).items
    
    #print("ingressList={}".format(ingressList))
    
    for ingress in ingressList:
        
        ingressName = ingress.metadata.name
        annotations = ingress.metadata.annotations
        
        if annotations:
            target_group_mode_exists = (
                "alb.ingress.kubernetes.io/target-type"
                in annotations
            )
            if target_group_mode_exists:
                
                target_group_mode_type = annotations.get(
                    "alb.ingress.kubernetes.io/target-type"
                )
                if target_group_mode_type == "ip":
                    #ingressObjList.append(ingress)
                    rules = ingress.spec.rules
                    #print("ingressName={} rules={}".format(ingressName, rules))
                    for rule in rules:
                        paths = rule.http.paths
                        #print("paths={}".format(paths))
                        for path in paths:
                            serviceName = path.backend.service.name
                            #print("serviceName={}".format(serviceName))
                            serviceObj = client.CoreV1Api().read_namespaced_service(name=serviceName,  namespace=namespaced_resources.namespace)
                            serviceObjList.append(serviceObj)
                            #print("serviceObj={}".format(serviceObj))
                    
            
            
                
    #print("serviceObjList={}".format(serviceObjList))
    
    for service in serviceObjList:
        
        is_sleep_command_exists = False
        serviceName = service.metadata.name
        serviceSelector = service.spec.selector
        #serviceSelector = {'app1': 'nginx1', 'k1':'v1', 'k2' : 'v2'}
        numberOfLabels = len (serviceSelector)
        i=0
        serviceSelectorStr=''
        for k,v in serviceSelector.items():
            #print("k={} v={}".format(k,v))
            serviceSelectorStr += k +'=' + v
            i += 1
            if i < numberOfLabels:
                serviceSelectorStr += ','
                
        #print("serviceName={} serviceSelector={} serviceSelectorStr={}".format(serviceName, serviceSelector, serviceSelectorStr))
        pods = client.CoreV1Api().list_namespaced_pod(namespace=namespaced_resources.namespace, label_selector=serviceSelectorStr).items
        #print("pods={}".format(pods))
        #for pod in pods:
        if len(pods) >= 1:
            podName = pods[0].metadata.name
            containers = pods[0].spec.containers
            image = containers[0].image
            lifecycle = containers[0].lifecycle
            #print("podName={} image={} lifecycle={}".format(podName, image, lifecycle))
            if lifecycle:
                commandList = lifecycle.pre_stop._exec.command
                #print("commandList={}".format(commandList))
                
                for command in commandList:
                    if 'sleep' in command:
                        is_sleep_command_exists = True
                        #print("sleep command={}".format(command))
            
        if is_sleep_command_exists:
            complianceServiceNamesList.append(serviceName)
        else:
            objectsList.append(service)
            nonComplianceServiceNamesList.append(serviceName)
            
    
    #print("complianceServiceNamesList={} nonComplianceServiceNamesList={}".format(complianceServiceNamesList, nonComplianceServiceNamesList))
            
    if len(complianceServiceNamesList) >=1:
        complianceServiceNames = "Compliance Service List: " + ' '.join(complianceServiceNamesList)
        #objectsList.extend(complianceServiceNamesList)

    if len(nonComplianceServiceNamesList) >=1:
        nonComplianceServiceNames = "Non Compliance Service List: " + ' '.join(nonComplianceServiceNamesList)
        #objectsList.extend(nonComplianceServiceNamesList)


    #for ingressObj in                
    #print("ingressObjList={}".format(ingressObjList))
    
    if len(complianceServiceNamesList) >=1 or len(nonComplianceServiceNamesList) >=1:
        
        if len(nonComplianceServiceNamesList) == 0:
            status = True
            message = complianceServiceNames
        else:
            status = False
            message = complianceServiceNames + ' ' + nonComplianceServiceNames


    if status is None:
        message = "Note this Rule is NOT applicable since there are no Loadbalaccer Services or Ingress"
        
    return (status, message, objectsList, "Service")


def configure_pod_disruption_budget(namespaced_resources: NamespacedResources,):
    
    status = None
    objectsList = None
    objectType = None
    message = ''
    succes_message = "Target Group Mode IP configured for services :"
    error_message = "Target Group Mode IP is NOT configured for services :"
    objectsList = []
    deployNamesWithPDB =''
    deploymentsWithPDB =[]
    deployNamesWithoutPDB = ''
    deploymentsWithoutPDB =[]
    
    
    print("namespace={}".format(namespaced_resources.namespace))
    print("deployments={}".format(namespaced_resources.deployments))
    
    pdsList = client.PolicyV1Api().list_namespaced_pod_disruption_budget(namespace=namespaced_resources.namespace).items

    #print("pdsList={}".format(pdsList))
    #print("deployments={}".format(namespaced_resources.deployments))
    
    for deployment in namespaced_resources.deployments:
        deploymentName = deployment.metadata.name
        deployLabels =  deployment.spec.selector.match_labels
        #print("deploymentName={} deployLabels={}".format(deploymentName, deployLabels))
        
        isPDBExists = False
        for pdb in pdsList:
            
            pdbName = pdb.metadata.name
            pdbLabels = pdb.spec.selector.match_labels
            #print("pdbName={} pdbLabels={}".format(pdbName, pdbLabels))
            isPDBExists = all((deployLabels.get(k) == v for k, v in pdbLabels.items()))
            #print("deploymentName={} pdbName={} res={}".format(deploymentName, pdbName, isPDBExists))
        
        if isPDBExists:
            deploymentsWithPDB.append(deploymentName)
        else:
            deploymentsWithoutPDB.append(deploymentName)
            objectsList.append(deployment)

            
    if len(deploymentsWithPDB) >=1:
        deployNamesWithPDB = "Deployments with PDB: " + ' '.join(deploymentsWithPDB)
        #objectsList.extend(deploymentsWithPDB)

    if len(deploymentsWithoutPDB) >=1:
        deployNamesWithoutPDB = "Deployments without PDB: " + ' '.join(deploymentsWithoutPDB)       
        #objectsList.extend(deploymentsWithoutPDB)

    
    if len(deploymentsWithPDB) >=1 or len(deploymentsWithoutPDB) >=1:
        
        if len(deploymentsWithoutPDB) == 0:
            status = True
            message = deployNamesWithPDB
        else:
            status = False
            message = deployNamesWithPDB + ' ' + deployNamesWithoutPDB

    if status is None:
        message = "Note this Rule is NOT applicable since there are no deployments in this namespace"
        
    return (status, message, objectsList, "Deployment")

