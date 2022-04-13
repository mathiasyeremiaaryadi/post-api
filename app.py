from decimal import DefaultContext
import json
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from datetime import datetime
from kanpai import Kanpai
from flask_cors import CORS

# Inisiasi Flask
app = Flask(__name__)
CORS(app)

# Konfigurasi validasi JSON
article_validator = Kanpai.Object({
    'title': Kanpai.String().required(error='Title is required').match(r'^.{20,}$', error='Title at least 20 characters'),
    'content': Kanpai.String().required(error='Content is required').match(r'^.{200,}$', error='Content at least 200 characters'),
    'category': Kanpai.String().required(error='Category is required').match(r'^.{3,}$', error='Category at least 3 characters'),
    'status': Kanpai.String().required(error='Status is required').anyOf(('publish', 'draft', 'trash'), error='Status must choose between publish, draft, or trash')
})

# Konfigurasi database
DB_URL = 'mysql://root@localhost/posts'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
marshmallow = Marshmallow(app)

# Inisiasi database migration
migrate = Migrate(app, db)

# Membuat model Article
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    category = db.Column(db.String(100))
    created_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(100))

    def __init__(self, title, content, category, status):
        self.title = title
        self.content = content
        self.category = category
        self.status = status

# Membuat schema Article
class ArticleSchema(marshmallow.Schema):
    class Meta:
        fields = ('id', 'title', 'content', 'category', 'status')

# Inisiasi schema Article
article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)

# Membuat endpoint REST API
# Tambah artikel
@app.route('/article', methods=['POST'])
def store_article():
    try:
        article_validation = article_validator.validate(request.json)

        if article_validation.get('success', False) is False:
            return jsonify({
                'status': 'validation',
                'code': 400,
                'data': article_validation.get('error')
            })

        title = request.json['title']
        content = request.json['content']
        category = request.json['category']
        status = request.json['status']

        new_article = Article(title, content, category, status)

        db.session.add(new_article)
        db.session.commit()
    except Exception as error:
        return jsonify({
            'status': 'error',
            'code': 400,
            'data': str(error)
        })


    return jsonify({
        'status': 'OK',
        'code': 201,
        'data': 'Article successfuly created'
    })

# Ambil semua artikel yang sudah dipublish dengan paginasi
@app.route('/article/<limit>/<offset>', methods=['GET'])
def get_articles(limit, offset):
    try:
        articles = Article.query.filter_by(status='publish').order_by(desc(Article.created_date)).limit(limit).offset(offset).all()
        result = articles_schema.dump(articles)
    except Exception as error:
        return jsonify({
            'status': 'error',
            'code': 400,
            'data': str(error)
        })

    return jsonify({
        'status': 'OK',
        'code': 200,
        'data': result
    })

# Ambil semua artikel yang published
@app.route('/article/published', methods=['GET'])
def get_published_articles():
    try:
        articles = Article.query.filter_by(status='publish').order_by(desc(Article.created_date)).all()
        result = articles_schema.dump(articles)
    except Exception as error:
        return jsonify({
            'status': 'error',
            'code': 400,
            'data': str(error)
        })

    return jsonify({
        'status': 'OK',
        'code': 200,
        'data': result
    })

# Ambil semua artikel yang drafted
@app.route('/article/drafted', methods=['GET'])
def get_drafted_articles():
    try:
        articles = Article.query.filter_by(status='draft').order_by(desc(Article.created_date)).all()
        result = articles_schema.dump(articles)
    except Exception as error:
        return jsonify({
            'status': 'error',
            'code': 400,
            'data': str(error)
        })

    return jsonify({
        'status': 'OK',
        'code': 200,
        'data': result
    })

# Ambil semua artikel yang trashed
@app.route('/article/trashed', methods=['GET'])
def get_trashed_articles():
    try:
        articles = Article.query.filter_by(status='trash').order_by(desc(Article.created_date)).all()
        result = articles_schema.dump(articles)
    except Exception as error:
        return jsonify({
            'status': 'error',
            'code': 400,
            'data': str(error)
        })

    return jsonify({
        'status': 'OK',
        'code': 200,
        'data': result
    })

# Ambil satu artikel berdasarkan id
@app.route('/article/<id>', methods=['GET'])
def get_article(id):
    try:
        article = Article.query.get(id)
        result = article_schema.dump(article)
    except Exception as error:
        return jsonify({
            'status': 'error',
            'code': 400,
            'data': str(error)
        })

    return jsonify({
        'status': 'OK',
        'code': 200,
        'data': result
    })

# Ubah artikel berdasarkan id
@app.route('/article/<id>', methods=['PUT'])
def update_article(id):
    try:
        article_validation = article_validator.validate(request.json)

        if article_validation.get('success', False) is False:
            return jsonify({
                'status': 'validation',
                'code': 400,
                'data': article_validation.get('error')
            })

        article = Article.query.get(id)
        title = request.json['title']
        content = request.json['content']
        category = request.json['category']
        status = request.json['status']

        article.title = title
        article.content = content
        article.category = category
        article.status = status

        db.session.commit()
    except Exception as error:
        return jsonify({
            'status': 'error',
            'code': 400,
            'data': str(error)
        })

    return jsonify({
        'status': 'OK',
        'code': 200,
        'data': 'Article successfuly updated'
    })

# Ubah status berdasarkan id
@app.route('/article/status/<id>', methods=['PUT'])
def update_article_status(id):
    try:
        article = Article.query.get(id)
        article.status = 'trash'

        db.session.commit()
    except Exception as error:
        return jsonify({
            'status': 'error',
            'code': 400,
            'data': str(error)
        })

    return jsonify({
        'status': 'OK',
        'code': 200,
        'data': 'Article successfuly moved to trash'
    })

# Hapus artikel berdasarkan id
@app.route('/article/<id>', methods=['DELETE'])
def delete_article(id):
    try:
        article = Article.query.get(id)

        db.session.delete(article)
        db.session.commit()
    except Exception as error:
        return jsonify({
            'status': 'error',
            'code': 400,
            'data': str(error)
        })

    return jsonify({
        'status': 'OK',
        'code': 200,
        'data': 'Article successfuly deleted'
    })

# Inisiasi server BE
if __name__ == 'main':
    app.run()
