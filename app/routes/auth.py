from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token, unset_jwt_cookies

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Optional: Debug print
    print("Received registration data:", data)

    # Validate input
    full_name = data.get('full_name') or data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not full_name or not email or not password:
        return jsonify({'message': 'Missing fields'}), 400

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 400

    # Hash password
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create new user with default role
    new_user = User(
        name=full_name,
        email=email,
        password=hashed_pw,
        role=data.get('role')
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error during registration: {e}")
        return jsonify({'message': 'Error during registration'}), 500


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing fields'}), 400

    try:
        user = User.query.filter_by(email=email).first()
    except Exception as e:
        return jsonify({'message': f'Error querying user: {str(e)}'}), 500

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if bcrypt.check_password_hash(user.password, password):
        # Generate access token using user_id as string
        access_token = create_access_token(identity=str(user.user_id))

        # Send back access token and role
        return jsonify({'access_token': access_token, 'role': user.role}), 200

    return jsonify({'message': 'Invalid credentials'}), 401




@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify({'message': f'Welcome, user {current_user_id}'}), 200

@bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    return jsonify({"message": "Token is valid"}), 200


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"message": "Successfully logged out"})
    unset_jwt_cookies(response)  # This clears the JWT token
    return response, 200


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    # Generate a new access token using the identity of the current user
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': new_access_token}), 200

@bp.route('/set-role', methods=['POST'])
@jwt_required()
def set_role():
    data = request.get_json()
    role = data.get('role')

    if role not in ['job_seeker', 'employer']:
        return jsonify({'error': 'Invalid role'}), 400

    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.role = role
    db.session.commit()
    return jsonify({'message': f'Role set to {role} successfully'}), 200


@bp.route('/updateskill', methods=['PUT'])
@jwt_required()
def update_profile():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    user = User.query.filter_by(user_id=current_user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if 'skills' in data:
        user.skills = data['skills']

    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating profile'}), 500

@bp.route('/deleteaccount', methods=['DELETE'])
@jwt_required()
def delete_account():
    current_user_id = get_jwt_identity()

    user = User.query.filter_by(user_id=current_user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Account deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting account'}), 500
