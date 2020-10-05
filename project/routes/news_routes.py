from flask import Blueprint, jsonify, request
from ..services.news_service import NewsService
import time
import datetime
import json

news_bp = Blueprint('news_routes', __name__, url_prefix='/api/v1/news')
news_service = NewsService()


@news_bp.route('', methods=['POST'])
def save_news():
        articles = request.get_json()
        news_service.save_articles(articles)
        return "Articles saved", 200
        
@news_bp.route('/scrape', methods=["GET"])
def get_news():
    if request.args.get('company_name'):
        news_service = NewsService()
        articles = news_service.scrape(**request.args)
        return jsonify(articles), 200
    return "No company name provided", 400

