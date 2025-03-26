# app/api/v1/ecs/routes.py
from flask import Blueprint, request
from flask_restful import Api, Resource
from app.services.ecs_service import ECSService
from app.utils.auth_utils import AuthUtils

ecs_bp = Blueprint('ecs', __name__)
api = Api(ecs_bp)

class ECSClustersResource(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        
        try:
            # Validate the token
            payload = AuthUtils.validate_token(token)
            
            # Create ECS Service with credentials from token
            ecs_service = ECSService(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            # List ECS Clusters - return directly, no jsonify
            clusters = ecs_service.list_clusters()
            return {'clusters': clusters}, 200
        
        except ValueError as e:
            return {'error': str(e)}, 401

class ECSClusterServicesResource(Resource):
    def get(self, cluster_name):
        token = request.headers.get('Authorization')
        
        try:
            # Validate the token
            payload = AuthUtils.validate_token(token)
            
            # Create ECS Service with credentials from token
            ecs_service = ECSService(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            # List Services for specific cluster - return directly, no jsonify
            services = ecs_service.list_services(cluster_name)
            return {'services': services}, 200
        
        except ValueError as e:
            return {'error': str(e)}, 401

class ECSClusterDetailsResource(Resource):
    def get(self, cluster_name):
        token = request.headers.get('Authorization')
        
        try:
            # Validate the token
            payload = AuthUtils.validate_token(token)
            
            # Create ECS Service with credentials from token
            ecs_service = ECSService(
                aws_access_key_id=payload['aws_access_key_id'],
                aws_secret_access_key=payload['aws_secret_access_key'],
                region=payload.get('aws_region', 'us-west-2')
            )
            
            # Get detailed cluster information - return directly, no jsonify
            cluster_details = ecs_service.get_cluster_details(cluster_name)
            return cluster_details, 200
        
        except ValueError as e:
            return {'error': str(e)}, 401

# Register resources with API endpoints
api.add_resource(ECSClustersResource, '/clusters')
api.add_resource(ECSClusterServicesResource, '/clusters/<string:cluster_name>/services')
api.add_resource(ECSClusterDetailsResource, '/clusters/<string:cluster_name>/details')