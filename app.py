from quart import Quart, jsonify, request, session
from db_manager import db_manager
from models import Book, Review
from auth_manager import AuthManager, require_login  
import os
from dotenv import load_dotenv

load_dotenv()

app = Quart(__name__)
auth_manager = AuthManager(db_manager)  # Initialize AuthManager with db_manager
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'qwe')



@app.before_serving
async def setup():
    await db_manager.create_tables()


@app.route('/register', methods=['POST'])
async def register():
    """Handle user registration."""
    data = await request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    full_name = data.get('full_name')

    if not username or not password or not email or not full_name:
        return jsonify({"error": "All fields are required."}), 400

    # Register the user using AuthManager
    result = await auth_manager.register(username, password, email, full_name)
    return jsonify(result)


@app.route('/login', methods=['POST'])
async def login():
    """Handle user login."""
    data = await request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    # Sign in the user using AuthManager
    result = await auth_manager.sign_in(username, password)
    return jsonify(result)


@app.route('/logout', methods=['POST'])
async def logout():
    """Handle user logout."""
    result = await auth_manager.sign_out()
    return jsonify(result)


@app.route('/profile', methods=['GET'])
@require_login
async def profile():
    """Fetch the current user's profile information."""
    current_user = await auth_manager.get_current_user()
    if current_user:
        return jsonify(current_user)
    return jsonify({"error": "User not found."}), 404


@app.route('/books', methods=['POST'])
@require_login
async def add_book():
    """Add a new book - requires login."""
    data = await request.json
    new_book = Book(
        title=data['title'],
        author=data['author'],
        genre=data['genre'],
        year_published=data.get('year_published'),
        summary=data.get('summary')
    )
    
    await db_manager.add(new_book)
    return jsonify({"message": "Book added successfully!"}), 201


@app.route('/books', methods=['GET'])
async def get_books():
    """Fetch all books."""
    rows = await db_manager.fetch_all("SELECT * FROM books")
    return jsonify(rows)


@app.route('/books/<int:book_id>', methods=['GET'])
async def get_book(book_id):
    """Fetch a specific book."""
    book = await db_manager.fetch_one("SELECT * FROM books WHERE id = :id", {"id": book_id})
    if book:
        return jsonify(book)
    return jsonify({"error": "Book not found"}), 404


@app.route('/books/<int:book_id>', methods=['PUT'])
@require_login
async def update_book(book_id):
    """Update an existing book - requires login."""
    data = await request.json
    title = data.get('title')
    author = data.get('author')
    genre = data.get('genre')
    year_published = data.get('year_published')
    summary = data.get('summary')

    query = """
    UPDATE books
    SET title = :title,
        author = :author,
        genre = :genre,
        year_published = :year_published,
        summary = :summary
    WHERE id = :id
    """

    params = {
        'title': title,
        'author': author,
        'genre': genre,
        'year_published': year_published,
        'summary': summary,
        'id': book_id
    }

    await db_manager.execute(query, params)
    return jsonify({"message": "Book updated successfully!"}), 200


@app.route('/books/<int:book_id>', methods=['DELETE'])
@require_login
async def delete_book(book_id):
    """Delete a specific book - requires login."""
    book = await db_manager.fetch_one("SELECT * FROM books WHERE id = :id", {"id": book_id})
    if book:
        query = "DELETE FROM books WHERE id = :id"
        params = {'id': book_id}
        await db_manager.execute(query, params)
        return jsonify({"message": "Book deleted successfully!"})
    return jsonify({"error": "Book not found"}), 404


@app.route('/books/<int:book_id>/reviews', methods=['POST'])
@require_login
async def add_review(book_id):
    """Add a review to a book - requires login."""
    data = await request.json
    new_review = Review(
        book_id=book_id,
        user_id=session['user_id'],
        review_text=data['review_text'],
        rating=data['rating']
    )
    
    await db_manager.add(new_review)
    return jsonify({"message": "Review added successfully!"}), 201

@require_login
@app.route('/books/<int:book_id>/reviews', methods=['GET'])
async def get_reviews(book_id):
    """Fetch reviews for a specific book."""
    query = """
            SELECT u.username as username, b.title, r.review_text, r.rating
              FROM reviews r 
              inner join users u on r.user_id = u.id 
              inner join books b on r.book_id = b.id and r.book_id = :book_id
            """
    reviews = await db_manager.fetch_all(query, {"book_id": book_id})
    return jsonify(reviews)

@require_login
@app.route('/books/<int:book_id>/summary', methods=['GET'])
async def get_book_summary(book_id):
    """Fetch book summary and average rating."""
    book = await db_manager.fetch_one("SELECT * FROM books WHERE id = :id", {"id": book_id})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    reviews = await db_manager.fetch_all("SELECT rating FROM reviews WHERE book_id = :book_id", {"book_id": book_id})
    total_rating = sum(review.rating for review in reviews) if reviews else 0
    average_rating = total_rating / len(reviews) if reviews else 0

    return jsonify({
        "book": book,
        "average_rating": average_rating,
        "review_count": len(reviews)
    })

@require_login
@app.route('/recommendations', methods=['GET'])
async def get_recommendations():
    """Fetch recommended books."""
    recommendations = await db_manager.fetch_all("SELECT * FROM books LIMIT 5")
    return jsonify([book._asdict() for book in recommendations])

@require_login
@app.route('/generate-summary', methods=['POST'])
async def generate_summary():
    """Generate a summary for book content."""
    data = await request.json
    # Placeholder for generating summary logic (like using Llama3)
    summary = "This is a placeholder summary."
    return jsonify({"summary": summary})


if __name__ == '__main__':
    app.run(debug=True)
