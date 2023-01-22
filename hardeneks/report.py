from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich import print


colorMap = {
      True: "green", 
      False: "red",
      None: "yellow"
}

statusMap = {
      True: "PASS", 
      False: "FAIL",
      None: "NA"
}


ruledocsLinkMap = {
    
#toplevel links
    "aws-eks-best-practices": "https://aws.github.io/aws-eks-best-practices/" ,   
    "cluster-autoscaling": "https://aws.github.io/aws-eks-best-practices/karpenter/",
    "networking": "https://aws.github.io/aws-eks-best-practices/networking/index/",
    "security" : "https://aws.github.io/aws-eks-best-practices/security/docs/",
    "reliability" : "https://aws.github.io/aws-eks-best-practices/reliability/docs/",


# Cluster Autoscaling 
    
    "check_any_cluster_autoscaler_exists": "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/",
    "ensure_cluster_autoscaler_and_cluster_versions_match": "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/",
    "ensure_cluster_autoscaler_has_autodiscovery_mode": "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/",
    "ensure_cluster_autoscaler_has_three_replicas": "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/",
    "use_separate_iam_role_for_cluster_autoscaler": "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#employ-least-privileged-access-to-the-iam-role",
    "employ_least_privileged_access_to_the_IAM_role": "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#employ-least-privileged-access-to-the-iam-role",
    "use_managed_nodegroups": "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/",
    "ensure_uniform_instance_types_in_nodegroups":   "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/",
    
# Networking 
    
    "consider_public_and_private_mode": "https://aws.github.io/aws-eks-best-practices/networking/subnets/#consider-public-and-private-mode-for-cluster-endpoint",
    "deploy_vpc_cni_managed_add_on": "https://aws.github.io/aws-eks-best-practices/networking/vpc-cni/#deploy-vpc-cni-managed-add-on",
    "use_separate_iam_role_for_cni": "https://aws.github.io/aws-eks-best-practices/networking/vpc-cni/#use-separate-iam-role-for-cni",
    "monitor_IP_adress_inventory": "https://aws.github.io/aws-eks-best-practices/networking/vpc-cni/#monitor-ip-address-inventory",
    "use_dedicated_and_small_subnets_for_cluster_creation": "https://docs.aws.amazon.com/eks/latest/userguide/network_reqs.html",
    "use_prefix_mode" : "https://aws.github.io/aws-eks-best-practices/networking/prefix-mode/#use-prefix-mode-when",
    "use_aws_lb_controller" : "https://aws.github.io/aws-eks-best-practices/networking/loadbalancing/loadbalancing/",
    "use_IP_target_type_service_load_balancers" : "https://aws.github.io/aws-eks-best-practices/networking/loadbalancing/loadbalancing/#use-ip-target-type-load-balancers",
    "use_IP_target_type_ingress_load_balancers" : "https://aws.github.io/aws-eks-best-practices/networking/loadbalancing/loadbalancing/#use-ip-target-type-load-balancers",
    "utilize_pod_readiness_gates": "https://aws.github.io/aws-eks-best-practices/networking/loadbalancing/loadbalancing/#utilize-pod-readiness-gates",
    "ensure_pods_deregister_from_LB_before_termination" : "https://aws.github.io/aws-eks-best-practices/networking/loadbalancing/loadbalancing/#ensure-pods-are-deregistered-from-load-balancers-before-termination",
    "configure_pod_disruption_budget" : "https://aws.github.io/aws-eks-best-practices/networking/loadbalancing/loadbalancing/#configure-a-pod-disruption-budget",
    

# reliability
    # reliability - cluster level
    "check_metrics_server_is_running" :  "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#run-kubernetes-metrics-server",
    "check_vertical_pod_autoscaler_exists" : "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#vertical-pod-autoscaler-vpa",

    # reliability - namespace level    
    "check_horizontal_pod_autoscaling_exists" : "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#horizontal-pod-autoscaler-hpa",
    "schedule_replicas_across_nodes" : "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#schedule-replicas-across-nodes",
    "run_multiple_replicas" : "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#run-multiple-replicas",
    "avoid_running_singleton_pods" : "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#avoid-running-singleton-pods",
    "check_readiness_probes" : "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#use-readiness-probe-to-detect-partial-unavailability",
    "check_liveness_probes" : "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#use-liveness-probe-to-remove-unhealthy-pods",
    
    
# security 
    
    #iam - cluster level
    
    "disable_anonymous_access_for_cluster_roles" : "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#review-and-revoke-unnecessary-anonymous-access",
    "check_endpoint_public_access" : "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#make-the-eks-cluster-endpoint-private",
    "check_aws_node_daemonset_service_account" : "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#update-the-aws-node-daemonset-to-use-irsa",
    "check_access_to_instance_profile" : "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#when-your-application-needs-access-to-imds-use-imdsv2-and-increase-the-hop-limit-on-ec2-instances-to-2",
    "restrict_wildcard_for_cluster_roles" : "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#employ-least-privileged-access-when-creating-rolebindings-and-clusterrolebindings",
    
    #iam - namespace level
    "disable_anonymous_access_for_roles" : "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#review-and-revoke-unnecessary-anonymous-access",
    "restrict_wildcard_for_roles" : "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#employ-least-privileged-access-when-creating-rolebindings-and-clusterrolebindings" ,
    "disable_service_account_token_mounts" : "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#disable-auto-mounting-of-service-account-tokens",
    "disable_run_as_root_user": "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#run-the-application-as-a-non-root-user",
    "use_dedicated_service_accounts_for_each_deployment" : "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#use-dedicated-service-accounts-for-each-application",
    "use_dedicated_service_accounts_for_each_stateful_set" : "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#use-dedicated-service-accounts-for-each-application",
    "use_dedicated_service_accounts_for_each_daemon_set" : "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#use-dedicated-service-accounts-for-each-application",
    
    
    # multi_tenancy
    
    "ensure_namespace_quotas_exist" : "https://aws.github.io/aws-eks-best-practices/security/docs/multitenancy/#namespaces",
    
    # detective_controls
    "check_logs_are_enabled" : "https://aws.github.io/aws-eks-best-practices/security/docs/detective/#enable-audit-logs",
    
    # network_security - cluster level
    
    "check_vpc_flow_logs" : "https://aws.github.io/aws-eks-best-practices/security/docs/network/#log-network-traffic-metadata",
    "check_awspca_exists" : "https://aws.github.io/aws-eks-best-practices/security/docs/network/#acm-private-ca-with-cert-manager",
    "check_default_deny_policy_exists" : "https://aws.github.io/aws-eks-best-practices/security/docs/network/#create-a-default-deny-policy",
    
    # network_security - namespace level
    
    "use_encryption_with_aws_load_balancers" : "https://aws.github.io/aws-eks-best-practices/security/docs/network/#use-encryption-with-aws-load-balancers" ,
    
    # encryption_secrets - cluster level
    
    "use_encryption_with_ebs" : "https://aws.github.io/aws-eks-best-practices/security/docs/data/#encryption-at-rest",
    "use_encryption_with_efs" : "https://aws.github.io/aws-eks-best-practices/security/docs/data/#encryption-at-rest",
    "use_efs_access_points" : "https://aws.github.io/aws-eks-best-practices/security/docs/data/#use-efs-access-points-to-simplify-access-to-shared-datasets",
    
    # encryption_secrets - cluster level

    "disallow_secrets_from_env_vars" : "https://aws.github.io/aws-eks-best-practices/security/docs/data/#use-volume-mounts-instead-of-environment-variables",
    
    
    # infrastructure_security
    
    "deploy_workers_onto_private_subnets" : "https://aws.github.io/aws-eks-best-practices/security/docs/hosts/#deploy-workers-onto-private-subnets" ,
    "make_sure_inspector_is_enabled" : "https://aws.github.io/aws-eks-best-practices/security/docs/hosts/#run-amazon-inspector-to-assess-hosts-for-exposure-vulnerabilities-and-deviations-from-best-practices",
    
    # pod_security - cluster level
    
    "ensure_namespace_psa_exist" : "https://aws.github.io/aws-eks-best-practices/security/docs/pods/#pod-security-standards-pss-and-pod-security-admission-psa",

    # pod_security - namespace level
    
    "disallow_container_socket_mount" : "https://aws.github.io/aws-eks-best-practices/security/docs/pods/#never-run-docker-in-docker-or-mount-the-socket-in-the-container",
    "disallow_host_path_or_make_it_read_only" : "https://aws.github.io/aws-eks-best-practices/security/docs/pods/#restrict-the-use-of-hostpath-or-if-hostpath-is-necessary-restrict-which-prefixes-can-be-used-and-configure-the-volume-as-read-only" ,
    "set_requests_limits_for_containers" : "https://aws.github.io/aws-eks-best-practices/security/docs/pods/#set-requests-and-limits-for-each-container-to-avoid-resource-contention-and-dos-attacks" ,
    "disallow_privilege_escalation" : "https://aws.github.io/aws-eks-best-practices/security/docs/pods/#do-not-allow-privileged-escalation",
    "check_read_only_root_file_system" : "https://aws.github.io/aws-eks-best-practices/security/docs/pods/#configure-your-images-with-read-only-root-file-system",
    

    # image_security
    
    "use_immutable_tags_with_ecr" : "https://aws.github.io/aws-eks-best-practices/security/docs/image/#use-immutable-tags-with-ecr",
    
    # runtime_security - namespace level
    "disallow_linux_capabilities" : "https://aws.github.io/aws-eks-best-practices/security/docs/runtime/#consider-adddropping-linux-capabilities-before-writing-seccomp-policies"
    
}


