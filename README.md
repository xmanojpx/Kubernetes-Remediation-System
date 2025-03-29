# Kubernetes Remediation System

An automated system for detecting and remediating issues in Kubernetes clusters. The system uses predictive analysis to identify potential problems and takes automated actions to prevent service disruptions.

## Features

- **Automated Issue Detection**: Monitors for various types of issues:
  - Resource exhaustion
  - Node failures
  - Performance degradation
  - Resource bottlenecks

- **Intelligent Remediation**: Takes automated actions like:
  - Scaling deployments
  - Relocating pods
  - Optimizing resource allocation
  - Load balancing

- **Metrics & Monitoring**:
  - Prometheus metrics integration
  - Action effectiveness tracking
  - False positive detection
  - Historical action logging

- **REST API**:
  - `/health` - System health check
  - `/remediate` - Handle remediation requests
  - `/actions` - View action history
  - `/effectiveness` - Get effectiveness metrics
  - `/metrics` - Prometheus metrics endpoint

## Getting Started

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn
- Kubernetes cluster (optional - system works in demo mode)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/xmanojpx/Kubernetes-Remediation-System.git
cd Kubernetes-Remediation-System
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
python -m uvicorn src.api.server:app --reload
```

4. Access the web interface at http://localhost:8000

### Usage

The system can be used in two modes:

1. **Demo Mode** (default):
   - No Kubernetes cluster required
   - Simulates remediation actions
   - Perfect for testing and development

2. **Production Mode**:
   - Requires Kubernetes cluster access
   - Takes real remediation actions
   - Monitors actual cluster metrics

### API Examples

1. Check system health:
```bash
curl http://localhost:8000/health
```

2. Test remediation:
```bash
curl -X POST http://localhost:8000/remediate \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

3. View action history:
```bash
curl http://localhost:8000/actions
```

## Project Structure

```
.
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── server.py
│   └── remediation/
│       ├── __init__.py
│       ├── agent.py
│       ├── kubernetes_client.py
│       └── metrics.py
├── static/
│   └── index.html
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
   

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
