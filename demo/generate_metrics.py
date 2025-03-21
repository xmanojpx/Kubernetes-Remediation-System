import requests
import time
import random
from datetime import datetime

def send_prediction(prediction_data):
    """Send a prediction to the remediation API."""
    try:
        response = requests.post(
            'http://localhost:8000/remediate',
            json=prediction_data
        )
        return response.json()
    except Exception as e:
        print(f"Error sending prediction: {str(e)}")
        return None

def generate_resource_exhaustion():
    """Generate a resource exhaustion prediction."""
    return {
        "issue_type": "resource_exhaustion",
        "confidence": random.uniform(0.8, 0.99),
        "target": {
            "deployment": "web-app",
            "namespace": "default",
            "current_replicas": 2
        },
        "details": {
            "usage_increase": random.uniform(1.3, 2.0)
        }
    }

def generate_node_failure():
    """Generate a node failure prediction."""
    return {
        "issue_type": "node_failure",
        "confidence": random.uniform(0.8, 0.99),
        "target": {
            "pods": ["web-app-1", "web-app-2"],
            "namespace": "default"
        }
    }

def generate_resource_bottleneck():
    """Generate a resource bottleneck prediction."""
    return {
        "issue_type": "resource_bottleneck",
        "confidence": random.uniform(0.8, 0.99),
        "target": {
            "deployment": "resource-heavy",
            "namespace": "default",
            "current_cpu": "500m",
            "current_memory": "512Mi"
        },
        "details": {
            "cpu_adjustment": random.uniform(1.1, 1.5),
            "memory_adjustment": random.uniform(1.1, 1.5)
        }
    }

def main():
    """Main function to generate and send predictions."""
    generators = [
        generate_resource_exhaustion,
        generate_node_failure,
        generate_resource_bottleneck
    ]
    
    print("Starting metrics generation...")
    while True:
        try:
            # Generate a random prediction
            generator = random.choice(generators)
            prediction = generator()
            
            # Send the prediction
            print(f"\nSending prediction at {datetime.now().isoformat()}")
            print(f"Type: {prediction['issue_type']}")
            result = send_prediction(prediction)
            
            if result:
                print(f"Result: {'Success' if result['success'] else 'Failed'}")
            
            # Wait between 30-60 seconds before next prediction
            wait_time = random.uniform(30, 60)
            print(f"Waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
            
        except KeyboardInterrupt:
            print("\nStopping metrics generation...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    main() 