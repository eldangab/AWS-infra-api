# app/api/v1/s3/routes.py
from flask import Blueprint, request
from flask_restful import Api, Resource
from app.services.s3_service import S3Service
from app.utils.auth_utils import AuthUtils

s3_bp = Blueprint('s3', __name__)
api = Api(s3_bp)

class S3BucketsResource(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        
        try:
            # Validate the token
            payload = AuthUtils.validate_token(token)
            
            # Create S3 Service with credentials from token
            s3_service = S3Service(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            # List S3 Buckets - return directly, no jsonify
            buckets = s3_service.list_buckets()
            return {'buckets': buckets}, 200
        
        except ValueError as e:
            return {'error': str(e)}, 401

class S3BucketDetailsResource(Resource):
    def get(self, bucket_name):
        token = request.headers.get('Authorization')
        
        try:
            # Validate the token
            payload = AuthUtils.validate_token(token)
            
            # Create S3 Service with credentials from token
            s3_service = S3Service(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            # Get Bucket Details - return directly, no jsonify
            bucket_details = s3_service.get_bucket_details(bucket_name)
            return bucket_details, 200
        
        except ValueError as e:
            return {'error': str(e)}, 401

# Register resources with API endpoints
api.add_resource(S3BucketsResource, '/buckets')
api.add_resource(S3BucketDetailsResource, '/buckets/<string:bucket_name>/details')