# app/services/ecs_service.py
import boto3
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ECSService:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region):
        """
        Initialize the ECS service with AWS credentials
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region: AWS region
        """
        # Initialize ECS client
        self.client = boto3.client(
            'ecs',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region
        )
        
        self.region = region
        logger.debug(f"Initialized ECS service for region {region}")

    def list_clusters(self):
        """
        List all ECS clusters with detailed information
        
        Returns:
            dict: Dictionary with a 'clusters' key containing a list of cluster details
        """
        try:
            logger.debug("Attempting to list ECS clusters")
            
            # Get all cluster ARNs
            response = self.client.list_clusters()
            cluster_arns = response.get('clusterArns', [])
            
            if not cluster_arns:
                logger.info("No ECS clusters found")
                return {"clusters": []}
            
            # Get detailed information for each cluster
            clusters_info = []
            
            # Describe clusters to get more details
            describe_response = self.client.describe_clusters(
                clusters=cluster_arns,
                include=['SETTINGS', 'STATISTICS', 'TAGS']
            )
            
            for cluster in describe_response.get('clusters', []):
                # Extract cluster name from ARN
                cluster_arn = cluster.get('clusterArn', '')
                cluster_name = cluster.get('clusterName', '') or cluster_arn.split('/')[-1]
                
                # Get running and pending tasks count
                tasks_response = self.client.list_tasks(
                    cluster=cluster_arn,
                    desiredStatus='RUNNING'
                )
                running_tasks_count = len(tasks_response.get('taskArns', []))
                
                pending_tasks_response = self.client.list_tasks(
                    cluster=cluster_arn,
                    desiredStatus='PENDING'
                )
                pending_tasks_count = len(pending_tasks_response.get('taskArns', []))
                
                # Get container instances count
                container_instances_response = self.client.list_container_instances(
                    cluster=cluster_arn
                )
                registered_container_instances_count = len(container_instances_response.get('containerInstanceArns', []))
                
                # Create cluster info object
                cluster_info = {
                    "cluster_name": cluster_name,
                    "cluster_arn": cluster_arn,
                    "status": cluster.get('status', 'INACTIVE'),
                    "registered_container_instances_count": registered_container_instances_count,
                    "running_tasks_count": running_tasks_count,
                    "pending_tasks_count": pending_tasks_count
                }
                
                clusters_info.append(cluster_info)
            
            logger.info(f"Successfully listed {len(clusters_info)} ECS clusters")
            return {"clusters": clusters_info}
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS ECS Error: {error_code} - {error_message}")
            return {"error": f"AWS Error: {error_message}"}
        except Exception as e:
            logger.error(f"Unexpected error listing clusters: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    def list_services(self, cluster_name):
        """
        List all services in a specific ECS cluster
        
        Args:
            cluster_name: The name or ARN of the ECS cluster
        
        Returns:
            dict: Dictionary with a 'services' key containing a list of service details
        """
        try:
            logger.debug(f"Listing services for cluster: {cluster_name}")
            
            # List service ARNs
            response = self.client.list_services(
                cluster=cluster_name
            )
            
            service_arns = response.get('serviceArns', [])
            
            if not service_arns:
                logger.info(f"No services found in cluster: {cluster_name}")
                return {"services": []}
            
            # Get detailed information for each service
            services_info = []
            
            # Process services in batches of 10 (AWS API limit)
            for i in range(0, len(service_arns), 10):
                batch = service_arns[i:i+10]
                
                # Describe services to get more details
                describe_response = self.client.describe_services(
                    cluster=cluster_name,
                    services=batch
                )
                
                for service in describe_response.get('services', []):
                    # Extract service details
                    service_name = service.get('serviceName', '')
                    service_arn = service.get('serviceArn', '')
                    
                    # Determine deployment status
                    deployment_status = "NONE"
                    if service.get('deployments'):
                        primary_deployment = next(
                            (d for d in service['deployments'] if d.get('status') == 'PRIMARY'), 
                            None
                        )
                        if primary_deployment:
                            deployment_status = "PRIMARY"
                    
                    # Create service info object
                    service_info = {
                        "service_name": service_name,
                        "service_arn": service_arn,
                        "status": service.get('status', 'INACTIVE'),
                        "desired_count": service.get('desiredCount', 0),
                        "running_count": service.get('runningCount', 0),
                        "pending_count": service.get('pendingCount', 0),
                        "deployment_status": deployment_status
                    }
                    
                    services_info.append(service_info)
            
            logger.info(f"Successfully listed {len(services_info)} services for cluster {cluster_name}")
            return {"services": services_info}
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS ECS Error: {error_code} - {error_message}")
            return {"error": f"AWS Error: {error_message}"}
        except Exception as e:
            logger.error(f"Unexpected error listing services: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    def get_cluster_details(self, cluster_name):
        """
        Get detailed information about a specific ECS cluster
        
        Args:
            cluster_name: The name or ARN of the ECS cluster
        
        Returns:
            dict: Detailed information about the cluster
        """
        try:
            logger.debug(f"Getting details for cluster: {cluster_name}")
            
            # Describe the cluster
            response = self.client.describe_clusters(
                clusters=[cluster_name],
                include=['SETTINGS', 'STATISTICS', 'TAGS']
            )
            
            clusters = response.get('clusters', [])
            
            if not clusters:
                logger.warning(f"Cluster not found: {cluster_name}")
                return {"error": f"Cluster not found: {cluster_name}"}
            
            cluster = clusters[0]
            
            # Extract cluster name from ARN if needed
            cluster_arn = cluster.get('clusterArn', '')
            extracted_name = cluster.get('clusterName', '') or cluster_arn.split('/')[-1]
            
            # List services in the cluster
            services_response = self.client.list_services(
                cluster=cluster_name
            )
            services = services_response.get('serviceArns', [])
            
            # Create cluster details object
            details = {
                "name": extracted_name,
                "status": cluster.get('status', 'INACTIVE'),
                "serviceCount": len(services)
            }
            
            logger.info(f"Successfully retrieved details for cluster: {cluster_name}")
            return details
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS ECS Error: {error_code} - {error_message}")
            return {"error": f"AWS Error: {error_message}"}
        except Exception as e:
            logger.error(f"Unexpected error getting cluster details: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}