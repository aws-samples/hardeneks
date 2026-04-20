from typing import Optional
from kubernetes import client


class Resources:
    def __init__(self, region, context, cluster, namespaces):
        self.region = region
        self.context = context
        self.cluster = cluster
        self.namespaces = namespaces

    def set_resources(self):
        self.cluster_roles = (
            client.RbacAuthorizationV1Api().list_cluster_role().items
        )
        self.cluster_role_bindings = (
            client.RbacAuthorizationV1Api().list_cluster_role_binding().items
        )
        self.resource_quotas = (
            client.CoreV1Api().list_resource_quota_for_all_namespaces().items
        )
        self.network_policies = (
            client.NetworkingV1Api()
            .list_network_policy_for_all_namespaces()
            .items
        )
        self.storage_classes = client.StorageV1Api().list_storage_class().items
        self.persistent_volumes = (
            client.CoreV1Api().list_persistent_volume().items
        )
        self.services = (
            client.CoreV1Api().list_service_for_all_namespaces().items
        )
        self.namespace_list = client.CoreV1Api().list_namespace().items
        self.deployments = (
            client.AppsV1Api().list_deployment_for_all_namespaces().items
        )
        self.nodes = client.CoreV1Api().list_node().items

    def apply_masking(self, masker) -> None:
        """Apply name masking in-place using *masker*.

        Masks:
        * ``self.namespaces`` list (strings)
        * ``metadata.name`` of every item in all resource collections
          that carry a ``metadata`` attribute
        * ``metadata.namespace`` of every namespaced resource item
        """
        if masker is None:
            return

        self.namespaces = masker.mask_namespaces(self.namespaces)

        resource_collections = [
            self.cluster_roles,
            self.cluster_role_bindings,
            self.resource_quotas,
            self.network_policies,
            self.storage_classes,
            self.persistent_volumes,
            self.services,
            self.namespace_list,
            self.deployments,
            self.nodes,
        ]

        for collection in resource_collections:
            _mask_collection(collection, masker)


class NamespacedResources:
    def __init__(self, region, context, cluster, namespace):
        self.namespace = namespace
        self.region = region
        self.cluster = cluster
        self.context = context

    def set_resources(self):
        self.roles = (
            client.RbacAuthorizationV1Api()
            .list_namespaced_role(self.namespace)
            .items
        )
        self.pods = (
            client.CoreV1Api().list_namespaced_pod(self.namespace).items
        )
        self.role_bindings = (
            client.RbacAuthorizationV1Api()
            .list_namespaced_role_binding(self.namespace)
            .items
        )
        self.deployments = (
            client.AppsV1Api().list_namespaced_deployment(self.namespace).items
        )
        self.daemon_sets = (
            client.AppsV1Api().list_namespaced_daemon_set(self.namespace).items
        )
        self.stateful_sets = (
            client.AppsV1Api()
            .list_namespaced_stateful_set(self.namespace)
            .items
        )
        self.services = (
            client.CoreV1Api().list_namespaced_service(self.namespace).items
        )
        self.hpas = (
            client.AutoscalingV1Api()
            .list_namespaced_horizontal_pod_autoscaler(self.namespace)
            .items
        )

    def apply_masking(self, masker) -> None:
        """Apply name masking in-place using *masker*.

        Masks:
        * ``self.namespace`` (the namespace this object represents)
        * ``metadata.name`` of every item in all resource collections,
          unless the resource's namespace is excluded
        * ``metadata.namespace`` of every resource item
        """
        if masker is None:
            return

        original_namespace = self.namespace
        self.namespace = masker.mask_namespace(original_namespace)

        resource_collections = [
            self.roles,
            self.pods,
            self.role_bindings,
            self.deployments,
            self.daemon_sets,
            self.stateful_sets,
            self.services,
            self.hpas,
        ]

        for collection in resource_collections:
            _mask_collection(collection, masker, namespace=original_namespace)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _mask_collection(
    collection: list,
    masker,
    namespace: Optional[str] = None,
) -> None:
    """Mask ``metadata.name`` and ``metadata.namespace`` on each item
    in *collection* in-place.

    *namespace* is the logical namespace of the resource, used to honour
    namespace-level exclusion rules for resource names.
    """
    for item in collection:
        meta = getattr(item, "metadata", None)
        if meta is None:
            continue
        if hasattr(meta, "name") and meta.name is not None:
            meta.name = masker.mask_resource_name(
                meta.name, namespace=namespace
            )
        if hasattr(meta, "namespace") and meta.namespace is not None:
            meta.namespace = masker.mask_namespace(meta.namespace)
