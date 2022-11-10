#!/bin/sh
NAMESPACE=test-namespace
TEST_DATA_DIRECTORY=$1

mkdir "$TEST_DATA_DIRECTORY/cluster"
kubectl create namespace $NAMESPACE
kubectl apply -f "$TEST_DATA_DIRECTORY/good.yaml"
kubectl apply -f "$TEST_DATA_DIRECTORY/bad.yaml"
kubectl get namespace -o json > "$TEST_DATA_DIRECTORY/cluster/namespaces_api_response.json"
kubectl get resourcequota -n $NAMESPACE -o json > "$TEST_DATA_DIRECTORY/cluster/resource_quotas_api_response.json"
kubectl get pod -o json -n $NAMESPACE > "$TEST_DATA_DIRECTORY/cluster/pods_api_response.json"
kubectl get service -o json -n $NAMESPACE > "$TEST_DATA_DIRECTORY/cluster/services_api_response.json" 
kubectl get role -o json -n $NAMESPACE > "$TEST_DATA_DIRECTORY/cluster/roles_api_response.json" 
kubectl get clusterrole -o json > "$TEST_DATA_DIRECTORY/cluster/cluster_roles_api_response.json"
kubectl get rolebinding -o json -n $NAMESPACE > "$TEST_DATA_DIRECTORY/cluster/role_bindings_api_response.json" 
kubectl get clusterrolebinding -o json > "$TEST_DATA_DIRECTORY/cluster/cluster_role_bindings_api_response.json" 
kubectl get daemonset -o json -n "$NAMESPACE" > "$TEST_DATA_DIRECTORY/cluster/daemon_sets_api_response.json" 
kubectl get statefulset -o json -n "$NAMESPACE" > "$TEST_DATA_DIRECTORY/cluster/stateful_sets_api_response.json"
kubectl get deployment -o json -n "$NAMESPACE" > "$TEST_DATA_DIRECTORY/cluster/deployments_api_response.json"
kubectl get networkpolicy -o json -n "$NAMESPACE" > "$TEST_DATA_DIRECTORY/cluster/network_policies_api_response.json"
kubectl get hpa -o json -n "$NAMESPACE" > "$TEST_DATA_DIRECTORY/cluster/horizontal_pod_autoscaler_api_response.json"

kubectl delete namespace $NAMESPACE --force
kubectl get namespace $NAMESPACE -o json | jq 'del(.spec.finalizers[0])' | kubectl replace --raw "/api/v1/namespaces/$NAMESPACE/finalize" -f -
