import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_remediation_api():
    """Test the remediation API endpoints."""
    base_url = "http://localhost:8000"
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        logger.info(f"Health check response: {response.json()}")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
    
    # Test remediation endpoint
    payload = {
        "issue_type": "resource_exhaustion",
        "confidence": 0.95,
        "target": {
            "namespace": "default",
            "deployment": "web-app",
            "replicas": 2
        },
        "details": {
            "usage_increase": 0.9
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/remediate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        logger.info(f"Remediation response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        logger.error(f"Remediation request failed: {str(e)}")
    
    # Test actions history
    try:
        response = requests.get(f"{base_url}/actions")
        logger.info(f"Actions history: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        logger.error(f"Actions history request failed: {str(e)}")
    
    # Test effectiveness metrics
    try:
        response = requests.get(f"{base_url}/effectiveness")
        logger.info(f"Effectiveness metrics: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        logger.error(f"Effectiveness metrics request failed: {str(e)}")

if __name__ == "__main__":
    test_remediation_api() 