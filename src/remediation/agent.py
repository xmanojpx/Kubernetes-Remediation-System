from typing import Dict, List, Optional
import logging
from .kubernetes_client import KubernetesClient
from .metrics import MetricsCollector
import json
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RemediationAgent:
    def __init__(self, demo_mode: bool = True):
        """Initialize the remediation agent.
        
        Args:
            demo_mode (bool): Whether to run in demo mode without K8s cluster
        """
        self.k8s_client = KubernetesClient(demo_mode=demo_mode)
        self.metrics = MetricsCollector()
        self.action_history = []
        self.demo_mode = demo_mode
        self.prediction_threshold = 0.8  # Confidence threshold for taking action

    def handle_prediction(self, prediction: Dict) -> Dict:
        """Handle a prediction by executing appropriate remediation actions.
        
        Args:
            prediction (Dict): The prediction data containing issue type and details
            
        Returns:
            Dict: Result of remediation actions
        """
        timestamp = datetime.now().isoformat()
        actions = []
        success = True
        error = None

        try:
            if prediction["confidence"] < self.prediction_threshold:
                logger.info(f"Prediction confidence {prediction['confidence']} below threshold")
                return {
                    "timestamp": timestamp,
                    "prediction": prediction,
                    "actions": [],
                    "success": False
                }

            if prediction["issue_type"] == "resource_exhaustion":
                actions = self._handle_resource_exhaustion(prediction)
                action_type = "resource_scaling"
            elif prediction["issue_type"] == "node_failure":
                actions = self._handle_node_failure(prediction)
                action_type = "pod_relocation"
            elif prediction["issue_type"] == "resource_bottleneck":
                actions = self._handle_resource_bottleneck(prediction)
                action_type = "resource_optimization"
            elif prediction["issue_type"] == "performance_degradation":
                actions = self._handle_performance_degradation(prediction)
            else:
                raise ValueError(f"Unknown issue type: {prediction['issue_type']}")

            # Record actions
            for action in actions:
                action["timestamp"] = timestamp
                self.action_history.append(action)
                self.metrics.record_action(action_type, action["success"], action.get("duration", 0))

            if actions:
                self.metrics.record_prevention(prediction["issue_type"])

            return {
                "timestamp": timestamp,
                "prediction": prediction,
                "actions": actions,
                "success": success,
                "error": error
            }

        except Exception as e:
            success = False
            error = str(e)
            logger.error(f"Error handling prediction: {error}")

        return {
            "timestamp": timestamp,
            "prediction": prediction,
            "actions": [],
            "success": success,
            "error": error
        }

    def _handle_resource_exhaustion(self, prediction: Dict) -> List[Dict]:
        """Handle resource exhaustion prediction."""
        actions = []
        target = prediction["target"]
        
        # Scale up deployment
        if prediction.get("details", {}).get("usage_increase", 0) > 0.8:
            scale_result = self.k8s_client.scale_deployment(
                target["namespace"],
                target["deployment"],
                target.get("replicas", 1) + 1
            )
            actions.append({
                "type": "scale_deployment",
                "details": scale_result
            })

        # Optimize resource allocation
        optimize_result = self.k8s_client.optimize_resources(
            target["namespace"],
            target["deployment"]
        )
        actions.append({
            "type": "optimize_resources",
            "details": optimize_result
        })

        return actions

    def _handle_node_failure(self, prediction: Dict) -> List[Dict]:
        """Handle node failure prediction."""
        actions = []
        target = prediction["target"]

        # Relocate affected pods
        relocate_result = self.k8s_client.relocate_pod(
            target["namespace"],
            target["pod"]
        )
        actions.append({
            "type": "relocate_pod",
            "details": relocate_result
        })

        return actions

    def _handle_resource_bottleneck(self, prediction: Dict) -> List[Dict]:
        """Handle resource bottlenecks by optimizing resource allocation."""
        actions = []
        target = prediction["target"]
        
        # Calculate optimal resource requests based on prediction
        current_cpu = target.get("current_cpu", "100m")
        current_memory = target.get("current_memory", "128Mi")
        
        # Adjust resources based on prediction
        cpu_multiplier = prediction["details"].get("cpu_adjustment", 1.2)
        memory_multiplier = prediction["details"].get("memory_adjustment", 1.2)
        
        new_cpu = f"{int(float(current_cpu.replace('m', '')) * cpu_multiplier)}m"
        new_memory = f"{int(float(current_memory.replace('Mi', '')) * memory_multiplier)}Mi"
        
        optimize_result = self.k8s_client.optimize_resources(
            target["namespace"],
            target["deployment"],
            cpu_request=new_cpu,
            memory_request=new_memory
        )
        actions.append({
            "type": "optimize_resources",
            "details": optimize_result
        })

        return actions

    def _handle_performance_degradation(self, prediction: Dict) -> List[Dict]:
        """Handle performance degradation prediction."""
        actions = []
        target = prediction["target"]

        # Get node metrics
        metrics = self.k8s_client.get_node_metrics(target["node"])
        
        # Analyze and optimize based on metrics
        if metrics["cpu_usage"] > 0.8 or metrics["memory_usage"] > 0.8:
            optimize_result = self.k8s_client.optimize_resources(
                target["namespace"],
                target["deployment"]
            )
            actions.append({
                "type": "optimize_resources",
                "details": optimize_result
            })

        return actions

    def get_action_history(self) -> List[Dict]:
        """Get the history of remediation actions."""
        return self.action_history

    def set_prediction_threshold(self, threshold: float) -> None:
        """Update the confidence threshold for taking action."""
        if 0 <= threshold <= 1:
            self.prediction_threshold = threshold
        else:
            raise ValueError("Threshold must be between 0 and 1")

    def get_effectiveness_metrics(self) -> Dict:
        """Get effectiveness metrics of remediation actions."""
        return self.metrics.get_metrics()

    def mark_false_positive(self, action_id: str, action_type: str) -> bool:
        """Mark an action as a false positive for learning."""
        for action in self.action_history:
            if action.get("id") == action_id and action.get("type") == action_type:
                action["false_positive"] = True
                self.metrics.record_false_positive(action)
                return True
        return False 