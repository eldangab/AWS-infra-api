# app/services/s3_service.py
import boto3
import logging
from botocore.exceptions import ClientError
from datetime import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region):
        # Initialize the main S3 client
        self.client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region
        )
        
        # Initialize the S3 resource for higher-level operations
        self.resource = boto3.resource(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region
        )
        
        self.region = region
        logger.debug(f"Initialized S3 service for region {region}")

    def list_buckets(self):
        """
        List all S3 buckets with detailed information
        
        Returns:
            dict: Dictionary with a 'buckets' key containing a list of bucket details
        """
        try:
            logger.debug("Attempting to list S3 buckets with detailed information")
            response = self.client.list_buckets()
            buckets_info = []
            
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                creation_date = bucket['CreationDate'].isoformat() + 'Z'
                
                # Get additional bucket details
                try:
                    # Get bucket location/region
                    try:
                        location_response = self.client.get_bucket_location(Bucket=bucket_name)
                        region = location_response.get('LocationConstraint')
                        # None represents us-east-1 in the API response
                        if region is None:
                            region = 'us-east-1'
                    except ClientError:
                        region = self.region
                    
                    # Get bucket versioning status
                    try:
                        versioning_response = self.client.get_bucket_versioning(Bucket=bucket_name)
                        versioning_enabled = versioning_response.get('Status') == 'Enabled'
                    except ClientError:
                        versioning_enabled = False
                    
                    # Get public access block configuration
                    try:
                        public_access_response = self.client.get_public_access_block(Bucket=bucket_name)
                        block_config = public_access_response.get('PublicAccessBlockConfiguration', {})
                        public_access_blocked = (
                            block_config.get('BlockPublicAcls', False) and
                            block_config.get('IgnorePublicAcls', False) and
                            block_config.get('BlockPublicPolicy', False) and
                            block_config.get('RestrictPublicBuckets', False)
                        )
                    except ClientError:
                        public_access_blocked = False
                    
                    # Get object count and total size (this can be resource-intensive)
                    object_count = 0
                    total_size_bytes = 0
                    
                    try:
                        # For performance reasons, limit the count to a reasonable number
                        bucket_obj = self.resource.Bucket(bucket_name)
                        MAX_OBJECTS = 1000  # Set a reasonable limit
                        
                        # Count objects up to the limit
                        for i, obj in enumerate(bucket_obj.objects.limit(MAX_OBJECTS + 1)):
                            if i >= MAX_OBJECTS:
                                object_count = f"{MAX_OBJECTS}+"
                                break
                            else:
                                object_count += 1
                                total_size_bytes += obj.size
                    except ClientError:
                        # Continue with zero counts if there's an error
                        pass
                    
                    # Create bucket info object
                    bucket_info = {
                        "name": bucket_name,
                        "creation_date": creation_date,
                        "region": region,
                        "object_count": object_count,
                        "total_size_bytes": total_size_bytes,
                        "versioning_enabled": versioning_enabled,
                        "public_access_blocked": public_access_blocked
                    }
                    
                    buckets_info.append(bucket_info)
                    
                except Exception as e:
                    logger.error(f"Error getting details for bucket {bucket_name}: {str(e)}")
                    # Add bucket with minimal information if we encounter an error
                    buckets_info.append({
                        "name": bucket_name,
                        "creation_date": creation_date,
                        "region": self.region,
                        "object_count": 0,
                        "total_size_bytes": 0,
                        "versioning_enabled": False,
                        "public_access_blocked": False
                    })
            
            logger.info(f"Successfully listed {len(buckets_info)} S3 buckets with details")
            return {"buckets": buckets_info}
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS S3 Error: {error_code} - {error_message}")
            return {"error": f"AWS Error: {error_message}"}
        except Exception as e:
            logger.error(f"Unexpected error listing buckets: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    def get_bucket_details(self, bucket_name):
        """
        Get detailed information about a specific S3 bucket
        
        Args:
            bucket_name: The name of the S3 bucket
        
        Returns:
            dict: Detailed information about the bucket
        """
        try:
            logger.debug(f"Getting details for bucket: {bucket_name}")
            
            # Get basic bucket information
            response = self.client.list_buckets()
            creation_date = None
            
            for bucket in response.get('Buckets', []):
                if bucket['Name'] == bucket_name:
                    creation_date = bucket['CreationDate'].isoformat() + 'Z'
                    break
            
            if not creation_date:
                logger.warning(f"Could not find creation date for bucket: {bucket_name}")
                creation_date = datetime.now().isoformat() + 'Z'
            
            # Get bucket location/region
            try:
                location_response = self.client.get_bucket_location(Bucket=bucket_name)
                region = location_response.get('LocationConstraint')
                # None represents us-east-1 in the API response
                if region is None:
                    region = 'us-east-1'
            except ClientError as e:
                logger.warning(f"Error getting bucket location: {str(e)}")
                region = self.region  # Default to the service region
            
            # Get storage class summary
            storage_class_summary = self._get_storage_class_summary(bucket_name)
            
            # Get lifecycle rules
            lifecycle_rules = self._get_lifecycle_rules(bucket_name)
            
            # Get encryption settings
            encryption_settings = self._get_encryption_settings(bucket_name)
            
            # Compile and return bucket details
            details = {
                "name": bucket_name,
                "creation_date": creation_date,
                "region": region,
                "storage_class_summary": storage_class_summary,
                "lifecycle_rules": lifecycle_rules,
                "encryption": encryption_settings
            }
            
            logger.info(f"Successfully retrieved details for bucket: {bucket_name}")
            return details
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS S3 Error for bucket {bucket_name}: {error_code} - {error_message}")
            return {"error": f"AWS Error: {error_message}"}
        except Exception as e:
            logger.error(f"Unexpected error getting details for bucket {bucket_name}: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}
    
    def _get_storage_class_summary(self, bucket_name):
        """
        Get summary of storage classes used in the bucket
        
        Args:
            bucket_name: The name of the S3 bucket
            
        Returns:
            dict: Summary of storage classes and their sizes in bytes
        """
        try:
            # Initialize storage class summary
            storage_summary = defaultdict(int)
            
            # Get bucket objects
            bucket = self.resource.Bucket(bucket_name)
            
            # Limit to a reasonable number for performance
            for obj in bucket.objects.limit(1000):
                # Get object's storage class
                storage_class = getattr(obj, 'storage_class', 'STANDARD')
                if not storage_class:
                    storage_class = 'STANDARD'  # Default if not specified
                
                # Add object size to corresponding storage class
                storage_summary[storage_class] += obj.size
            
            # Convert defaultdict to regular dict
            return dict(storage_summary)
        except Exception as e:
            logger.warning(f"Error getting storage class summary for bucket {bucket_name}: {str(e)}")
            # Return default storage class summary
            return {"STANDARD": 0}
    
    def _get_lifecycle_rules(self, bucket_name):
        """
        Get lifecycle rules for the bucket
        
        Args:
            bucket_name: The name of the S3 bucket
            
        Returns:
            list: Lifecycle rules
        """
        try:
            response = self.client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            
            # Extract and format lifecycle rules
            rules = []
            for rule in response.get('Rules', []):
                formatted_rule = {
                    "id": rule.get('ID', 'Unknown'),
                    "status": rule.get('Status', 'Disabled')
                }
                
                # Extract transitions
                transitions = []
                for transition in rule.get('Transitions', []):
                    transitions.append({
                        "days": transition.get('Days', 0),
                        "storage_class": transition.get('StorageClass', 'STANDARD')
                    })
                
                if transitions:
                    formatted_rule["transitions"] = transitions
                
                rules.append(formatted_rule)
            
            return rules
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                logger.info(f"No lifecycle rules configured for bucket {bucket_name}")
                return []
            else:
                logger.warning(f"Error getting lifecycle rules for bucket {bucket_name}: {str(e)}")
                return []
    
    def _get_encryption_settings(self, bucket_name):
        """
        Get encryption settings for the bucket
        
        Args:
            bucket_name: The name of the S3 bucket
            
        Returns:
            dict: Encryption settings
        """
        try:
            response = self.client.get_bucket_encryption(Bucket=bucket_name)
            encryption_config = response.get('ServerSideEncryptionConfiguration', {})
            
            # Extract encryption rules
            rules = encryption_config.get('Rules', [])
            if rules and 'ApplyServerSideEncryptionByDefault' in rules[0]:
                default_encryption = rules[0]['ApplyServerSideEncryptionByDefault']
                encryption_type = default_encryption.get('SSEAlgorithm', 'Unknown')
                
                return {
                    "enabled": True,
                    "type": encryption_type
                }
            else:
                return {
                    "enabled": False,
                    "type": None
                }
        except ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                logger.info(f"No encryption configured for bucket {bucket_name}")
                return {"enabled": False, "type": None}
            else:
                logger.warning(f"Error getting encryption settings for bucket {bucket_name}: {str(e)}")
                return {"enabled": False, "type": None}