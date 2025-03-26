# app/services/dashboard_service.py
import logging
from app.services.s3_service import S3Service
from app.services.ecs_service import ECSService
from app.services.ebs_service import EBSService

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region):
        """
        Initialize the Dashboard service with AWS credentials
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region: AWS region
        """
        # Initialize service clients
        self.s3_service = S3Service(aws_access_key_id, aws_secret_access_key, region)
        self.ecs_service = ECSService(aws_access_key_id, aws_secret_access_key, region)
        self.ebs_service = EBSService(aws_access_key_id, aws_secret_access_key, region)
        
        self.region = region
        logger.debug(f"Initialized Dashboard service for region {region}")

    def get_summary(self):
        """
        Get comprehensive summary of all AWS resources
        
        Returns:
            dict: Summary of ECS, S3, and EBS resources
        """
        try:
            logger.debug("Generating dashboard summary")
            
            # Get ECS summary
            ecs_summary = self._get_ecs_summary()
            
            # Get S3 summary
            s3_summary = self._get_s3_summary()
            
            # Get EBS summary
            ebs_summary = self._get_ebs_summary()
            
            # Combine all summaries
            summary = {
                "summary": {
                    "ecs": ecs_summary,
                    "s3": s3_summary,
                    "ebs": ebs_summary
                }
            }
            
            logger.info("Successfully generated dashboard summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {str(e)}")
            return {"error": f"Failed to generate summary: {str(e)}"}

    def _get_ecs_summary(self):
        """
        Get summary of ECS resources
        
        Returns:
            dict: ECS summary metrics
        """
        try:
            # Get clusters
            clusters_response = self.ecs_service.list_clusters()
            clusters = clusters_response.get('clusters', [])
            
            total_clusters = len(clusters)
            total_services = 0
            total_tasks = 0
            unhealthy_services = 0
            
            # Get services and tasks for each cluster
            for cluster in clusters:
                cluster_name = cluster if isinstance(cluster, str) else cluster.get('cluster_name', '')
                
                # Extract cluster name from ARN if needed
                if cluster_name.startswith('arn:'):
                    cluster_name = cluster_name.split('/')[-1]
                
                # Get services for this cluster
                services_response = self.ecs_service.list_services(cluster_name)
                services = services_response.get('services', [])
                total_services += len(services)
                
                # Check for unhealthy services and count tasks
                for service in services:
                    # This is a simplified approach; in a real implementation,
                    # you would check service health and count tasks
                    if isinstance(service, dict):
                        if service.get('status') != 'ACTIVE':
                            unhealthy_services += 1
                        total_tasks += service.get('running_count', 0) + service.get('pending_count', 0)
                    
            return {
                "total_clusters": total_clusters,
                "total_services": total_services,
                "total_tasks": total_tasks,
                "unhealthy_services": unhealthy_services
            }
            
        except Exception as e:
            logger.error(f"Error generating ECS summary: {str(e)}")
            return {
                "total_clusters": 0,
                "total_services": 0,
                "total_tasks": 0,
                "unhealthy_services": 0
            }

    def _get_s3_summary(self):
        """
        Get summary of S3 resources
        
        Returns:
            dict: S3 summary metrics
        """
        try:
            # Get buckets
            buckets_response = self.s3_service.list_buckets()
            buckets = buckets_response.get('buckets', [])
            
            total_buckets = len(buckets)
            total_storage_gb = 0
            buckets_without_encryption = 0
            publicly_accessible_buckets = 0
            
            # Process bucket details
            for bucket in buckets:
                # Get bucket details
                bucket_name = bucket.get('name') if isinstance(bucket, dict) else bucket
                bucket_details = self.s3_service.get_bucket_details(bucket_name)
                
                # Get storage size
                storage_class_summary = bucket_details.get('storage_class_summary', {})
                for storage_class, size_bytes in storage_class_summary.items():
                    total_storage_gb += size_bytes / (1024 * 1024 * 1024)
                
                # Check encryption
                encryption = bucket_details.get('encryption', {})
                if not encryption.get('enabled', False):
                    buckets_without_encryption += 1
                
                # Check public access (simplified)
                # In a real implementation, you'd check bucket policies and ACLs
                publicly_accessible_buckets += 0  # Placeholder
            
            # Round total storage to 2 decimal places
            total_storage_gb = round(total_storage_gb, 2)
            
            return {
                "total_buckets": total_buckets,
                "total_storage_gb": total_storage_gb,
                "buckets_without_encryption": buckets_without_encryption,
                "publicly_accessible_buckets": publicly_accessible_buckets
            }
            
        except Exception as e:
            logger.error(f"Error generating S3 summary: {str(e)}")
            return {
                "total_buckets": 0,
                "total_storage_gb": 0,
                "buckets_without_encryption": 0,
                "publicly_accessible_buckets": 0
            }

    def _get_ebs_summary(self):
        """
        Get summary of EBS resources
        
        Returns:
            dict: EBS summary metrics
        """
        try:
            # Get volumes
            volumes_response = self.ebs_service.list_volumes()
            volumes = volumes_response.get('volumes', [])
            
            total_volumes = len(volumes)
            total_storage_gb = 0
            unattached_volumes = 0
            unencrypted_volumes = 0
            
            # Process volume details
            for volume in volumes:
                # Get storage size
                total_storage_gb += volume.get('size', 0)
                
                # Check if volume is attached
                if volume.get('state') != 'in-use' or not volume.get('attached_instance'):
                    unattached_volumes += 1
                
                # Check encryption
                if not volume.get('encrypted', False):
                    unencrypted_volumes += 1
            
            return {
                "total_volumes": total_volumes,
                "total_storage_gb": total_storage_gb,
                "unattached_volumes": unattached_volumes,
                "unencrypted_volumes": unencrypted_volumes
            }
            
        except Exception as e:
            logger.error(f"Error generating EBS summary: {str(e)}")
            return {
                "total_volumes": 0,
                "total_storage_gb": 0,
                "unattached_volumes": 0,
                "unencrypted_volumes": 0
            }