"""File upload API endpoints."""
from flask import Blueprint, request, jsonify, g
from app.services.upload_service import UploadService
from app.utils.decorators import login_required

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/image', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '请选择文件'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'code': 400, 'message': '请选择文件'}), 400

    url, error = UploadService.save_image(file, 'recipes')
    if error:
        return jsonify({'code': 400, 'message': error}), 400

    return jsonify({
        'code': 200,
        'message': '上传成功',
        'data': {'url': url},
    }), 200


@upload_bp.route('/image/<path:filename>', methods=['DELETE'])
@login_required
def delete_image(filename: str):
    filepath = f'/uploads/recipes/{filename}'
    success = UploadService.delete_image(filepath)
    if success:
        return jsonify({'code': 200, 'message': '已删除'}), 200
    return jsonify({'code': 404, 'message': '文件不存在'}), 404
