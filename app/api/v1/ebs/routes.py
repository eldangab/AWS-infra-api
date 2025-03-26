# app/api/v1/ebs/routes.py
from flask import Blueprint, request
from flask_restful import Api, Resource
from app.services.ebs_service import EBSService
from app.utils.auth_utils import AuthUtils
from datetime import datetime, timedelta

ebs_bp = Blueprint('ebs', __name__)
api = Api(ebs_bp)

class EBSVolumesResource(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        
        try:
            # Validate the token
            payload = AuthUtils.validate_token(token)
            
            # Create EBS Service with credentials from token
            ebs_service = EBSService(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            # List EBS Volumes
            volumes = ebs_service.list_volumes()
            
            # Check if an error occurred
            if isinstance(volumes, dict) and 'error' in volumes:
                return volumes, 400
                
            return {'volumes': volumes}, 200
        
        except ValueError as e:
            return {'error': str(e)}, 401

class EBSVolumeMetricsResource(Resource):
    def get(self, volume_id):
        token = request.headers.get('Authorization')
        
        try:
            # Validate the token
            payload = AuthUtils.validate_token(token)
            
            # Parse query parameters with defaults
            period = request.args.get('period', default=3600, type=int)
            
            # Handle time parameters
            now = datetime.utcnow()
            default_start = (now - timedelta(hours=24)).isoformat()
            
            start_time = request.args.get('start_time', default=default_start)
            end_time = request.args.get('end_time', default=now.isoformat())
            
            # Create EBS Service with credentials from token
            ebs_service = EBSService(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            # Get volume metrics
            metrics = ebs_service.get_volume_metrics(
                volume_id=volume_id,
                period=period,
                start_time=start_time,
                end_time=end_time
            )
            
            # Check if an error occurred
            if isinstance(metrics, dict) and 'error' in metrics:
                return metrics, 400
                
            return metrics, 200
        
        except ValueError as e:
            return {'error': str(e)}, 401

# Register resources with API endpoints
api.add_resource(EBSVolumesResource, '/volumes')
api.add_resource(EBSVolumeMetricsResource, '/volumes/<string:volume_id>/metrics')