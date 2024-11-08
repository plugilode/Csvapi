from flask import jsonify, request
from models import DataRecord
from sqlalchemy import desc
import re

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_query_parameters(query, dataset_records, dataset_id):
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Sorting parameters
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', 'asc')
    
    # Search parameter
    search = request.args.get('search')
    
    # Apply filtering based on column values
    for key, value in request.args.items():
        if key not in ['page', 'per_page', 'sort_by', 'sort_order', 'search']:
            query = query.filter(DataRecord.data[key].astext == value)
    
    # Apply search across all columns if search parameter is provided
    if search:
        search_conditions = []
        sample_record = dataset_records.first()
        if sample_record:
            for column in sample_record.data.keys():
                search_conditions.append(
                    DataRecord.data[column].astext.ilike(f'%{search}%')
                )
            from sqlalchemy import or_
            query = query.filter(or_(*search_conditions))
    
    # Apply sorting if sort_by parameter is provided
    if sort_by:
        sort_expr = DataRecord.data[sort_by].astext
        if sort_order.lower() == 'desc':
            sort_expr = desc(sort_expr)
        query = query.order_by(sort_expr)
    
    # Apply pagination
    paginated_query = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepare response metadata
    total_pages = paginated_query.pages
    total_records = paginated_query.total
    
    return {
        'data': [record.data for record in paginated_query.items],
        'metadata': {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_records': total_records
        }
    }

def create_api_endpoints(app, dataset):
    @app.route(f'/api/v1/{dataset.id}/data', methods=['GET'])
    def get_dataset_data(dataset_id=dataset.id):
        dataset_records = DataRecord.query.filter_by(dataset_id=dataset_id)
        base_query = DataRecord.query.filter_by(dataset_id=dataset_id)
        result = process_query_parameters(base_query, dataset_records, dataset_id)
        return jsonify(result)

    @app.route(f'/api/v1/{dataset.id}/data/<int:record_id>', methods=['GET'])
    def get_record(dataset_id=dataset.id, record_id=None):
        record = DataRecord.query.filter_by(dataset_id=dataset_id, id=record_id).first_or_404()
        return jsonify(record.data)

def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
