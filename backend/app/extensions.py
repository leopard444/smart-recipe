from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import redis

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
redis_client: redis.Redis | None = None

def init_redis(app):
    global redis_client
    redis_client = redis.Redis.from_url(
        app.config['REDIS_URL'],
        decode_responses=True,  # Auto-decode to Python str
    )
    return redis_client

def get_redis() -> redis.Redis:
    return redis_client
