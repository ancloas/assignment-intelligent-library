from werkzeug.security import generate_password_hash, check_password_hash
from db_utils import DatabaseManager  # Assuming this is the new db_manager
from models import User  # Assuming User is a model class
from typing import Dict, Any
from functools import wraps
from quart import session, jsonify

class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def register(self, username: str, password: str, email: str, full_name: str) -> Dict[str, Any]:
        """Register a new user with hashed password."""
        # Check if username already exists
        existing_user = await self.db_manager.fetch_one(User, filters={"username": username})

        if existing_user:
            return {"is_success": False, "message": "Username already exists"}

        # Hash the password before storing
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password, email=email, full_name=full_name)

        try:
            # Insert the user object into PostgreSQL
            await self.db_manager.add_or_save(new_user)
            return {"is_success": True, "message": "User registered successfully"}
        except Exception as e:
            return {"is_success": False, "message": f"Error creating user: {e}"}

    async def sign_in(self, username: str, password: str) -> Dict[str, Any]:
        """Sign in the user by verifying credentials."""
        # Fetch the user by username
        user = await self.db_manager.fetch_one(User, filters={"username": username})

        if user and check_password_hash(user.password_hash, password):
            # Store user info in session
            session['user_id'] = user.id
            session['username'] = user.username
            return {
                "is_success": True,
                "message": "Sign in successful",
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            }
        else:
            return {"is_success": False, "message": "Invalid credentials"}

    async def sign_out(self) -> Dict[str, Any]:
        """Sign out the user by clearing the session."""
        session.clear()
        return {"is_success": True, "message": "Sign out successful"}

    def is_authenticated(self) -> bool:
        """Check if the user is authenticated."""
        return 'user_id' in session

    async def get_current_user(self) -> Dict[str, Any]:
        """Retrieve the current logged-in user based on the session."""
        user_id = session.get('user_id')
        if user_id:
            user = await self.db_manager.fetch_one(User, user_id)
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            } if user else None
        return None

# Decorator to require login for certain routes


def require_login(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        # Ensure session is correctly checked in an async environment
        if session.get('user_id') is None:
            # Return a 403 Forbidden response if not logged in
            return jsonify({"error": "User must be logged in."}), 403
        return await f(*args, **kwargs)
    return decorated_function
