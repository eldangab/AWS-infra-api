# AWS Infrastructure Monitoring

A comprehensive web application for monitoring AWS infrastructure, providing real-time insights into AWS resources including S3 buckets, ECS clusters, and EBS volumes with a focus on security and performance.



## Features

- **Real-time Monitoring**: Track status and performance metrics of AWS resources
- **Multi-service Support**: Monitor ECS, S3, and EBS resources from a single dashboard
- **Cross-region Management**: Switch between AWS regions seamlessly
- **Security Insights**: Analyze resource security posture and get actionable recommendations
- **User-friendly Interface**: Intuitive dashboard with search and filtering capabilities
- **Secure Authentication**: Token-based authentication with AWS credential validation

## Prerequisites

- Python 3.9+
- pip
- AWS Account with access credentials

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/aws-infrastructure-monitor.git
cd aws-infrastructure-monitor
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
Create a `.env` file in the project root:
```
SECRET_KEY=your_generated_secret_key
JWT_SECRET_KEY=another_generated_secret_key
TOKEN_EXPIRATION_MINUTES=60
```

5. Generate secret keys (copy output to `.env` file)
```python
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32)); print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

## Running the Application

```bash
python run.py
```

The application will be available at:
- Standard HTTP (not recommended for production): `http://localhost:5000/`
- HTTPS (self-signed certificate): `https://localhost:5000/`

## API Endpoints Reference

### Authentication

#### Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Description**: Authenticate with AWS credentials and receive JWT token
- **Request Body**:
```json
{
  "aws_access_key_id": "YOUR_AWS_ACCESS_KEY",
  "aws_secret_access_key": "YOUR_AWS_SECRET_KEY",
  "aws_region": "us-west-2"
}
```
- **Response**:
```json
{
  "token": "your.jwt.token",
  "expires_at": "2025-03-05T14:30:00Z"
}
```
- **Status Codes**:
  - `200 OK`: Authentication successful
  - `401 Unauthorized`: Invalid credentials

### S3 Monitoring

#### List Buckets
- **Endpoint**: `GET /api/v1/s3/buckets`
- **Description**: Retrieve all S3 buckets
- **Headers**: `Authorization: <JWT_TOKEN>`
- **Response**:
```json
{
  "buckets": [
    "example-bucket-1",
    "example-bucket-2"
  ]
}
```

#### Get Bucket Details
- **Endpoint**: `GET /api/v1/s3/buckets/{bucket_name}/details`
- **Description**: Get detailed information about a specific bucket
- **Headers**: `Authorization: <JWT_TOKEN>`
- **Response**:
```json
{
  "name": "example-bucket-1",
  "location": "us-west-2",
  "size": "2.5 GB",
  "encryption": {
    "ServerSideEncryptionConfiguration": { ... }
  }
}
```

### ECS Monitoring

#### List Clusters
- **Endpoint**: `GET /api/v1/ecs/clusters`
- **Description**: Retrieve all ECS clusters
- **Headers**: `Authorization: <JWT_TOKEN>`
- **Response**:
```json
{
  "clusters": [
    "arn:aws:ecs:region:account:cluster/cluster-name",
    "arn:aws:ecs:region:account:cluster/another-cluster"
  ]
}
```

#### List Cluster Services
- **Endpoint**: `GET /api/v1/ecs/clusters/{cluster_name}/services`
- **Description**: List services in a specific cluster
- **Headers**: `Authorization: <JWT_TOKEN>`
- **Response**:
```json
{
  "services": [
    "arn:aws:ecs:region:account:service/cluster-name/service-name",
    "arn:aws:ecs:region:account:service/cluster-name/another-service"
  ]
}
```

#### Get Cluster Details
- **Endpoint**: `GET /api/v1/ecs/clusters/{cluster_name}/details`
- **Description**: Get detailed information about a specific cluster
- **Headers**: `Authorization: <JWT_TOKEN>`
- **Response**:
```json
{
  "name": "cluster-name",
  "status": "ACTIVE",
  "serviceCount": 3
}
```

### EBS Monitoring

#### List Volumes
- **Endpoint**: `GET /api/v1/ebs/volumes`
- **Description**: Retrieve all EBS volumes
- **Headers**: `Authorization: <JWT_TOKEN>`
- **Response**:
```json
{
  "volumes": [
    {
      "volume_id": "vol-0a1b2c3d4e5f6g7h8",
      "size": 100,
      "volume_type": "gp3",
      "state": "in-use",
      "iops": 3000,
      "throughput": 125,
      "attached_instance": "i-0a1b2c3d4e5f6g7h8",
      "device": "/dev/sda1",
      "availability_zone": "us-west-2a",
      "encrypted": true
    }
  ]
}
```

#### Get Volume Metrics
- **Endpoint**: `GET /api/v1/ebs/volumes/{volume_id}/metrics`
- **Description**: Get performance metrics for a specific volume
- **Headers**: `Authorization: <JWT_TOKEN>`
- **Query Parameters**:
  - `period`: The granularity of the metrics in seconds (default: 3600)
  - `start_time`: Start time for metrics (default: 24 hours ago)
  - `end_time`: End time for metrics (default: now)
