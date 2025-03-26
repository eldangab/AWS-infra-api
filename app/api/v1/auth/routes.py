# app/api/v1/auth/routes.py
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.utils.auth_utils import AuthUtils

auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp)

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        
        # Check if all required fields are present
        if not data or 'aws_access_key_id' not in data or 'aws_secret_access_key' not in data:
            return {'error': 'Missing required credentials'}, 400
        
        # Extract credentials from request
        aws_access_key_id = data['aws_access_key_id']
        aws_secret_access_key = data['aws_secret_access_key']
        aws_region = data.get('aws_region', 'us-west-2')  # Default to us-west-2 if not provided
        
        try:
            # Generate token with all required parameters
            token_info = AuthUtils.generate_token(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_region=aws_region
            )
            # Return dictionary directly, not wrapped in jsonify
            return token_info, 200
        except ValueError as e:
            return {'error': str(e)}, 401

api.add_resource(LoginResource, '/login')