console = Console()

def print_console_message(ret, rule, message, objectsList, kind):    
    
    color = colorMap[ret]
    colorStr = "[" + color + "]"
    ruleStr = "Rule: " + rule
    titleMessage = colorStr + ruleStr
    
    docs_link = ruledocsLinkMap[rule]
    docs_url = "[link=" + docs_link + "]Click to see the guide[/link]"

        
    if objectsList and kind:
        table = Table()
        if kind == "IP":
            table.add_column("SubnetId", style="cyan")
            table.add_column("CidrBlock", style="magenta")
            table.add_column("AvailableIpAddressCount", style="green")  
            totalAvailableIpAddressCount = 0
            for objectData in objectsList:
                table.add_row(objectData['SubnetId'], objectData['CidrBlock'], str(objectData['AvailableIpAddressCount']))
                totalAvailableIpAddressCount += objectData['AvailableIpAddressCount']
            table.add_row("", "[green]totalAvailableIpAddressCount", str(totalAvailableIpAddressCount))    
        elif kind == "instanceMetadata":
            table.add_column("InstanceId", style="cyan")
            table.add_column("HttpPutResponseHopLimit", style="magenta")
        
            for instance in objectsList:
                table.add_row(
                    instance["Instances"][0]["InstanceId"],
                    str(
                        instance["Instances"][0]["MetadataOptions"][
                            "HttpPutResponseHopLimit"
                        ]
                    ),
                )
            print(Panel(table, title=titleMessage, subtitle=docs_url))
        elif kind == "PublicInstances":
            table.add_column("InstanceId", style="cyan")
            table.add_column("PublicDnsName", style="magenta")
        
            for instance in objectsList:
                table.add_row(
                    instance["Instances"][0]["InstanceId"],
                    str(instance["Instances"][0]["PublicDnsName"]),
                )
            print(Panel(table, title=titleMessage, subtitle=docs_url)) 
            
        elif kind == "CIDR":
            table.add_column("SubnetId", style="cyan")
            table.add_column("CidrBlock", style="magenta")
            for objectData in objectsList:
                table.add_row(objectData['SubnetId'], objectData['CidrBlock'])
                
            print(Panel(table, title=titleMessage, subtitle=docs_url))
        elif kind == "Repository":
            table.add_column("Repository", style="cyan")
            table.add_column("imageTagMutability", style="magenta")
            
            for objectData in objectsList:
                table.add_row(objectData['repositoryName'], objectData['imageTagMutability'])
                
            print(Panel(table, title=titleMessage, subtitle=docs_url)) 
        elif kind == "PersistentVolume" or kind == "StorageClass" :

            table.add_column("PersistentVolume", style="cyan")
            table.add_column("Encrypted", style="magenta")
    
            for objectData in objectsList:
                table.add_row(objectData.metadata.name, "false")
            
            print(Panel(table, title=titleMessage, subtitle=docs_url))                
            
        elif kind in ["Namespace", "ClusterRole", "ClusterRoleBinding", "RoleBinding"] :
            table.add_column(kind, style="cyan")
            for objectData in objectsList:
                table.add_row(objectData)
            
            print(Panel(table, title=titleMessage, subtitle=docs_url))
        elif kind == "Report":
            totalNumOfRules = len(objectsList[rule])
            table.add_column("S.No", style="cyan")
            table.add_column("Rule", style="magenta")
            table.add_column("Status", style="green")
            table.add_column("Message", style="yellow")
        
            for i, objectData in enumerate( objectsList[rule]):
                color = colorMap[objectData['ret']]
                colorStr = "[" + color + "]"
                table.add_row(colorStr+str(i+1)+"/"+str(totalNumOfRules), colorStr+objectData['rule'], colorStr+statusMap[objectData['ret']], colorStr+objectData['message'] ) 
        
            if message is None:
                titleMessage = colorStr + "Hardeneks Report for Cluster for Pillar: {}".format(rule)
            else:
                titleMessage = colorStr + "Hardeneks Report for Namespace : {} for Pillar: {}".format(message, rule)
                    
            print(Panel(renderable=table, title=titleMessage, subtitle=docs_url))
        elif kind == "ClusterData":
            totalNumOfRules = len(objectsList)
            table.add_column("S.No", style="cyan")
            table.add_column("Description", style="magenta")
            table.add_column("Details", style="green")
            table.add_column("Comments", style="yellow")
            
            for i, objectData in enumerate( objectsList):
                color = objectData[0]
                colorStr = "[" + color + "]"
                table.add_row(colorStr+str(i+1)+"/"+str(totalNumOfRules), colorStr+objectData[1], colorStr+objectData[2], colorStr+objectData[3] ) 
        
            titleMessage = colorStr + "EKS Cluster Details"
            print(Panel(renderable=table, title=titleMessage, subtitle=docs_url))
                        
        else:
            table.add_column("Kind", style="cyan")
            table.add_column("Namespace", style="magenta")
            table.add_column("Name", style="green")        
            for objectData in objectsList:
                table.add_row(kind, objectData.metadata.namespace, objectData.metadata.name)

            print(Panel(renderable=table, title=titleMessage, subtitle=docs_url))
    else:
        descriptionMessage = colorStr + message
        print(Panel(renderable=descriptionMessage, title=titleMessage, subtitle=docs_url))
        
    console.print()

