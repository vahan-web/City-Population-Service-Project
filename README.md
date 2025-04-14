# City Population Service with MySQL

This project provides a containerized RESTful service that maintains a list of cities and their populations, with data stored in a MySQL database. The entire stack is deployed on Kubernetes using Helm charts.

## Project Overview

The system consists of two main components:

1. **MySQL Database** - A StatefulSet deployment of MySQL
2. **City Population Service** - A Python Flask application that provides REST endpoints

## Features

- Health check endpoint (`/health`)
- Endpoint for inserting/updating a city's population (`/city` - POST/PUT)
- Endpoint for retrieving a city's population (`/city/<name>` - GET)
- Data persistence in MySQL
- Fully containerized application and database
- Kubernetes deployment with Helm charts
- Separate deployment of database and application for better scalability

## Repository Structure

```
├── mysql-statefulset/         # MySQL Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── statefulset.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       ├── secret.yaml
│       └── _helpers.tpl
│
├── city-population-service/   # Application Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       ├── secret.yaml
│       └── _helpers.tpl
│
├── app/                       # Application code
│   ├── __init__.py
│   ├── main.py
│   └── db.py
│
├── Dockerfile                 # Container definition
├── requirements.txt           # Python dependencies
└── wsgi.py                    # WSGI entry point
```

## Prerequisites

- Docker
- Kubernetes cluster (local or cloud)
- Helm v3
- kubectl configured to access your cluster

## Local Development

### Setup Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start MySQL with Docker
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=citydb \
  -e MYSQL_USER=cityapp \
  -e MYSQL_PASSWORD=password \
  -p 3306:3306 \
  mysql:8.0

# Set environment variables
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DATABASE=citydb
export MYSQL_USER=cityapp
export MYSQL_PASSWORD=password

# Run application
python wsgi.py
```

### Build Docker Image

```bash
# Build image
docker build -t city-population-service:latest .

# Test with Docker network
docker network create city-net
docker network connect city-net mysql
docker run -p 5000:5000 \
  --network city-net \
  -e MYSQL_HOST=mysql \
  -e MYSQL_PORT=3306 \
  -e MYSQL_DATABASE=citydb \
  -e MYSQL_USER=cityapp \
  -e MYSQL_PASSWORD=password \
  city-population-service:latest
```

## Kubernetes Deployment

### Prepare for Deployment

1. Push your Docker image to a container registry:
   ```bash
   # Tag image for your registry
   docker tag city-population-service:latest your-registry/city-population-service:latest
   
   # Push to registry
   docker push your-registry/city-population-service:latest
   ```

2. Update image repository in values.yaml for both charts:
   ```yaml
   # In city-population-service/values.yaml
   image:
     repository: your-registry/city-population-service
     tag: latest
   ```

### Deploy MySQL StatefulSet

1. Validate the MySQL Helm chart:
   ```bash
   helm template mysql-test ./mysql-statefulset
   ```

2. Deploy MySQL:
   ```bash
   helm install mysql ./mysql-statefulset
   ```

3. Verify MySQL deployment:
   ```bash
   kubectl get pods -l app.kubernetes.io/name=mysql-statefulset
   kubectl get pvc -l app.kubernetes.io/name=mysql-statefulset
   ```

### Deploy City Population Service

1. Validate the application Helm chart:
   ```bash
   helm template city-test ./city-population-service
   ```

2. Deploy the application:
   ```bash
   helm install city-population ./city-population-service
   ```

3. Verify application deployment:
   ```bash
   kubectl get pods -l app.kubernetes.io/name=city-population-service
   ```

## Testing the Application

1. Port-forward to the service:
   ```bash
   kubectl port-forward svc/city-population-city-population-service 8080:80
   ```

2. Test the endpoints:
   ```bash
   # Health check
   curl http://localhost:8080/health
   
   # Add a city
   curl -X POST http://localhost:8080/city \
     -H "Content-Type: application/json" \
     -d '{"name":"New York", "population":8804190}'
   
   # Get a city's population
   curl http://localhost:8080/city/new%20york
   ```

3. Test Exposing the API Publicly:
   ```bash
   # Health check
   curl http://<EXTERNAL-IP>/health
   
   # Add a city
   curl -X POST http://<EXTERNAL-IP>/city \
     -H "Content-Type: application/json" \
     -d '{"name":"New York", "population":8804190}'
   
   # Get a city's population
   curl http://<EXTERNAL-IP>/city/new%20york
   ```

## Customizing Deployment

### Using Custom Values

1. Create a custom values file (e.g., `prod-values.yaml`)
2. Deploy with custom values:
   ```bash
   helm install mysql ./mysql-statefulset -f mysql-prod-values.yaml
   helm install city-population ./city-population-service -f city-prod-values.yaml
   ```

### Key Configuration Options

#### MySQL Values

```yaml
mysql:
  # Resource allocation
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi
  
  # Storage configuration
  persistence:
    size: 10Gi
    storageClass: "standard"  # Use your storage class
  
  # Authentication
  auth:
    rootPassword: "your-secure-root-password"
    password: "your-secure-user-password"
```

#### Application Values

```yaml
# Scaling
replicaCount: 3

# Resources
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 200m
    memory: 256Mi

# MySQL connection
config:
  mysql:
    host: mysql-mysql
    port: 3306
```

## Troubleshooting

### Common Issues

1. **Database connection errors:**
   - Check MySQL pod status: `kubectl get pods -l app.kubernetes.io/name=mysql-statefulset`
   - Check MySQL logs: `kubectl logs -l app.kubernetes.io/name=mysql-statefulset`
   - Verify service: `kubectl get svc mysql-mysql`

2. **Application not starting:**
   - Check application logs: `kubectl logs -l app.kubernetes.io/name=city-population-service`
   - Verify environment variables: `kubectl describe pods -l app.kubernetes.io/name=city-population-service`

3. **Cannot access service:**
   - Check service: `kubectl get svc city-population-city-population-service`
   - Check endpoints: `kubectl get endpoints city-population-city-population-service`