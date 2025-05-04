# Hostel Mess Management System - DevOps Implementation

This project implements a complete DevOps pipeline for a Hostel Mess Management System, featuring containerization, orchestration, infrastructure as code, and continuous deployment.

## System Architecture

![System Architecture](https://mermaid.ink/img/pako:eNqNk01v2zAMhv8K4ZMHJBiSHPYMpMXQYRj6caiwA7FDYDCyldoEbEmQ5XZYkP8-KXXtbNtpPUkW3yePSNLTtOYcU5F2FbWPYE21UXAzfPX6-4fb4eufd59BEGMVMDYfj0yoMHxfyg2DufFYz6FkNBqkBu4jfSvZVmG7XUqFLz9XUjXQ7xn7oDu9VVCwQvN2J3jFSDzO8-QzJR3YAJrxkpB-KpqhVyaEITQ53DMMTZXdnFuVmhE9vGboU8DGnfKcRLXf0N0Zw-uWoIcCvFJyaZBNK_XAK2rD82iHDqsWyB7-4AJ45a0RNrREVTJ8JPpaqkVl-U-Ie1XYzgmTMrOSHBzVdgSl2vCpR-cwbQVJCZ0WSdmwDMZJC0_1XHCwQGEXW7BWl_dI7HnYokXJ3HMxtHF3H9XHUHrwGNdkd8I-_nZcWx-0VxduNxG1nZXb0x_OP53GPCKqS2r0hLyT3NnXfDmPf06hfmL6BG3W0xmvqbFT2TBjprLnGr107pI-8U9_R3NxP-KONzumNJPjZ6o9OGPUlucjl_nZ3Uu7g2ej--j-Aqg_3T0?type=png)

## Technology Stack

- **Frontend**: Streamlit web application for mess management interface
- **Backend**: FastAPI RESTful API service for data handling
- **Containerization**: Docker for packaging applications
- **Orchestration**: Kubernetes for container management
- **Infrastructure as Code**: Terraform and Ansible
- **CI/CD**: GitHub Actions pipeline
- **Monitoring**: Prometheus and Grafana

## Components

### 1. Application Code

- **mess-frontend**: Streamlit web application for the mess management user interface
- **mess-backend**: FastAPI-based API providing data and business logic

### 2. DevOps Implementation

- **Docker**: Containerization of both frontend and backend services
- **Kubernetes**: Deployment, scaling, and management of containerized applications
- **Terraform**: Infrastructure provisioning on AWS
- **Ansible**: Configuration management and application deployment
- **GitHub Actions**: CI/CD pipeline for testing, building, and deploying
- **Monitoring**: Prometheus for metrics collection and Grafana for visualization

## Infrastructure Setup

The infrastructure is provisioned on AWS using Terraform:

1. **VPC**: Dedicated virtual private cloud with public and private subnets
2. **EKS Cluster**: Managed Kubernetes service for container orchestration
3. **ECR**: Container registry for storing Docker images
4. **S3 & DynamoDB**: For Terraform state management

## CI/CD Pipeline

The GitHub Actions workflow automates:

1. **Testing**: Running unit and integration tests
2. **Building**: Building Docker images for frontend and backend
3. **Publishing**: Pushing images to Amazon ECR
4. **Deploying**: Updating Kubernetes deployments with new images
5. **Notification**: Sending notifications on pipeline completion/failure

## Deployment and Scaling

Kubernetes handles:

1. **Deployments**: Managing the rollout of application updates
2. **Services**: Exposing applications with load balancing
3. **Autoscaling**: Adjusting replicas based on resource usage
4. **Health Checks**: Ensuring application availability

## Monitoring and Logging

- **Prometheus**: Collects metrics from applications and infrastructure
- **Grafana**: Visualizes metrics and provides dashboards
- **ELK Stack**: Can be integrated for centralized logging (optional extension)

## Getting Started

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured locally
- Terraform installed locally
- kubectl installed locally
- GitHub account for setting up Actions workflow

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd hostel-mess-management-system
   ```

2. **Initialize Terraform**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

3. **Configure kubectl**
   ```bash
   aws eks update-kubeconfig --region <region> --name mess-management-cluster
   ```

4. **Deploy Application Using Ansible**
   ```bash
   cd ../ansible
   ansible-playbook -i inventory.yml playbook.yml
   ```

5. **Access the Application**
   ```bash
   kubectl get service mess-frontend-service
   ```
   Use the EXTERNAL-IP address displayed to access the application.

## Development Workflow

1. Create a feature branch from main
2. Implement changes and write tests
3. Submit a pull request
4. Automated tests run via GitHub Actions
5. After approval and merge to main, the CI/CD pipeline deploys changes

## Security Considerations

- Secrets managed via Kubernetes Secrets and GitHub Secrets
- Network policies enforced at the Kubernetes level
- IAM roles with least privilege principle
- Regular security scanning of Docker images

## Challenges and Solutions

- **Challenge**: Managing environment variables across different environments
  **Solution**: Kubernetes ConfigMaps and Secrets with environment-specific values

- **Challenge**: Ensuring zero-downtime deployments
  **Solution**: Kubernetes rolling updates with proper health checks

- **Challenge**: Resource optimization
  **Solution**: Horizontal Pod Autoscaler based on CPU/memory metrics

## Future Improvements

1. Implement GitOps with ArgoCD or Flux
2. Add canary deployments or blue/green strategy
3. Enhance monitoring with custom metrics and alerts
4. Implement distributed tracing with Jaeger or Zipkin
5. Integrate security scanning tools like Trivy and SonarQube
