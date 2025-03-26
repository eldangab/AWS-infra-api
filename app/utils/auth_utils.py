# app/utils/auth_utils.py
import jwt
import datetime
import boto3
import logging
from botocore.exceptions import ClientError
from flask import current_app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AuthUtils:
    @staticmethod
    def generate_token(aws_access_key_id, aws_secret_access_key, aws_region='us-west-2'):
        try:
            # Detailed credential validation
            logger.debug(f"Attempting to validate AWS credentials for access key: {aws_access_key_id}")
            
            # Create STS client with provided credentials
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region
            )
            
            try:
                # Attempt to get caller identity to validate credentials
                caller_identity = sts_client.get_caller_identity()
                logger.info(f"Credentials validated successfully. Account ID: {caller_identity['Account']}")
            except ClientError as e:
                # Log specific error details
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']
                logger.error(f"AWS Credential Validation Failed: {error_code} - {error_message}")
                raise ValueError(f"AWS Credential Validation Failed: {error_message}")
            
            # Generate token with full credential information
            expiration = datetime.datetime.utcnow() + datetime.timedelta(
                minutes=current_app.config['TOKEN_EXPIRATION_MINUTES']
            )
            
            token_payload = {
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key,
                'aws_region': aws_region,
                'exp': expiration
            }
            
            token = jwt.encode(
                token_payload, 
                current_app.config['JWT_SECRET_KEY'], 
                algorithm='HS256'
            )
            
            return {
                'token': token,
                'expires_at': expiration.isoformat() + 'Z'
            }
        
        except Exception as e:
            logger.error(f"Token generation failed: {str(e)}")
            raise ValueError(f"Authentication failed: {str(e)}")

    @staticmethod
    def validate_token(token):
        try:
            payload = jwt.decode(
                token, 
                current_app.config['JWT_SECRET_KEY'], 
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            raise ValueError("Invalid token")