- **Response**:
```json
{
  "volume_id": "vol-0a1b2c3d4e5f6g7h8",
  "metrics": {
    "read_ops": [
      {"timestamp": "2025-03-05T12:00:00Z", "value": 1245.6},
      {"timestamp": "2025-03-05T13:00:00Z", "value": 1356.2}
    ],
    "write_ops": [
      {"timestamp": "2025-03-05T12:00:00Z", "value": 2341.8},
      {"timestamp": "2025-03-05T13:00:00Z", "value": 2567.3}
    ],
    "read_bytes": [...],
    "write_bytes": [...],
    "queue_length": [...]
  }
}
```

### Dashboard

#### Overview
- **Endpoint**: `GET /api/v1/dashboard/overview`
- **Description**: Get comprehensive overview of all resources
- **Headers**: `Authorization: <JWT_TOKEN>`
- **Response**:
```json
{
  "s3": {
    "total_buckets": 5,
    "bucket_details": [...]
  },
  "ecs": {
    "total_clusters": 2,
    "cluster_details": [...]
  },
  "ebs": {
    "total_volumes": 8,
    "volume_details": [...]
  }
}
```

#### Security Insights
- **Endpoint**: `GET /api/v1/dashboard/security_insights`
- **Description**: Get security analysis of resources
- **Headers**: `Authorization: <JWT_TOKEN>`
- **Response**:
```json
{
  "security_insights": {
    "s3": [
      {
        "bucket_name": "example-bucket",
        "encryption_status": "Not Encrypted"
      }
    ],
    "ebs": [
      {
        "volume_id": "vol-123456789",
        "encryption_status": "Encrypted"
      }
    ]
  }
}
```

## Querying the API

### Authentication Flow

1. **Login to get a token**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"aws_access_key_id": "YOUR_ACCESS_KEY", "aws_secret_access_key": "YOUR_SECRET_KEY", "aws_region": "us-west-2"}' \
  https://localhost:5000/api/v1/auth/login
```

2. **Store the token**
```
export TOKEN="your.jwt.token"
```

3. **Use the token in subsequent requests**
```bash
curl -H "Authorization: $TOKEN" https://localhost:5000/api/v1/s3/buckets
```

### Using with Postman

1. **Login Request**
   - Method: `POST`
   - URL: `https://localhost:5000/api/v1/auth/login`
   - Body (raw JSON):
   ```json
   {
     "aws_access_key_id": "YOUR_ACCESS_KEY",
     "aws_secret_access_key": "YOUR_SECRET_KEY",
     "aws_region": "us-west-2"
   }
   ```

2. **Resource Requests**
   - Method: `GET`
   - URL: Any endpoint, e.g., `https://localhost:5000/api/v1/s3/buckets`
   - Authorization: Set the token in the "Authorization" header

### JavaScript Fetch Example
```javascript
// Login and get token
async function login() {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      aws_access_key_id: 'YOUR_ACCESS_KEY',
      aws_secret_access_key: 'YOUR_SECRET_KEY',
      aws_region: 'us-west-2'
    })
  });
  
  const data = await response.json();
  return data.token;
}

// Get resources using token
async function getResources(token, endpoint) {
  const response = await fetch(endpoint, {
    headers: {
      'Authorization': token
    }
  });
  
  return await response.json();
}

// Usage
async function main() {
  const token = await login();
  const s3Data = await getResources(token, '/api/v1/s3/buckets');
  console.log(s3Data);
}
```

## Development

### Project Structure
```
aws-infrastructure-monitor/
│
├── app/
│   ├── __init__.py
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── auth/
│   │       ├── s3/
│   │       ├── ecs/
│   │       ├── ebs/
│   │       └── dashboard/
│   │
│   ├── config/
│   ├── models/
│   ├── services/
│   ├── templates/
│   ├── static/
│   └── utils/
│
├── tests/
├── .env
├── requirements.txt
└── run.py
```

### Required IAM Permissions

For full functionality, your AWS IAM user should have at minimum:
- `AmazonS3ReadOnlyAccess`
- `AmazonECSReadOnlyAccess`
- `AmazonEC2ReadOnlyAccess`
- `CloudWatchReadOnlyAccess`

## Security Considerations

- This application uses JWT tokens for authentication
- AWS credentials are never stored on disk
- All API endpoints require authentication
- HTTPS is recommended for all communications
- Token-based sessions have an expiration time
- Sensitive operations require fresh authentication

## Troubleshooting

### Common Issues

1. **Login Fails**
   - Verify AWS credentials are correct
   - Check IAM permissions for the user

2. **No Resources Shown**
   - Ensure your AWS account has the resources in the selected region
   - Verify API permissions in IAM policy

3. **HTTPS Certificate Warning**
   - The default installation uses a self-signed certificate
   - For production, use a valid SSL certificate

### Logs

Application logs are available in the console. For more detailed logging, modify the logging configuration in `config/config.py`.



## Contact

eldangab@gmail.corp
