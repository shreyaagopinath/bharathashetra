import os
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Ensure JWT secrets are set
if 'JWT_SECRET_KEY' not in os.environ:
    os.environ['JWT_SECRET_KEY'] = 'bharathashetra-jwt-secret-key-dev-2024'
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'bharathashetra-secret-key-dev-2024'

db = SQLAlchemy()
jwt = JWTManager()
