# City Population Service

A containerized microservice that maintains a list of cities and their populations, with RESTful endpoints for retrieving and updating population information.

## Features

- Health check endpoint (`/health`)
- Endpoint for inserting/updating a city's population (`/city` - PUT/POST)
- Endpoint for retrieving a city's population (`/city/<name>` - GET)
- Data stored in MySQL database
- Containerized with Docker
- Deployable to Kubernetes via Helm chart

## Project Structure

```
city-population-service/
├── app/
│   ├── __init__.py      # Flask application factory
│   ├── main.py          # Route definitions and handlers
│   └── db.py            # Database client for MySQL
├── helm/
│   └── city-population-service/
│       ├── Chart.yaml             # Helm chart metadata with MySQL dependency
│       ├── values.yaml            # Configuration values for the service
│       └── templates/
│           ├── deployment.yaml    # Kubernetes deployment configuration
│           ├── service.yaml       # Kubernetes service configuration
│           ├── secret.yaml        # Kubernetes secret for database credentials
│           └── _helpers.tpl       # Helper templates for Helm
├── Dockerfile          # Docker configuration for building the container
├── requirements.txt    # Python dependencies
├── wsgi.py             # WSGI entry point
└── README.md           # This file
```

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
- MySQL database
- Docker (for containerization)
- Kubernetes and Helm (for deployment)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd city-population-service
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up local MySQL database:
```bash
# Using Docker for local development
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=citydb \
  -e MYSQL_USER=cityapp \
  -e MYSQL_PASSWORD=password \
  -p 3306:3306 \
  mysql:8.0
```

4. Set environment variables:
```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DATABASE=citydb
export MYSQL_USER=cityapp
export MYSQL_PASSWORD=password
```

5. Run the application:
```bash
python wsgi.py
```

## Docker Build

Build the Docker image:
```bash
docker build -t city-population-service:latest .
```

Run the container:
```bash
docker run -p 5000:5000 \
  -e MYSQL_HOST=mysql-host \
  -e MYSQL_PORT=3306 \
  -e MYSQL_DATABASE=citydb \
  -e MYSQL_USER=cityapp \
  -e MYSQL_PASSWORD=password \
  city-population-service:latest
```

## Kubernetes Deployment with Helm

### Prerequisites
- A Kubernetes cluster
- Helm v3 installed
- `kubectl` configured to access your cluster

### Adding Required Helm Repositories

```bash
# Add Bitnami repo for MySQL chart
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Update Dependencies

```bash
# Inside the helm/city-population-service directory
helm dependency update
```

### Deployment Steps

1. Push your Docker image to a registry accessible to your Kubernetes cluster:
```bash
# Tag the image for your registry
docker tag city-population-service:latest your-registry/city-population-service:latest

# Push the image
docker push your-registry/city-population-service:latest
```

2. Update the `helm/city-population-service/values.yaml` with your specific configuration:
   - Update the image repository to point to your Docker image
   - Configure MySQL settings as needed

3. Deploy the Helm chart:
```bash
helm install city-population ./helm/city-population-service
```

4. Check the status of the deployment:
```bash
kubectl get pods
```

### Connecting to AWS EKS

If you're using AWS EKS, follow these steps to connect:

1. Configure AWS CLI:
```bash
aws configure
```

2. Update your kubeconfig:
```bash
aws eks update-kubeconfig --name your-cluster-name --region your-aws-region
```

3. Verify connection:
```bash
kubectl get nodes
```

4. Deploy your application as described above.

## Testing the Endpoints

You can use port-forwarding to test your endpoints:

```bash
# Forward the service port to your local machine
kubectl port-forward svc/city-population-city-population-service 5000:80
```

Then in another terminal:

```bash
# Test health endpoint
curl http://localhost:5000/health

# Add a city
curl -X POST http://localhost:5000/city \
  -H "Content-Type: application/json" \
  -d '{"name":"New York", "population":8804190}'

# Get a city
curl http://localhost:5000/city/new%20york
```

## Troubleshooting

### Application Issues

If the application isn't working as expected:

1. Check application logs:
```bash
kubectl logs -l app.kubernetes.io/name=city-population-service
```

2. Verify MySQL connection:
```bash
kubectl exec -it <pod-name> -- env | grep MYSQL
```

3. Test database connectivity from the pod:
```bash
kubectl exec -it <pod-name> -- python -c "import pymysql; conn = pymysql.connect(host='city-population-mysql', user='cityapp', password='password123', database='citydb'); print('Connection successful!')"
```

### Database Issues

If there are issues with the database:

1. Check MySQL pod status:
```bash
kubectl get pods -l app.kubernetes.io/name=mysql
```

2. Check MySQL logs:
```bash
kubectl logs -l app.kubernetes.io/name=mysql
```

3. Check MySQL service:
```bash
kubectl get service city-population-mysql
```

## Production Considerations

For production deployments:

1. **Security**:
   - Use Kubernetes Secrets for storing sensitive information like database credentials
   - Configure network policies to restrict access to the database
   - Enable TLS for secure communication

2. **Scalability**:
   - Configure Horizontal Pod Autoscaler for the application
   - Set appropriate resource requests and limits
   - Use a managed database service for MySQL in production

3. **Reliability**:
   - Implement proper health checks and readiness probes
   - Configure appropriate liveness probes
   - Set up database backups and replication
   - Use persistent volumes with appropriate storage classes

4. **Monitoring and Logging**:
   - Implement monitoring with tools like Prometheus and Grafana
   - Set up centralized logging with tools like ELK stack or CloudWatch
   - Configure alerts for critical issues

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.