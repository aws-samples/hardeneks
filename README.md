# Hardeneks

[![PyPI version](https://badge.fury.io/py/hardeneks.svg)](https://badge.fury.io/py/hardeneks)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/hardeneks.svg)](https://pypi.python.org/pypi/hardeneks/)
[![Python package](https://github.com/aws-samples/hardeneks/actions/workflows/ci.yaml/badge.svg)](https://github.com/aws-samples/hardeneks/actions/workflows/ci.yaml)
[![Downloads](https://pepy.tech/badge/hardeneks)](https://pepy.tech/project/hardeneks)


Runs checks to see if an EKS cluster follows [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/).

**Quick Start**:

```
python3.10 -m venv /tmp/.venv   # Or any other supported Python version listed above.
source /tmp/.venv/bin/activate
pip install hardeneks
hardeneks
```

![alt text](https://raw.githubusercontent.com/aws-samples/hardeneks/main/docs/hardeneks.gif)

**Usage**:

```console
hardeneks [OPTIONS]
```

**Options**:

* `--region TEXT`: AWS region of the cluster. Ex: us-east-1
* `--context TEXT`: K8s context
* `--cluster TEXT`: EKS Cluster name
* `--namespace TEXT`: Namespace to be checked (default is all namespaces)
* `--config TEXT`: Path to a hardeneks config file
* `--export-txt TEXT`: Export the report in txt format
* `--export-csv TEXT`: Export the report in csv format
* `--export-html TEXT`: Export the report in html format
* `--export-json TEXT`: Export the report in json format
* `--export-security-hub`: Export failed checks to AWS Security Hub
* `--insecure-skip-tls-verify`: Skip TLS verification
* `--width`: Width of the output (defaults to terminal size)
* `--height`: Height of the output (defaults to terminal size)
* `--help`: Show this message and exit.


- <b>K8S_CONTEXT<b> 
  
    You can get the contexts by running:
    ```
    kubectl config get-contexts
    ```
    or get the current context by running:
    ```
    kubectl config current-context
    ```

- <b>CLUSTER_NAME<b>
  
    You can get the cluster names by running:
    ```
    aws eks list-clusters --region us-east-1
    ```
  
**Configuration File**:

Default behavior is to run all the checks. If you want to provide your own config file to specify list of rules to run, you can use the --config flag.You can also add namespaces to be skipped. 

Following is a sample config file:

```yaml
ignore-namespaces:
  - kube-node-lease
  - kube-public
  - kube-system
  - kube-apiserver
  - karpenter
  - kubecost
  - external-dns
  - argocd
  - aws-for-fluent-bit
  - amazon-cloudwatch
  - vpa
masking:
  constraints:
    mask_namespace_names: false
    mask_resource_names: false
    replace_with: hash
  exclude:
    namespaces:
      - example
    regex:  # e.g. "^system:.*"
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
    cluster_autoscaling:
      cluster_autoscaler:
        - check_any_cluster_autoscaler_exists
        - ensure_cluster_autoscaler_and_cluster_versions_match
        - ensure_cluster_autoscaler_has_autodiscovery_mode
        - use_separate_iam_role_for_cluster_autoscaler
        - employ_least_privileged_access_cluster_autoscaler_role
        - use_managed_nodegroups
    scalability:
      control_plane:
        - check_eks_version
        - check_kubectl_compression
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
        - check_readiness_probes
        - check_liveness_probes
```

**Masking**:

Sensitive namespace and resource names can be masked in all output and exports
using a deterministic one-way hash (truncated SHA-256). Masking is configured
inside `rules:` so it travels with the rest of the rule config:

```yaml
masking:
  constraints:
    mask_namespace_names: false   # replace namespace names
    mask_resource_names: false    # replace resource names
    replace_with: hash            # "hash" (default) or a single character e.g. "*"
  exclude:
    namespaces:                   # these namespaces (and their resources) are never masked
      - example
    regex:                        # PCRE pattern; matching names are never masked
```

- Both constraints default to `false`; omitting the `masking` block entirely disables masking.
- `replace_with: hash` — replaces the entire name with an 8-character truncated SHA-256 hex digest. The same name always produces the same digest within a run.
- `replace_with: <char>` — partially redacts each hyphen-delimited word while preserving its shape:
  - Words of 1–2 characters are left untouched.
  - Words shorter than 6 characters: keep first and last character, mask the middle.
  - Words of 6+ characters: keep the first 3 and last character, mask the middle.
  - Generated suffixes (e.g. `7d9f4b` or `xkq2p` in Pod names) are kept as-is.
- `exclude.namespaces` is an explicit allow-list — names listed here are always shown as-is.
- `exclude.regex` is matched against both namespace names and resource names; matches are never masked.
- When `mask_namespace_names` is enabled the namespace shown in the result table and all exports is replaced.
- When `mask_resource_names` is enabled every offending resource name reported by a check is replaced. Resources that belong to an excluded namespace are not masked.

## Permissions
 
In order to run hardeneks we need to have some permissions both on AWS side and k8s side.

### Minimal IAM role policy for all checks

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "eks:ListClusters",
                "eks:DescribeCluster",
                "eks:ListPodIdentityAssociations",
                "eks:DescribePodIdentityAssociation",
                "eks:DescribeClusterVersions",
                "ecr:DescribeRepositories",
                "inspector2:BatchGetAccountStatus",
                "ec2:DescribeFlowLogs",
                "ec2:DescribeInstances",
                "iam:ListAttachedRolePolicies",
                "iam:ListRolePolicies",
                "iam:GetPolicy",
                "iam:GetPolicyVersion",
                "iam:GetRolePolicy"
            ],
            "Resource": "*"
        }
    ]
}
```

### Minimal ClusterRole for all checks

```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: hardeneks-runner
rules:
- apiGroups: [""]
  resources: ["namespaces", "resourcequotas", "persistentvolumes", "pods", "services", "nodes"]
  verbs: ["list"]
- apiGroups: [""]
  resources: ["serviceaccounts"]
  verbs: ["get"]
- apiGroups: ["rbac.authorization.k8s.io"]
  resources: ["clusterroles", "clusterrolebindings", "roles", "rolebindings"]
  verbs: ["list"]
- apiGroups: ["networking.k8s.io"]
  resources: ["networkpolicies"]
  verbs: ["list"]
- apiGroups: ["storage.k8s.io"]
  resources: ["storageclasses"]
  verbs: ["list"]
- apiGroups: ["apps"]
  resources: ["deployments", "daemonsets", "statefulsets"]
  verbs: ["list", "get"]
- apiGroups: ["autoscaling"]
  resources: ["horizontalpodautoscalers"]
  verbs: ["list"]
```

## For Developers

**Prerequisites**:

* This cli uses poetry. Follow instructions that are outlined [here](https://python-poetry.org/docs/) to install poetry.


**Installation**:

```console
git clone git@github.com:aws-samples/hardeneks.git
cd hardeneks
poetry install
```

**Running Tests**:

```console
poetry shell
pytest --cov=hardeneks tests/ --cov-report term-missing
```




