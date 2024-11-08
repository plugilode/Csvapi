from flask import jsonify, request
from models import DataRecord
from sqlalchemy import desc, and_, or_, cast, String, Float
import re

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_filter_operator(operator, value):
    operators = {
        'eq': lambda field: field.astext == str(value),
        'gt': lambda field: cast(field.astext, Float) > float(value),
        'lt': lambda field: cast(field.astext, Float) < float(value),
        'gte': lambda field: cast(field.astext, Float) >= float(value),
        'lte': lambda field: cast(field.astext, Float) <= float(value),
        'contains': lambda field: field.astext.ilike(f'%{value}%'),
        'startswith': lambda field: field.astext.ilike(f'{value}%'),
        'endswith': lambda field: field.astext.ilike(f'%{value}'),
    }
    return operators.get(operator, operators['eq'])

def process_query_parameters(query, dataset_records, dataset_id):
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Multiple sort fields support
    sort_fields = request.args.getlist('sort_by')
    sort_orders = request.args.getlist('sort_order')
    
    # Field selection
    fields = request.args.getlist('fields')
    
    # Search parameter
    search = request.args.get('search')
    
    # Apply advanced filtering
    filter_conditions = []
    for key, value in request.args.items():
        # Skip special parameters
        if key in ['page', 'per_page', 'sort_by', 'sort_order', 'search', 'fields']:
            continue
            
        # Handle advanced operators (e.g., column__gt=5, column__contains=text)
        if '__' in key:
            field, operator = key.split('__')
            try:
                filter_op = get_filter_operator(operator, value)
                filter_conditions.append(filter_op(DataRecord.data[field]))
            except (ValueError, TypeError):
                continue
        else:
            # Default exact match
            filter_conditions.append(DataRecord.data[key].astext == value)
    
    if filter_conditions:
        query = query.filter(and_(*filter_conditions))
    
    # Apply search across all columns if search parameter is provided
    if search:
        search_conditions = []
        sample_record = dataset_records.first()
        if sample_record:
            for column in sample_record.data.keys():
                search_conditions.append(
                    DataRecord.data[column].astext.ilike(f'%{search}%')
                )
            query = query.filter(or_(*search_conditions))
    
    # Apply multiple sorting
    if sort_fields:
        sort_expressions = []
        for idx, sort_field in enumerate(sort_fields):
            sort_order = sort_orders[idx] if idx < len(sort_orders) else 'asc'
            sort_expr = DataRecord.data[sort_field].astext
            if sort_order.lower() == 'desc':
                sort_expr = desc(sort_expr)
            sort_expressions.append(sort_expr)
        if sort_expressions:
            query = query.order_by(*sort_expressions)
    
    # Apply pagination
    paginated_query = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepare response data with field selection
    data = []
    for record in paginated_query.items:
        if fields:
            # Only include requested fields
            filtered_data = {field: record.data.get(field) for field in fields if field in record.data}
            data.append(filtered_data)
        else:
            data.append(record.data)
    
    # Prepare response metadata
    total_pages = paginated_query.pages
    total_records = paginated_query.total
    
    return {
        'data': data,
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
