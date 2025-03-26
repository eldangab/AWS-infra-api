from flask import Blueprint, jsonify
from app.services.s3_service import S3Service
from app.services.ecs_service import ECSService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview')
def dashboard_overview():
    # Placeholder for dashboard data aggregation
    s3_data = {
        'total_buckets': len(s3_service.list_buckets()),
        'storage_utilization': 'TBD'
    }
    ecs_data = {
        'total_clusters': len(ecs_service.list_clusters()),
        'running_services': 'TBD'
    }
    
    return jsonify({
        's3': s3_data,
        'ecs': ecs_data
    })