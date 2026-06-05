"""Unified error handlers."""
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError

def register_error_handlers(app: Flask):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'code': 400, 'message': str(e.description) if hasattr(e, 'description') else '请求参数错误'}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'code': 401, 'message': '未授权，请先登录'}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'code': 403, 'message': '没有访问权限'}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'code': 404, 'message': '资源不存在'}), 404

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({'code': 429, 'message': '请求过于频繁'}), 429

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

    @app.errorhandler(ValidationError)
    def validation_error(e):
        return jsonify({'code': 422, 'message': '数据验证失败', 'errors': e.messages}), 422
