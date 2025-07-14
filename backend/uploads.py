import os
from flask import Blueprint, send_from_directory

uploads_bp = Blueprint('uploads', __name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@uploads_bp.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory('uploads', filename, as_attachment=True)