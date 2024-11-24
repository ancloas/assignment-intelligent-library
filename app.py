from quart import Quart, jsonify, request, session
from db_utils import db_manager
from models import Book, Review
from auth_manager import AuthManager, require_login
import os
from dotenv import load_dotenv
from llm_utils import HuggingFaceModel
import pandas as pd

load_dotenv()

app = Quart(__name__)
auth_manager = AuthManager(db_manager)  # Initialize AuthManager with db_manager
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'qwe')
hf_model = HuggingFaceModel(model_name="meta-llama/Llama-3.2-3B-Instruct")


@app.before_serving
async def setup():
    """Initialize database tables before starting the server."""
    await db_manager.create_tables()


@app.route('/register', methods=['POST'])
async def register():
    """Handle user registration."""
    data = await request.get_json()
    required_fields = ['username', 'password', 'email', 'full_name']
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "All fields are required."}), 400

    result = await auth_manager.register(
        data['username'], 
        data['password'], 
        data['email'], 
        data['full_name']
    )
    return jsonify(result)


@app.route('/login', methods=['POST'])
async def login():
    """Handle user login."""
    data = await request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required."}), 400

    result = await auth_manager.sign_in(data['username'], data['password'])
    return jsonify(result)


@app.route('/logout', methods=['POST'])
@require_login
async def logout():
    """Handle user logout."""
    result = await auth_manager.sign_out()
    return jsonify(result)


@app.route('/profile', methods=['GET'])
@require_login
async def profile():
    """Fetch the current user's profile information."""
    current_user = await auth_manager.get_current_user()
    return jsonify(current_user) if current_user else jsonify({"error": "User not found."}), 404


@app.route('/books', methods=['POST'])
@require_login
async def add_book():
    """Add a new book."""
    data = await request.get_json()
    new_book = Book(**data)
    await db_manager.add_or_save(new_book)
    return jsonify({"message": "Book added successfully!"}), 201


@app.route('/books', methods=['GET'])
@require_login
async def get_books():
    """Fetch all books."""
    books = await db_manager.fetch_all(Book)
    return jsonify([book.to_dict() for book in books])


@app.route('/books/<int:book_id>', methods=['GET'])
@require_login
async def get_book(book_id):
    """Fetch a specific book."""
    book = await db_manager.fetch_one(Book, {'id':book_id})
    if book: 
        return jsonify(book.to_dict()), 200 
    else:
        return jsonify({"error": "Book not found"}), 404


@app.route('/books/<int:book_id>', methods=['PUT'])
@require_login
async def update_book(book_id):
    """Update an existing book."""
    data = await request.get_json()
    updated_results = await db_manager.update_one_or_more(Book,filters= {'id':book_id}, updates = data)
    if updated_results:
        book = updated_results[0]

    return jsonify({"message": "Book updated successfully!", "updated_book": book.to_dict()}), 200


@app.route('/books/<int:book_id>', methods=['DELETE'])
@require_login
async def delete_book(book_id):
    """Delete a specific book."""
    book = await db_manager.fetch_one(Book, {'id':book_id})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    await db_manager.delete(book)
    return jsonify({"message": "Book deleted successfully!"})


@app.route('/books/<int:book_id>/reviews', methods=['POST'])
@require_login
async def add_review(book_id):
    """Add a review to a book."""
    data = await request.get_json()
    review = Review(
        book_id=book_id,
        user_id=session.get('user_id'),
        review_text=data['review_text'],
        rating=data['rating']
    )
    await db_manager.add_or_save(review)
    return jsonify({"message": "Review added successfully!"}), 201


@app.route('/books/<int:book_id>/reviews', methods=['GET'])
@require_login
async def get_reviews(book_id):
    """Fetch reviews for a specific book."""
    reviews = await db_manager.fetch_all(Review, filters={"book_id": book_id})
    return jsonify([review.to_dict() for review in reviews])


@app.route('/books/<int:book_id>/summary', methods=['GET'])
@require_login
async def get_book_summary(book_id):
    """Fetch book summary and average rating."""
    book = await db_manager.fetch_one(Book, {'id':book_id})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    reviews = await db_manager.fetch_all(Review, filters={"book_id": book_id})
    average_rating = (
        sum(review.rating for review in reviews) / len(reviews) if reviews else 0
    )

    return jsonify({
        "book": book.to_dict(),
        "average_rating": average_rating,
        "review_count": len(reviews)
    })


@app.route('/recommendations', methods=['GET'])
@require_login
async def get_recommendations():
    """Fetch recommended books based on user reviews."""
    
    # Query to get the user's preferred genres and authors from their reviews
    query = """SELECT DISTINCT 
                    B.author, 
                    B.genre
                    FROM books B
                    JOIN reviews R 
                        ON B.id = R.book_id
                    WHERE R.user_id = :user_id
            """
    # Execute the query asynchronously and fetch results
    result = await db_manager.execute_raw(query=query, params={'user_id': session.get('user_id')})
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

    # Extract unique authors and genres
    authors = df['author'].unique().tolist()
    genres = df['genre'].unique().tolist()
    
    # Construct a persona-based prompt for the recommendation model
    persona_prompt =  f"""You are a friendly and knowledgeable book recommender with a passion for literature. 
    Your goal is to recommend books that align with the user's reading preferences. 
    You know a lot about different authors, genres, and trends in literature. 
    The user has given you their reading history, and you should provide book recommendations based on their favorite authors and genres. 
    Keep your recommendations diverse, but always ensure they reflect the user’s interests. 
    Here are their favorite authors and genres:
    
    - Authors: {', '.join(authors)}
    - Genres: {', '.join(genres)}

    Now, please recommend some books that the user might enjoy based on these preferences. """
    
    # Generate the recommendation using your HuggingFace model's generate_response function
    try:
        recommendations = await hf_model.generate_response(persona_prompt)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    # Return the recommendations as part of the response
    return jsonify({"recommendations": recommendations})



@app.route('/books/<int:book_id>/generate-summary', methods=['POST'])
@require_login
async def generate_summary(book_id):
    """Generate a summary for book content."""
    book = await db_manager.fetch_one(Book, filters={'id': book_id})
    summary = await book.generate_summary(llm_model = hf_model, db_manager= db_manager)

    return jsonify({"summary": summary})



if __name__ == '__main__':
    app.run(debug=True)
