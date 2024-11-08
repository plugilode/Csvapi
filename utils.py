from flask import jsonify
from models import DataRecord
import re

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_api_endpoints(app, dataset):
    @app.route(f'/api/v1/{dataset.id}/data', methods=['GET'])
    def get_dataset_data(dataset_id=dataset.id):
        records = DataRecord.query.filter_by(dataset_id=dataset_id).all()
        return jsonify([record.data for record in records])

    @app.route(f'/api/v1/{dataset.id}/data/<int:record_id>', methods=['GET'])
    def get_record(dataset_id=dataset.id, record_id=None):
        record = DataRecord.query.filter_by(dataset_id=dataset_id, id=record_id).first_or_404()
        return jsonify(record.data)

def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
