from flask import render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
from app import app, db
from models import Dataset, DataRecord
from utils import allowed_file, create_api_endpoints
import os

@app.route('/')
def index():
    datasets = Dataset.query.all()
    return render_template('index.html', datasets=datasets)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Read CSV
        df = pd.read_csv(file)
        
        # Create dataset
        dataset = Dataset(name=filename)
        db.session.add(dataset)
        db.session.flush()
        
        # Store records
        for _, row in df.iterrows():
            record = DataRecord(
                dataset_id=dataset.id,
                data=row.to_dict()
            )
            db.session.add(record)
        
        db.session.commit()
        create_api_endpoints(app, dataset)
        
        flash('File successfully uploaded')
        return redirect(url_for('index'))

@app.route('/docs')
def documentation():
    datasets = Dataset.query.all()
    return render_template('documentation.html', datasets=datasets)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
