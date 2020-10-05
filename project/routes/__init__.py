from flask import Blueprint

from .news_routes import news_bp

def init_app(app):
    app.register_blueprint(news_bp)

