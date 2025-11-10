from flask import Flask, request, jsonify
from pydantic import ValidationError
from botocore.exceptions import ClientError
from models.book import Book
from db.factory import DatabaseFactory

app = Flask(__name__)

try:
    db = DatabaseFactory.create()
except ValueError as e:
    raise RuntimeError(f"Error initializing DB: {e}") from e

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,x-api-key'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

@app.route('/items', methods=['POST'])
def create_item():
    try:
        data = request.get_json()
        book = Book(**data)
        created = db.create_book(book)
        return jsonify(created.model_dump()), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except ClientError as e:
        error_message = e.response['Error']['Message'] if 'Error' in e.response else str(e)
        return jsonify({'error': 'DynamoDB error', 'details': error_message}), 500

@app.route('/items/<book_id>', methods=['GET'])
def get_item(book_id):
    try:
        book = db.get_book(book_id)
        if book:
            return jsonify(book.model_dump()), 200
        return jsonify({'error': 'Item no encontrado'}), 404
    except ClientError as e:
        error_message = e.response['Error']['Message'] if 'Error' in e.response else str(e)
        return jsonify({'error': 'DynamoDB error', 'details': error_message}), 500

@app.route('/items', methods=['GET'])
def get_all_items():
    try:
        books = db.get_all_books()
        return jsonify([t.model_dump() for t in books]), 200
    except ClientError as e:
        error_message = e.response['Error']['Message'] if 'Error' in e.response else str(e)
        return jsonify({'error': 'DynamoDB error', 'details': error_message}), 500

@app.route('/items/<book_id>', methods=['PUT'])
def update_item(book_id):
    try:
        data = request.get_json()
        data.pop('book_id', None)
        data.pop('created_at', None)
        book = Book(**data)
        updated = db.update_book(book_id, book)
        if updated:
            return jsonify(updated.model_dump()), 200
        return jsonify({'error': 'Item no encontrado'}), 404
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except ClientError as e:
        error_message = e.response['Error']['Message'] if 'Error' in e.response else str(e)
        return jsonify({'error': 'DynamoDB error', 'details': error_message}), 500

@app.route('/items/<book_id>', methods=['DELETE'])
def delete_item(book_id):
    try:
        if db.delete_book(book_id):
            return '', 204
        return jsonify({'error': 'Item no encontrado'}), 404
    except ClientError as e:
        error_message = e.response['Error']['Message'] if 'Error' in e.response else str(e)
        return jsonify({'error': 'DynamoDB error', 'details': error_message}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)