## v1.1.0 (2026-03-23)

### Feat

- **__init__.py**: Added time in UTC that HardenEKS was run against the cluster

### Fix

- **__init__.py**: Fixed json output so it prints all namespaces

## v1.0.0 (2026-03-10)

### Fix

- **use_encryption_with_ebs**: Simplification of use_encryption_with_ebs to remove unnecessary conditional
- **applications.py**: Adding resource name to offenders rather than the entire object
- **disallow_linux_capabilities**: Avoids adding pods more than once
- **disallow_secrets_from_env_vars**: Fix to prevent pods being added more than once
- **use_encryption_with_aws_load_balancers**: Add NLB as offender when annotations are empty
- **check_read_only_root_file_system**: Break when first offending container found
- **test_disable_run_as_root_user_container**: Deleted test_disable_run_as_root_user_container files as these tests are now in test_disable_run_as_root_user
- **disallow_privilege_escalation**: Break when first container with privilege escalation found
- **set_requests_limits_for_containers**: Break when first offending pod found
- **disallow_host_path_or_make_it_read_only**: Check passes if the pod mounts the host path as read only
- **disallow_container_socket_mount**: Check for empty volumes in pod spec to prevent crash
- **use_dedicated_service_accounts_for_each_***: Corrected variable names in functions
- **disable_anonymous_access_for_roles**: Add role binding name rather than full object to offenders
- **disable_run_as_root_user**: Modified disable_run_as_root_user so it checks all pods have container security context then checks pod security context as fallback
- **disable_service_account_token_mounts**: Updated disable_service_account_token_mounts so it checks if the default service account allows auto mounting
- **restrict_wildcard_for_roles**: Handles rules which are empty
- **check_kubectl_compression**: Return cluster name for failed compression check
- **check_EKS_version**: Updated check_EKS_version so it checks if cluster in standard support
- **use_managed_nodegroups**: Appending node name rather than full node resource
- **employ_least_privileged_access_cluster_autoscaler_role**: Added checks for pod identity. Removd DescribeTags as that's no longer required as of CA 1.25. Checking that a statement is specifically for an Allow, not Deny.
- **use_separate_iam_role_for_cluster_autoscaler**: Check Cluster Autoscaler for IRSA or pod identities
- **ensure_cluster_autoscaler_has_autodiscovery_mode**: Exits after cluster-autoscaler deployment is checked
- **ensure_cluster_autoscaler_and_cluster_versions_match**: Breaking loop when CA checked. No need to continue checking the other deployments
- **check_any_cluster_autoscaler_exists**: Checking for any deployment containing cluster or karpenter as it's common to add suffixes to the deployment name
- **applications.py**: Added resource name when there is an offender, as is convention in the code base
- **check_default_deny_policy_exists**: Fixed default deny policy so it confirms namespace default deny for both ingress and egress
- **check_awspca_exists**: Exit when first "aws-privateca-issuer" found. No need to keep checking
- **make_sure_inspector_is_enabled**: Check whether inspector enabled for EC2 OR ECR
- **deploy_workers_onto_private_subnets**: Added pagination to deploy_workers_onto_private_subnets
- **use_immutable_tags_with_ecr**: Added pagination to use_immutable_tags_with_ecr so it handles large number of repositories
- **disable_anonymous_access_for_cluster_roles**: Break when first instance of anonymous access found on a cluster role
- **check_access_to_instance_profile**: Modified check_access_to_instance_profile so it passes when IMDSv2 is required and hop limit == 1
- **check_endpoint_public_access**: Made message check_endpoint_public_access message more accurately reflect the check
- **check_aws_node_daemonset_service_account**: Updated check so it checks if Pod Identities or IRSA is configured for the aws-node daemonset
- **harden.py**: Add error handling with rule names
- **restrict_wildcard_for_cluster_roles**: Fix restrict_wildcard_for_cluster_roles so it doesn't crash when there are roles with no rules
- **use_encryption_with_efs**: Updated use_encryption_with_efs so it checks for encryptInTransit: "true" or unset as this is the new method to set encyrption in transit from EFS CSI Driver > 0.3
- **config.yaml**: Added check_readiness_probes and check_liveness_probes to the config.yaml
- **use_encryption_with_ebs**: Check for EKS auto mode storage classes and fix EBS encryption validation to handle empty storage class parameters

### Refactor

- **Tests**: Refactored tests so they're easier to maintain
- **Test-files**: Deleted extra test files which aren't necessary. Configured the existing test logic so it only read in the required files.
- **create_k8s_test_data.sh**: Script updated so it can add all tests at once or only add a single test based on the good.yaml and bad.yaml files
- Upgrade dependencies and require Python 3.10+

## v0.11.1 (2024-11-17)

## v0.10.5 (2024-10-15)

## v0.11.0 (2024-10-15)

## v0.10.3 (2023-09-11)

### Fix

- Remove debugging statement
- Fix security context container bug
- Check container.security_context.capabilities.add before checking capabilites
- Check rules that config has "cluster_wide" or "namespace_based"
- Change validation condition for check_logs_are_enabled rule
- Print namespace name for passed namespace based rules

## v0.10.1 (2023-07-24)

### Fix

- Add resolution url to the json output

## v0.10.0 (2023-07-12)

### Feat

- Add console size as args

## v0.9.3 (2023-05-15)

### Fix

- Fix aws-node service account irsa bug

## v0.9.2 (2023-05-03)

### Fix

- Ignore public info viewer
- Fix namespace psa bug

## v0.9.0 (2023-03-31)

### Feat

- Add json output
- Implement namespace based rules with rule class
- Implement cluster wide security rules with Rule
- Add consolidated tables for cleaner report
- Implement rule class
- Implement security iam with rule class
- Implement reliabillity checks using rule class
- Make scalability section use the rule class
- Implement cluster autoscaling with new rules class
- **scalability**: adding generic get_kube_config and getting clusters to check
- **scalability**: adding checks for compression and skipped file
- **scalability**: adding first scalability checks

### Fix

- Fix namespace bug
- **scalability**: checking clusterName in cluster.name
- **scalability**: fixing up some things 2
- **scalability**: fixing up some things
- **scalability**: only checking current cluster
- **config**: fix up config
- **config**: uncomment config

### Refactor

- Simplify tests
- Remove Map Class

## v0.8.0 (2023-02-02)

### Feat

- Add check for managed node groups
- Add check for CA role polp
- Add check for separate IRSA for CA
- Add check for CA autodiscovery
- Add check for CA-k8s version mismatch
- Add check for cluster-autoscaler or karpenter

## v0.7.2 (2023-01-11)

### Refactor

- Fix insecure yaml load method
- Use more secure yaml load method

## v0.7.0 (2023-01-02)

### Feat

- Add option to export the report as html or txt

## v0.6.0 (2022-12-15)

### Feat

- Add a cli option for skipping tls verification

## 0.5.0 (2022-12-10)

## v0.5.0 (2022-12-10)

### Feat

- Add links to the doc pages

## 0.4.2 (2022-12-10)

## v0.4.2 (2022-12-10)

### Fix

- Fix non existent csi driver issue

## 0.4.1 (2022-12-10)

## v0.4.1 (2022-12-10)

### Feat

- Get sensible defaults for args
- Add first version of cli

### Fix

- Fix vpa message
- Fix coverage ci issue
- Add check for security context
- Fix secret env var exception
- Add more namespaces to the ignore list
- Add a try except block
- Fix changelog

