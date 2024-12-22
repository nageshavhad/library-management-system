from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import User, Book, Request
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/create_user', methods=['POST'])
def create_user():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')
    is_librarian = request.json.get('is_librarian', False)
    password_hash = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=password_hash, is_librarian=is_librarian)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@bp.route('/get_user/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    is_librarian = claims.get('is_librarian', False)

    if is_librarian or str(user_id) == str(id):
        user = User.query.get_or_404(id)
    else:
        return jsonify({'message': 'Unauthorized'}), 403

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_librarian': user.is_librarian
    }), 200

@bp.route('/update_user/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    is_librarian = claims.get('is_librarian', False)

    if is_librarian or str(user_id) == str(id):
        user = User.query.get_or_404(id)
    else:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.is_librarian = data.get('is_librarian', user.is_librarian)
    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

@bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    is_librarian = claims.get('is_librarian', False)

    if is_librarian:
        user = User.query.get_or_404(id)
    else:
        return jsonify({'message': 'Unauthorized'}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

@bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        additional_claims = {"is_librarian": user.is_librarian}
        access_token = create_access_token(identity=str(user.id),additional_claims=additional_claims)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401

@bp.route('/request_book', methods=['POST'])
@jwt_required()
def request_book():
    user_id = get_jwt_identity()
    book_id = request.json.get('book_id')
    book = Book.query.get_or_404(book_id)
    if not book.available:
        return jsonify({'message': 'Book not available'}), 400
    new_request = Request(user_id=user_id, book_id=book_id)
    book.available = False
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': 'Book requested successfully'}), 201

@bp.route('/submit_book', methods=['POST'])
@jwt_required()
def submit_book():
    user_id = get_jwt_identity()
    request_id = request.json.get('request_id')
    book_request = Request.query.get(request_id)
    print(book_request.user_id,user_id)
    if str(book_request.user_id) != str(user_id):
        return jsonify({'message': 'Unauthorized'}), 403

    book_request.returned = True
    book_request.return_date = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Book submitted successfully'}), 200

@bp.route('/list_requests', methods=['GET'])
@jwt_required()
def list_requests():
    user_id = get_jwt_identity()
    claims = get_jwt()
    is_librarian = claims.get('is_librarian', False)
    
    if is_librarian:
        requests = db.session.query(Request, User.username).join(User, Request.user_id == User.id).all()
    else:
        requests = db.session.query(Request, User.username).filter(Request.user_id == user_id).join(User, Request.user_id == User.id).all()
    
    requests_list = [{
        'id': req.Request.id,
        'book_id': req.Request.book_id,
        'request_date': req.Request.request_date,
        'request_approved': req.Request.request_approved,
        'return_approved': req.Request.return_approved,
        'return_date': req.Request.return_date,
        'returned': req.Request.returned,
        'user_id': req.Request.user_id,
        'username': req.username
    } for req in requests]

    return jsonify(requests_list), 200