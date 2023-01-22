import boto3
from kubernetes import client
from rich import print
import sys


from ...resources import Resources
from ...report import  print_console_message

def deploy_vpc_cni_managed_add_on(resources: Resources):
    status = True
    objectsList = None
    objectType = None
    message = None
    
    func_name = sys._getframe().f_code.co_name
    docs_link = "https://aws.github.io/aws-eks-best-practices/networking/vpc-cni/#deploy-vpc-cni-managed-add-on"
    client = boto3.client("eks", region_name=resources.region)
    try:
        vpccni_add_on = client.describe_addon(clusterName=resources.cluster, addonName='vpc-cni')
        message = "VPC CNI is a Managed Add-On"
        #pprint("vpccni_add_on={}".format(vpccni_add_on))
    except Exception as exc:
        #print(f"[bold][red]{exc}")
        message = "VPC CNI is Not a Managed Add-On"
        status = False

    return (status, message, objectsList, objectType)


def use_separate_iam_role_for_cni(resources: Resources):

    status = True
    objectsList = None
    objectType = None
    message = None
    
    daemonset = client.AppsV1Api().read_namespaced_daemon_set(name="aws-node", namespace="kube-system")
    sa = daemonset.spec.template.spec.service_account_name
    sa_data = client.CoreV1Api().read_namespaced_service_account(sa, 'kube-system', pretty="true")
    #print(sa_data.metadata.annotations.keys())
    
    if 'eks.amazonaws.com/role-arn' in sa_data.metadata.annotations.keys():
        message = "aws-node daemonset uses a dedicated IAM Role (IRSA)"
    else:
        message = "aws-node daemonset does not use a dedicated IAM Role (IRSA)"
        status = False
    return (status, message, objectsList, objectType)
    
    

def monitor_IP_adress_inventory(resources: Resources):
    status = True
    objectsList = None
    objectType = None
    message = None
    
    eksclient = boto3.client("eks", region_name=resources.region)
    cluster_metadata = eksclient.describe_cluster(name=resources.cluster)
    vpcId  = cluster_metadata["cluster"]["resourcesVpcConfig"]["vpcId"]
    subnetIds = cluster_metadata["cluster"]["resourcesVpcConfig"]["subnetIds"]

    #print("vpcId={} subnetIds={}".format(vpcId, subnetIds))
    
    subnets = boto3.resource("ec2").subnets.filter(
        Filters=[{"Name": "vpc-id", "Values": [vpcId]}]
    )
    subnet_ids = [sn.id for sn in subnets]
    
    #print("subnets={} subnet_ids={}".format(subnets, subnet_ids))
    ec2client = boto3.client('ec2')
    subnetsList = ec2client.describe_subnets(SubnetIds=subnet_ids)
    #print("response={} ".format(response))
    totalAvailableIpAddressCount = 0
    for subnet in subnetsList['Subnets']:
        #print("SubnetId={} CidrBlock={} AvailableIpAddressCount={}".format(subnet['SubnetId'], subnet['CidrBlock'], subnet['AvailableIpAddressCount']))
        totalAvailableIpAddressCount += subnet['AvailableIpAddressCount']
    
    #print("totalAvailableIpAddressCount={}".format(totalAvailableIpAddressCount))
    
    descriptionMessage = "Total number of Available IPs across all subnets in the VPC is {}".format(totalAvailableIpAddressCount)
    if totalAvailableIpAddressCount > 5000:
        message = descriptionMessage
    else:
        message = descriptionMessage
        status = False
        
    return (status, message, objectsList, objectType)
    
def use_dedicated_and_small_subnets_for_cluster_creation(resources: Resources):
    status = True
    objectsList = None
    objectType = None
    message = None
    
    eksclient = boto3.client("eks", region_name=resources.region)
    cluster_metadata = eksclient.describe_cluster(name=resources.cluster)
    vpcId  = cluster_metadata["cluster"]["resourcesVpcConfig"]["vpcId"]
    subnetIds = cluster_metadata["cluster"]["resourcesVpcConfig"]["subnetIds"]

    #print("vpcId={} subnetIds={}".format(vpcId, subnetIds))
    
    #print("subnets={} subnet_ids={}".format(subnets, subnet_ids))
    ec2client = boto3.client('ec2')
    subnetsList = ec2client.describe_subnets(SubnetIds=subnetIds)
    #print("response={} ".format(response))
    
    is_cluster_subnet_cidr_size_big = None
    for subnet in subnetsList['Subnets']:
        #print("SubnetId={} CidrBlock={} AvailableIpAddressCount={}".format(subnet['SubnetId'], subnet['CidrBlock'], subnet['AvailableIpAddressCount']))
        cidr_size = subnet['CidrBlock'].split('/')[-1]
        #print(cidr_size)
        if int(cidr_size) < 28:
            is_cluster_subnet_cidr_size_big = True
    
    if not is_cluster_subnet_cidr_size_big:
        message = "Cluster Subnet CIDE Size is <= /28"
    else:
        message = "Cluster Subnet CIDE Size is > /28"
        status = False
        
    return (status, message, objectsList, objectType)