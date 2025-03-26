# app/api/v1/dashboard/routes.py

from flask import Blueprint, request
from flask_restful import Api, Resource
from app.services.s3_service import S3Service
from app.services.ecs_service import ECSService
from app.services.ebs_service import EBSService
from app.services.dashboard_service import DashboardService
from app.utils.auth_utils import AuthUtils

dashboard_bp = Blueprint('dashboard', __name__)
api = Api(dashboard_bp)

class DashboardOverviewResource(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        
        try:
            # Validate the token
            payload = AuthUtils.validate_token(token)
            
            # Create service clients with credentials from token
            s3_service = S3Service(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            ecs_service = ECSService(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            ebs_service = EBSService(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            # Gather S3 insights
            s3_buckets = s3_service.list_buckets()
            s3_details = [s3_service.get_bucket_details(bucket) for bucket in s3_buckets]
            
            # Gather ECS insights
            ecs_clusters = ecs_service.list_clusters()
            ecs_cluster_details = [ecs_service.get_cluster_details(cluster) for cluster in ecs_clusters]
            
            # Gather EBS insights
            ebs_volumes = ebs_service.list_volumes()
            
            # Return dashboard data directly, no jsonify
            return {
                's3': {
                    'total_buckets': len(s3_buckets),
                    'bucket_details': s3_details
                },
                'ecs': {
                    'total_clusters': len(ecs_clusters),
                    'cluster_details': ecs_cluster_details
                },
                'ebs': {
                    'total_volumes': len(ebs_volumes.get('volumes', [])),
                    'volume_details': ebs_volumes.get('volumes', [])
                }
            }, 200
        
        except ValueError as e:
            return {'error': str(e)}, 401

class SecurityInsightsResource(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        
        try:
            # Validate the token
            payload = AuthUtils.validate_token(token)
            
            # Create service clients with credentials from token
            s3_service = S3Service(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            ebs_service = EBSService(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            # Analyze S3 bucket security
            s3_buckets = s3_service.list_buckets()
            s3_security_analysis = []
            
            for bucket in s3_buckets:
                bucket_details = s3_service.get_bucket_details(bucket)
                security_status = {
                    'bucket_name': bucket,
                    'encryption_status': 'Encrypted' if bucket_details.get('encryption', {}).get('enabled', False) else 'Not Encrypted',
                }
                s3_security_analysis.append(security_status)
            
            # Analyze EBS volume security
            ebs_volumes = ebs_service.list_volumes()
            ebs_security_analysis = []
            
            for volume in ebs_volumes.get('volumes', []):
                security_status = {
                    'volume_id': volume.get('volume_id', 'Unknown'),
                    'encryption_status': 'Encrypted' if volume.get('encrypted', False) else 'Not Encrypted',
                }
                ebs_security_analysis.append(security_status)
            
            # Return security insights directly, no jsonify
            return {
                'security_insights': {
                    's3': s3_security_analysis,
                    'ebs': ebs_security_analysis
                }
            }, 200
        
        except ValueError as e:
            return {'error': str(e)}, 401

class DashboardSummaryResource(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        
        try:
            # Validate the token
            payload = AuthUtils.validate_token(token)
            
            # Create dashboard service
            dashboard_service = DashboardService(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            # Get summary
            summary = dashboard_service.get_summary()
            
            return summary, 200
        
        except ValueError as e:
            return {'error': str(e)}, 401

# Register resources with API endpoints
api.add_resource(DashboardOverviewResource, '/overview')
api.add_resource(SecurityInsightsResource, '/security_insights')
api.add_resource(DashboardSummaryResource, '/summary')