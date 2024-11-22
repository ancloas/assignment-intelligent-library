from werkzeug.security import generate_password_hash, check_password_hash
from db_manager import DatabaseManager  # Assuming this utility is for PostgreSQL
from models import User  # Assuming User is a model class for PostgreSQL
from typing import Dict, Any
from functools import wraps
from quart import session, jsonify

class AuthManager:
    def __init__(self, db_manager:DatabaseManager):
        self.db_manager = db_manager

    async def register(self, username: str, password: str, email: str, full_name: str) -> Dict[str, Any]:
        # Check if username already exists
        query = "SELECT * FROM users WHERE username = :username"
        existing_user = await self.db_manager.fetch_one(query, {"username": username})

        if existing_user:
            return {"is_success": False, "message": "Username already exists"}

        # Hash the password before storing
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password, email=email, full_name=full_name)

        try:
            # Insert the user object into PostgreSQL
            await self.db_manager.add(new_user)
            return {"is_success": True, "message": "User registered successfully"}
        except Exception as e:
            return {"is_success": False, "message": f"Error creating user: {e}"}

    async def sign_in(self, username: str, password: str) -> Dict[str, Any]:
        # Find user by username
        query = "SELECT * FROM users WHERE username = :username"
        user = await self.db_manager.fetch_one(query, {"username": username})

        if user and check_password_hash(user['password_hash'], password):
            # Store the user's id in the session to manage user authentication state
            session['user_id'] = user['id']
            session['username'] = user['username']
            return {"is_success": True, "message": "Sign in successful", 'username': user['username'], 'email': user['email'], 'full_name': user['full_name']}
        else:
            return {"is_success": False, "message": "Invalid credentials"}

    async def sign_out(self) -> Dict[str, Any]:
        # Clear the user's session
        session.clear()
        return {"is_success": True, "message": "Sign out successful"}

    def is_authenticated(self) -> bool:
        # Check if the user is authenticated by checking session
        return 'user_id' in session

    async def get_current_user(self) -> Dict[str, Any]:
        # Retrieve the current logged-in user based on session
        user_id = session.get('user_id')
        if user_id:
            query = "SELECT * FROM users WHERE id = :user_id"
            user = await self.db_manager.fetch_one(query, {"user_id": user_id})
            return user
        return None

# Decorator to require login for certain routes
def require_login(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            # Return a 403 Forbidden response if not logged in
            return jsonify({"error": "User must be logged in."}), 403
        return await f(*args, **kwargs)
    return decorated_function
