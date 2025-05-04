# Architecture Diagrams for Hostel Mess Management System

## System Architecture

```mermaid
graph TD
    subgraph "AWS Cloud"
        subgraph "VPC"
            subgraph "Public Subnet"
                ALB[Application Load Balancer]
                BastionHost[Bastion Host]
            end
            
            subgraph "Private Subnet"
                subgraph "EKS Cluster"
                    subgraph "Frontend Nodes"
                        F1[Frontend Pod 1]
                        F2[Frontend Pod 2]
                    end
                    
                    subgraph "Backend Nodes"
                        B1[Backend Pod 1]
                        B2[Backend Pod 2]
                    end
                    
                    subgraph "Monitoring"
                        Prometheus[Prometheus]
                        Grafana[Grafana]
                    end
                    
                    subgraph "Logging"
                        ES[Elasticsearch]
                        Kibana[Kibana]
                        Filebeat[Filebeat DaemonSet]
                    end
                end
            end
            
            ECR[Elastic Container Registry]
        end
        
        MongoDB[(MongoDB Atlas)]
    end
    
    subgraph "CI/CD Pipeline"
        GH[GitHub Repository]
        Actions[GitHub Actions]
    end
    
    User[User Browser] -->|HTTPS| ALB
    ALB -->|Route| F1 & F2
    F1 & F2 -->|API Calls| B1 & B2
    B1 & B2 -->|Database Queries| MongoDB
    
    GH -->|Trigger| Actions
    Actions -->|Push Images| ECR
    Actions -->|Deploy| EKS
    
    B1 & B2 -->|Export Metrics| Prometheus
    F1 & F2 -->|Export Metrics| Prometheus
    Prometheus -->|Visualization| Grafana
    
    B1 & B2 -->|Logs| Filebeat
    F1 & F2 -->|Logs| Filebeat
    Filebeat -->|Index| ES
    ES -->|Visualization| Kibana
    
    DevOps[DevOps Engineer] -->|SSH| BastionHost
    BastionHost -->|kubectl| EKS
```

## CI/CD Pipeline Flow

```mermaid
flowchart TD
    Dev[Developer] -->|Push Code| Repo[GitHub Repository]
    Repo -->|Trigger| CI[GitHub Actions CI]
    
    subgraph "CI Pipeline"
        Test[Run Tests] --> SonarQube[Code Quality Analysis]
        SonarQube --> Security[Security Scan]
        Security --> Build[Build Docker Images]
    end
    
    CI -->|On Success| CD[GitHub Actions CD]
    
    subgraph "CD Pipeline"
        Push[Push to ECR] --> Update[Update Kubernetes Manifests]
        Update --> Deploy[Deploy to EKS]
        Deploy --> Verify[Verify Deployment]
    end
    
    CD -->|Success/Failure| Notify[Slack Notification]
```

## Infrastructure as Code

```mermaid
flowchart TD
    subgraph "Terraform - Infrastructure Provisioning"
        VPC[VPC & Subnets] --> IGW[Internet Gateway]
        IGW --> NGW[NAT Gateway]
        NGW --> RT[Route Tables]
        RT --> SG[Security Groups]
        SG --> EKS[EKS Cluster]
        EKS --> NodeGroup[Worker Node Groups]
        NodeGroup --> IAM[IAM Roles & Policies]
        IAM --> ECR[ECR Repositories]
        ECR --> S3[S3 for State]
        S3 --> DynamoDB[DynamoDB for Locking]
    end
    
    subgraph "Ansible - Configuration Management"
        Configure[Configure Instances] --> Install[Install Tools]
        Install --> Deploy[Deploy Applications]
    end
    
    subgraph "Kubernetes - Application Management"
        Deployments[Deployments] --> Services[Services]
        Services --> Ingress[Ingress]
        Ingress --> ConfigMaps[ConfigMaps]
        ConfigMaps --> Secrets[Secrets]
        Secrets --> HPA[Horizontal Pod Autoscaler]
    end
    
    Terraform --> Ansible
    Ansible --> Kubernetes
```

## Monitoring and Logging Architecture

```mermaid
flowchart TD
    subgraph "Applications"
        FrontendApp[Frontend Application]
        BackendApp[Backend Application]
        K8s[Kubernetes Components]
    end
    
    subgraph "Monitoring"
        FrontendApp -->|Metrics| Prometheus[Prometheus]
        BackendApp -->|Metrics| Prometheus
        K8s -->|Metrics| Prometheus
        NodeExporter[Node Exporter] -->|System Metrics| Prometheus
        Prometheus -->|Visualization| Grafana[Grafana]
        Grafana -->|Alerts| AlertManager[Alert Manager]
        AlertManager -->|Notifications| Slack[Slack]
    end
    
    subgraph "Logging"
        FrontendApp -->|Logs| Filebeat[Filebeat]
        BackendApp -->|Logs| Filebeat
        K8s -->|Logs| Filebeat
        Filebeat -->|Shipping| Elasticsearch[Elasticsearch]
        Elasticsearch -->|Visualization| Kibana[Kibana]
    end
    
    subgraph "Dashboards"
        Grafana -->|Service Health| HealthDashboard[Health Dashboard]
        Grafana -->|Performance| PerfDashboard[Performance Dashboard]
        Grafana -->|Resource Usage| ResourceDashboard[Resource Dashboard]
        Kibana -->|Log Analysis| LogDashboard[Log Analysis Dashboard]
        Kibana -->|Error Tracking| ErrorDashboard[Error Dashboard]
    end
```

These diagrams can be rendered using Mermaid, which is supported by many Markdown renderers including GitHub.