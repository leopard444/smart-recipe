"""Decorators for auth, admin, and rate limiting."""
from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.services.cache_service import CacheService
from app.extensions import get_redis


def login_required(f):
    """Require valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        g.user_id = int(get_jwt_identity())
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Require admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'code': 403, 'message': '需要管理员权限'}), 403
        g.user_id = int(get_jwt_identity())
        return f(*args, **kwargs)
    return decorated


def optional_auth(f):
    """Try to parse JWT but don't require it."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            g.user_id = int(identity) if identity else None
        except Exception:
            g.user_id = None
        return f(*args, **kwargs)
    return decorated


def rate_limit(action: str, max_req: int = 20, window: int = 60):
    """Rate limit decorator using Redis."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            redis = get_redis()
            if not redis:
                return f(*args, **kwargs)

            # Use user ID or IP as identifier
            identifier = str(getattr(g, 'user_id', None) or request.remote_addr or 'anonymous')
            cache = CacheService(redis)

            if not cache.check_rate_limit(identifier, action, max_req, window):
                remaining = cache.get_rate_limit_remaining(identifier, action, max_req)
                return jsonify({
                    'code': 429,
                    'message': f'请求过于频繁，请在 {window} 秒后重试',
                    'retry_after': 60,
                    'remaining': remaining,
                }), 429

            return f(*args, **kwargs)
        return decorated
    return decorator
