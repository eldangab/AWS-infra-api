# app/services/ebs_service.py
import boto3
import logging
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class EBSService:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region):
        """
        Initialize the EBS service with AWS credentials
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region: AWS region
        """
        # Initialize EC2 client for EBS operations
        self.ec2_client = boto3.client(
            'ec2',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region
        )
        
        # Initialize CloudWatch client for metrics
        self.cloudwatch_client = boto3.client(
            'cloudwatch',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region
        )
        
        self.region = region
        logger.debug(f"Initialized EBS service for region {region}")

    def list_volumes(self):
        """
        List all EBS volumes with detailed information
        
        Returns:
            dict: Dictionary with a 'volumes' key containing a list of volume details
        """
        try:
            logger.debug("Attempting to list EBS volumes")
            
            # Get all volumes
            response = self.ec2_client.describe_volumes()
            
            volumes_info = []
            for volume in response.get('Volumes', []):
                # Extract volume details
                volume_id = volume.get('VolumeId', '')
                size = volume.get('Size', 0)
                volume_type = volume.get('VolumeType', '')
                state = volume.get('State', '')
                iops = volume.get('Iops', 0)
                throughput = volume.get('Throughput', 0)
                encrypted = volume.get('Encrypted', False)
                availability_zone = volume.get('AvailabilityZone', '')
                
                # Extract attachment information if available
                attached_instance = ''
                device = ''
                
                if volume.get('Attachments'):
                    attachment = volume['Attachments'][0]  # Get first attachment
                    attached_instance = attachment.get('InstanceId', '')
                    device = attachment.get('Device', '')
                
                # Create volume info object
                volume_info = {
                    "volume_id": volume_id,
                    "size": size,
                    "volume_type": volume_type,
                    "state": state,
                    "iops": iops,
                    "throughput": throughput,
                    "attached_instance": attached_instance,
                    "device": device,
                    "availability_zone": availability_zone,
                    "encrypted": encrypted
                }
                
                volumes_info.append(volume_info)
            
            logger.info(f"Successfully listed {len(volumes_info)} EBS volumes")
            return {"volumes": volumes_info}
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS EC2 Error: {error_code} - {error_message}")
            return {"error": f"AWS Error: {error_message}"}
        except Exception as e:
            logger.error(f"Unexpected error listing volumes: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    def get_volume_metrics(self, volume_id, period=3600, start_time=None, end_time=None):
        """
        Get CloudWatch metrics for a specific EBS volume
        
        Args:
            volume_id: The ID of the EBS volume
            period: Time period in seconds (default: 1 hour)
            start_time: Start time for metrics (default: 24 hours ago)
            end_time: End time for metrics (default: now)
            
        Returns:
            dict: Dictionary with volume metrics
        """
        try:
            logger.debug(f"Getting metrics for volume: {volume_id}")
            
            # Set default time range if not provided
            if end_time is None:
                end_time = datetime.utcnow()
            if start_time is None:
                start_time = end_time - timedelta(hours=24)
                
            # Convert datetime objects to strings if needed
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            # Define metrics to retrieve
            metric_names = {
                'VolumeReadOps': 'read_ops',
                'VolumeWriteOps': 'write_ops',
                'VolumeReadBytes': 'read_bytes',
                'VolumeWriteBytes': 'write_bytes',
                'VolumeQueueLength': 'queue_length'
            }
            
            metrics_data = {}
            
            # Fetch each metric
            for aws_metric_name, api_metric_name in metric_names.items():
                try:
                    response = self.cloudwatch_client.get_metric_data(
                        MetricDataQueries=[
                            {
                                'Id': 'metric1',
                                'MetricStat': {
                                    'Metric': {
                                        'Namespace': 'AWS/EBS',
                                        'MetricName': aws_metric_name,
                                        'Dimensions': [
                                            {
                                                'Name': 'VolumeId',
                                                'Value': volume_id
                                            }
                                        ]
                                    },
                                    'Period': period,
                                    'Stat': 'Average'
                                },
                                'ReturnData': True
                            }
                        ],
                        StartTime=start_time,
                        EndTime=end_time
                    )
                    
                    # Format response data
                    formatted_data = []
                    timestamps = response['MetricDataResults'][0]['Timestamps']
                    values = response['MetricDataResults'][0]['Values']
                    
                    for i in range(len(timestamps)):
                        formatted_data.append({
                            'timestamp': timestamps[i].isoformat() + 'Z',
                            'value': values[i]
                        })
                    
                    metrics_data[api_metric_name] = formatted_data
                    
                except Exception as e:
                    logger.warning(f"Error retrieving metric {aws_metric_name}: {str(e)}")
                    metrics_data[api_metric_name] = []
            
            # Verify volume exists
            try:
                self.ec2_client.describe_volumes(VolumeIds=[volume_id])
            except ClientError:
                return {"error": f"Volume {volume_id} not found"}
            
            result = {
                'volume_id': volume_id,
                'metrics': metrics_data
            }
            
            logger.info(f"Successfully retrieved metrics for volume {volume_id}")
            return result
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS Error for volume {volume_id}: {error_code} - {error_message}")
            return {"error": f"AWS Error: {error_message}"}
        except Exception as e:
            logger.error(f"Unexpected error getting volume metrics: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}