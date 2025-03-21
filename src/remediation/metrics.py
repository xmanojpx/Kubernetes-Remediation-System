from prometheus_client import Counter, Histogram, Gauge
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        """Initialize metrics collectors."""
        # Action metrics
        self.action_counter = Counter(
            'remediation_actions_total',
            'Total number of remediation actions taken',
            ['action_type', 'success']
        )
        self.action_duration = Histogram(
            'remediation_action_duration_seconds',
            'Duration of remediation actions',
            ['action_type']
        )
        
        # Prevention metrics
        self.prevention_counter = Counter(
            'issues_prevented_total',
            'Total number of issues prevented',
            ['issue_type']
        )
        
        # False positive metrics
        self.false_positive_counter = Counter(
            'false_positives_total',
            'Total number of false positive predictions',
            ['action_type']
        )
        
        # Resource utilization
        self.resource_utilization = Gauge(
            'resource_utilization_percent',
            'Resource utilization percentage',
            ['resource_type', 'namespace']
        )

    def record_action(self, action_type: str, success: bool, duration: float):
        """Record a remediation action."""
        try:
            self.action_counter.labels(action_type=action_type, success=str(success)).inc()
            self.action_duration.labels(action_type=action_type).observe(duration)
        except Exception as e:
            logger.error(f"Error recording action metric: {str(e)}")

    def record_prevention(self, issue_type: str):
        """Record a prevented issue."""
        try:
            self.prevention_counter.labels(issue_type=issue_type).inc()
        except Exception as e:
            logger.error(f"Error recording prevention metric: {str(e)}")

    def record_false_positive(self, action: dict):
        """Record a false positive prediction."""
        try:
            action_type = action.get("type", "unknown")
            self.false_positive_counter.labels(action_type=action_type).inc()
        except Exception as e:
            logger.error(f"Error recording false positive metric: {str(e)}")

    def record_resource_utilization(self, resource_type: str, namespace: str, value: float):
        """Record resource utilization."""
        try:
            self.resource_utilization.labels(
                resource_type=resource_type,
                namespace=namespace
            ).set(value)
        except Exception as e:
            logger.error(f"Error recording resource utilization: {str(e)}")

    def get_metrics(self) -> dict:
        """Get current metrics values."""
        try:
            return {
                "actions": {
                    "total": self.action_counter._value.sum(),
                    "success_rate": self._calculate_success_rate(),
                    "average_duration": self._calculate_average_duration()
                },
                "preventions": {
                    "total": self.prevention_counter._value.sum()
                },
                "false_positives": {
                    "total": self.false_positive_counter._value.sum()
                },
                "resource_utilization": self._get_resource_utilization()
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            return {}

    def _calculate_success_rate(self) -> float:
        """Calculate the success rate of actions."""
        try:
            total = self.action_counter._value.sum()
            if total == 0:
                return 0.0
            successful = sum(
                v for k, v in self.action_counter._value.items()
                if k[1] == "True"
            )
            return successful / total
        except Exception as e:
            logger.error(f"Error calculating success rate: {str(e)}")
            return 0.0

    def _calculate_average_duration(self) -> float:
        """Calculate the average duration of actions."""
        try:
            if self.action_duration._sum.sum() == 0:
                return 0.0
            return self.action_duration._sum.sum() / self.action_duration._count.sum()
        except Exception as e:
            logger.error(f"Error calculating average duration: {str(e)}")
            return 0.0

    def _get_resource_utilization(self) -> dict:
        """Get current resource utilization values."""
        try:
            utilization = {}
            for labels, value in self.resource_utilization._value.items():
                resource_type, namespace = labels
                if namespace not in utilization:
                    utilization[namespace] = {}
                utilization[namespace][resource_type] = value
            return utilization
        except Exception as e:
            logger.error(f"Error getting resource utilization: {str(e)}")
            return {} 