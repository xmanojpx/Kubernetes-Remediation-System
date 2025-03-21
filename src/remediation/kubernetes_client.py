import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class KubernetesClient:
    def __init__(self, demo_mode: bool = True):
        """Initialize the Kubernetes client.
        
        Args:
            demo_mode (bool): Whether to run in demo mode without K8s cluster
        """
        self.demo_mode = demo_mode
        if not demo_mode:
            try:
                from kubernetes import client, config
                config.load_kube_config()
                self.api = client.AppsV1Api()
                self.core_api = client.CoreV1Api()
                self.custom_api = client.CustomObjectsApi()
            except Exception as e:
                logger.error(f"Failed to initialize Kubernetes client: {str(e)}")
                self.demo_mode = True

    def scale_deployment(self, namespace: str, name: str, replicas: int) -> Dict:
        """Scale a deployment to the specified number of replicas."""
        try:
            if self.demo_mode:
                logger.info(f"[DEMO] Scaling deployment {name} in namespace {namespace} to {replicas} replicas")
                return {
                    "action": "scale_deployment",
                    "status": "success",
                    "details": {
                        "namespace": namespace,
                        "deployment": name,
                        "old_replicas": replicas - 1,
                        "new_replicas": replicas,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            deployment = self.api.read_namespaced_deployment(name, namespace)
            deployment.spec.replicas = replicas
            self.api.patch_namespaced_deployment(name, namespace, deployment)
            return {
                "action": "scale_deployment",
                "status": "success",
                "details": {
                    "namespace": namespace,
                    "deployment": name,
                    "old_replicas": deployment.spec.replicas,
                    "new_replicas": replicas,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Failed to scale deployment: {str(e)}")
            return {
                "action": "scale_deployment",
                "status": "error",
                "error": str(e)
            }

    def relocate_pod(self, namespace: str, pod_name: str) -> Dict:
        """Relocate a pod to a different node."""
        try:
            if self.demo_mode:
                logger.info(f"[DEMO] Relocating pod {pod_name} in namespace {namespace}")
                return {
                    "action": "relocate_pod",
                    "status": "success",
                    "details": {
                        "namespace": namespace,
                        "pod": pod_name,
                        "old_node": "node-1",
                        "new_node": "node-2",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            pod = self.core_api.read_namespaced_pod(pod_name, namespace)
            self.core_api.delete_namespaced_pod(pod_name, namespace)
            return {
                "action": "relocate_pod",
                "status": "success",
                "details": {
                    "namespace": namespace,
                    "pod": pod_name,
                    "old_node": pod.spec.node_name,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Failed to relocate pod: {str(e)}")
            return {
                "action": "relocate_pod",
                "status": "error",
                "error": str(e)
            }

    def get_node_metrics(self, node_name: Optional[str] = None) -> Dict:
        """Get metrics for a node or all nodes."""
        try:
            if self.demo_mode:
                logger.info(f"[DEMO] Getting metrics for node {node_name or 'all nodes'}")
                return {
                    "cpu_usage": 0.75,
                    "memory_usage": 0.85,
                    "disk_usage": 0.60,
                    "network_usage": 0.40
                }
            
            metrics = self.custom_api.list_cluster_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="nodes"
            )
            
            if node_name:
                for item in metrics["items"]:
                    if item["metadata"]["name"] == node_name:
                        return self._parse_node_metrics(item)
                return {}
            
            return {
                item["metadata"]["name"]: self._parse_node_metrics(item)
                for item in metrics["items"]
            }
        except Exception as e:
            logger.error(f"Failed to get node metrics: {str(e)}")
            return {}

    def optimize_resources(
        self,
        namespace: str,
        deployment: str,
        cpu_request: Optional[str] = None,
        memory_request: Optional[str] = None
    ) -> Dict:
        """Optimize resource allocation for a deployment."""
        try:
            if self.demo_mode:
                logger.info(f"[DEMO] Optimizing resources for deployment {deployment} in namespace {namespace}")
                return {
                    "action": "optimize_resources",
                    "status": "success",
                    "details": {
                        "namespace": namespace,
                        "deployment": deployment,
                        "changes": {
                            "cpu": {
                                "old": "500m",
                                "new": cpu_request or "750m"
                            },
                            "memory": {
                                "old": "512Mi",
                                "new": memory_request or "768Mi"
                            }
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            deployment_obj = self.api.read_namespaced_deployment(deployment, namespace)
            containers = deployment_obj.spec.template.spec.containers
            
            for container in containers:
                if cpu_request:
                    container.resources.requests["cpu"] = cpu_request
                if memory_request:
                    container.resources.requests["memory"] = memory_request
            
            self.api.patch_namespaced_deployment(deployment, namespace, deployment_obj)
            return {
                "action": "optimize_resources",
                "status": "success",
                "details": {
                    "namespace": namespace,
                    "deployment": deployment,
                    "changes": {
                        "cpu": {
                            "old": containers[0].resources.requests.get("cpu", ""),
                            "new": cpu_request
                        },
                        "memory": {
                            "old": containers[0].resources.requests.get("memory", ""),
                            "new": memory_request
                        }
                    },
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Failed to optimize resources: {str(e)}")
            return {
                "action": "optimize_resources",
                "status": "error",
                "error": str(e)
            }

    def _parse_node_metrics(self, metrics: Dict) -> Dict:
        """Parse node metrics into a standardized format."""
        try:
            cpu = metrics["usage"]["cpu"]
            memory = metrics["usage"]["memory"]
            return {
                "cpu": self._parse_cpu_value(cpu),
                "memory": self._parse_memory_value(memory)
            }
        except Exception as e:
            logger.error(f"Failed to parse node metrics: {str(e)}")
            return {}

    def _parse_cpu_value(self, cpu: str) -> float:
        """Parse CPU value from Kubernetes metrics."""
        try:
            if cpu.endswith("n"):
                return float(cpu[:-1]) / 1e9
            elif cpu.endswith("u"):
                return float(cpu[:-1]) / 1e6
            elif cpu.endswith("m"):
                return float(cpu[:-1]) / 1e3
            return float(cpu)
        except Exception as e:
            logger.error(f"Failed to parse CPU value: {str(e)}")
            return 0.0

    def _parse_memory_value(self, memory: str) -> float:
        """Parse memory value from Kubernetes metrics."""
        try:
            if memory.endswith("Ki"):
                return float(memory[:-2]) * 1024
            elif memory.endswith("Mi"):
                return float(memory[:-2]) * 1024 * 1024
            elif memory.endswith("Gi"):
                return float(memory[:-2]) * 1024 * 1024 * 1024
            return float(memory)
        except Exception as e:
            logger.error(f"Failed to parse memory value: {str(e)}")
            return 0.0 