# City Population Service

This is a microservice that maintains a list of cities and their population data. It provides RESTful endpoints for retrieving and updating population information.

## Features

- Health check endpoint (`/health`)
- Endpoint for inserting/updating a city's population (`/city` - PUT/POST)
- Endpoint for retrieving a city's population (`/city/<name>` - GET)
- Data is stored in Elasticsearch
- Containerized with Docker
- Deployable to Kubernetes via Helm

## API Usage

### Check Service Health
```
GET /health
```
Returns "OK" if the service is up and running.

### Add or Update a City's Population
```
POST /city
Content-Type: application/json

{
  "name": "New York",
  "population": 8804190
}
```
Adds a new city or updates an existing city's population.

### Retrieve a City's Population
```
GET /city/new-york
```
Returns the population of the specified city.

## Local Development

### Prerequisites
- Python 3.8+
- Elasticsearch (can be run via Docker)
- Docker (for containerization)
- Kubernetes and Helm (for deployment)

### Setup

1. Clone the repository:
```
git clone <repository-url>
cd city-population-service
```

2. Create a virtual environment and install dependencies:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Start Elasticsearch (via Docker):
```
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:7.17.0
```

4. Run the application:
```
python wsgi.py
```

## Docker Build

Build the Docker image:
```
docker build -t city-population-service:latest .
```

Run the container:
```
docker run -p 5000:5000 -e ELASTICSEARCH_HOST=<elasticsearch-host> city-population-service:latest
```

## Kubernetes Deployment

### Prerequisites
- A Kubernetes cluster
- Helm v3 installed
- `kubectl` configured to access your cluster

### Deployment Steps

1. Make sure your Docker image is pushed to a registry accessible to your Kubernetes cluster.

2. Update the `helm/city-population-service/values.yaml` with your specific configuration:
   - Update the image repository to point to your Docker image
   - Configure Elasticsearch settings as needed

3. Deploy the Helm chart:
```
helm install city-pop ./helm/city-population-service
```

4. To check the status of the deployment:
```
kubectl get pods
```

5. To access the service (if using minikube):
```
minikube service city-pop-city-population-service
```

### Using a Custom Elasticsearch Instance

If you want to use an existing Elasticsearch instance instead of deploying one with the chart:

1. Set `elasticsearch.enabled` to `false` in `values.yaml`
2. Configure the Elasticsearch connection details:
```yaml
config:
  elasticsearch:
    host: your-elasticsearch-host
    port: 9200
    user: elastic  # if authentication is enabled
    password: yourpassword
```

## Troubleshooting

### Checking Logs
```
kubectl logs -l app.kubernetes.io/name=city-population-service
```

### Verifying Elasticsearch Connection
```
kubectl exec -it <pod-name> -- curl -X GET http://elasticsearch-master:9200
```

## Security Considerations

- In a production environment, ensure Elasticsearch has authentication enabled
- Consider using Kubernetes Secrets for storing sensitive information like database credentials
- Implement proper network policies to restrict access to the Elasticsearch cluster