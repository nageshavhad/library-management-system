from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import Request, Book

bp = Blueprint('librarian', __name__, url_prefix='/librarian')

@bp.route('/create_book', methods=['POST'])
@jwt_required()
def create_book():
    user_id = get_jwt_identity()
    claims = get_jwt()
    is_librarian = claims.get('is_librarian', False)
    if not is_librarian:
        return jsonify({'message': 'Unauthorized'}), 403
    
    title = request.json.get('title')
    author = request.json.get('author')
    new_book = Book(title=title, author=author)
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book created successfully'}), 201

@bp.route('/get_book/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'available': book.available
    }), 200

@bp.route('/get_all_books', methods=['GET'])
@jwt_required()
def get_all_books():
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'available': book.available
    } for book in books]), 200

@bp.route('/update_book/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    is_librarian = claims.get('is_librarian', False)
    if not is_librarian:
        return jsonify({'message': 'Unauthorized'}), 403
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.available = data.get('available', book.available)
    db.session.commit()
    return jsonify({'message': 'Book updated successfully'}), 200

@bp.route('/delete_book/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    is_librarian = claims.get('is_librarian', False)
    if not is_librarian:
        return jsonify({'message': 'Unauthorized'}), 403
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'}), 200

@bp.route('/approve_request', methods=['POST'])
@jwt_required()
def approve_request():
    user_id = get_jwt_identity()
    claims = get_jwt()
    is_librarian = claims.get('is_librarian', False)
    if not is_librarian:
        return jsonify({'message': 'Unauthorized'}), 403
    request_id = request.json.get('request_id')
    book_request = Request.query.get(request_id)
    book_request.request_approved = True
    db.session.commit()
    return jsonify({'message': 'Request approved successfully'}), 200

@bp.route('/accept_submission', methods=['POST'])
@jwt_required()
def accept_submission():
    print('accept_submission')
    user_id = get_jwt_identity()
    claims = get_jwt()
    is_librarian = claims.get('is_librarian', False)
    if not is_librarian:
        return jsonify({'message': 'Unauthorized'}), 403
    request_id = request.json.get('request_id')
    book_request = Request.query.get(request_id)
    book_request.return_approved = True
    book = Book.query.get_or_404(book_request.book_id)
    book.available = True
    db.session.commit()
    return jsonify({'message': 'Submission accepted successfully'}), 200