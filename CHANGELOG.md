## Unreleased

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
