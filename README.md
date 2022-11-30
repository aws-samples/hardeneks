# Hardeneks

#### This is not an officially supported AWS product.

[![PyPI version](https://badge.fury.io/py/hardeneks.svg)](https://badge.fury.io/py/hardeneks)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/hardeneks.svg)](https://pypi.python.org/pypi/hardeneks/)
[![Python package](https://github.com/dorukozturk/hardeneks/actions/workflows/ci.yaml/badge.svg)](https://github.com/dorukozturk/hardeneks/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/dorukozturk/hardeneks/branch/main/graph/badge.svg?token=jrB7uWUHdr)](https://codecov.io/gh/dorukozturk/hardeneks)


Runs checks to see if an EKS cluster follows [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/).

**Quick Start**:

```
python3 -m venv /tmp/.venv
source /tmp/.venv/bin/activate
pip install hardeneks
hardeneks --context <K8S_CONTEXT> --cluster <CLUSTER_NAME> --region <AWS_REGION>
```

![alt text](https://github.com/dorukozturk/hardeneks/blob/e9168a857a57a13cee8fae870e33d585d8bd3be1/docs/hardeneks.png)

- <b><K8S_CONTEXT><b> 
  
    You can get the contexts by running:
    ```
    kubectl config get-contexts
    ```
    or get the current context by running:
    ```
    kubectl config current-context
    ```

- <b><CLUSTER_NAME><b>
  
    You can get the cluster names by running:
    ```
    aws eks list-clusters --region us-east-1
    ```
  
**Configuration File**:

Default behavior is to run all the checks. If you want to provide your own config file to specify list of rules to run, you can use the --config flag.You can also add namespaces to be skipped. 

Following is a sample config file:

```yaml
---
ignore-namespaces:
  - kube-node-lease
  - kube-public
  - kube-system
  - kube-apiserver
rules: 
  cluster_wide:
    security:
      iam:
        - disable_anonymous_access_for_cluster_roles
        - check_endpoint_public_access
        - check_aws_node_daemonset_service_account
        - check_access_to_instance_profile
        - restrict_wildcard_for_cluster_roles
      multi_tenancy:
        - ensure_namespace_quotas_exist
      detective_controls:
        - check_logs_are_enabled
      network_security:
        - check_vpc_flow_logs
        - check_awspca_exists
        - check_default_deny_policy_exists
      encryption_secrets:
        - use_encryption_with_ebs
        - use_encryption_with_efs
        - use_efs_access_points
      infrastructure_security:
        - deploy_workers_onto_private_subnets
        - make_sure_inspector_is_enabled
      pod_security:
        - ensure_namespace_psa_exist
      image_security:
        - use_immutable_tags_with_ecr
    reliability:
      applications:
        - check_metrics_server_is_running
        - check_vertical_pod_autoscaler_exists
  namespace_based:
    security: 
      iam:
        - disable_anonymous_access_for_roles
        - restrict_wildcard_for_roles
        - disable_service_account_token_mounts
        - disable_run_as_root_user
        - use_dedicated_service_accounts_for_each_deployment
        - use_dedicated_service_accounts_for_each_stateful_set
        - use_dedicated_service_accounts_for_each_daemon_set
      pod_security:
        - disallow_container_socket_mount
        - disallow_host_path_or_make_it_read_only
        - set_requests_limits_for_containers
        - disallow_privilege_escalation
        - check_read_only_root_file_system
      network_security:
        - use_encryption_with_aws_load_balancers
      encryption_secrets:
        - disallow_secrets_from_env_vars    
      runtime_security:
        - disallow_linux_capabilities
    reliability:
      applications:
        - check_horizontal_pod_autoscaling_exists
        - schedule_replicas_across_nodes
        - run_multiple_replicas
        - avoid_running_singleton_pods
```
  

## For Developers

**Prerequisites**:

* This cli uses poetry. Follow instructions that are outlined [here](https://python-poetry.org/docs/) to install poetry.


**Installation**:

```console
git clone git@github.com:dorukozturk/hardeneks.git
cd hardeneks
poetry install
```

**Running Tests**:

```console
poetry shell
pytest --cov=hardeneks tests/ --cov-report term-missing
```
