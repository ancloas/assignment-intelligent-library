from quart import Quart, jsonify, request
from db_manager import db_manager
from models import Book, Review

app = Quart(__name__)

@app.before_serving
async def setup():
    await db_manager.create_tables()

@app.route('/books', methods=['POST'])
async def add_book():
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
    rows = await db_manager.fetch_all("SELECT * FROM books")  # Fetch all rows
    return jsonify([row._asdict() for row in rows])

@app.route('/books/<int:book_id>', methods=['GET'])
async def get_book(book_id):
    book = await db_manager.fetch_one("SELECT * FROM books WHERE id = :id", {"id": book_id})  # Fetch specific book
    if book:
        return jsonify(book._asdict())  # Convert to dict for JSON response
    return jsonify({"error": "Book not found"}), 404

@app.route('/books/<int:book_id>', methods=['PUT'])
async def update_book(book_id):
    data = await request.json
    title = data.get('title')
    author = data.get('author')
    genre = data.get('genre')
    year_published = data.get('year_published')
    summary = data.get('summary')

    # Prepare the update query
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

    # Execute the update query
    await db_manager.execute(query, params)

    return jsonify({"message": "Book updated successfully!"}), 200


@app.route('/books/<int:book_id>', methods=['DELETE'])
async def delete_book(book_id):
    book = await db_manager.fetch_one("SELECT * FROM books WHERE id = :id", {"id": book_id})  # Check if book exists
    if book:
        query = """
        DELETE FROM books
        WHERE id = :id
        """
        params = {
        'id': book_id
        }

        await db_manager.execute(query=query, params=params)  # Delete the book
        return jsonify({"message": "Book deleted successfully!"})
    return jsonify({"error": "Book not found"}), 404

@app.route('/books/<int:book_id>/reviews', methods=['POST'])
async def add_review(book_id):
    data = await request.json
    new_review = Review(
        book_id=book_id,
        user_id=data['user_id'],
        review_text=data['review_text'],
        rating=data['rating']
    )
    
    await db_manager.add(new_review)  # Add the review
    return jsonify({"message": "Review added successfully!"}), 201

@app.route('/books/<int:book_id>/reviews', methods=['GET'])
async def get_reviews(book_id):
    reviews = await db_manager.fetch_all("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id})  # Fetch reviews for a specific book
    return jsonify([review._asdict() for review in reviews])  # Convert to dict for JSON response

@app.route('/books/<int:book_id>/summary', methods=['GET'])
async def get_book_summary(book_id):
    book = await db_manager.fetch_one("SELECT * FROM books WHERE id = :id", {"id": book_id})  # Fetch specific book
    if not book:
        return jsonify({"error": "Book not found"}), 404

    reviews = await db_manager.fetch_all("SELECT rating FROM reviews WHERE book_id = :book_id", {"book_id": book_id})  # Fetch ratings for the book
    total_rating = sum(review.rating for review in reviews) if reviews else 0
    average_rating = total_rating / len(reviews) if reviews else 0

    return jsonify({
        "book": book._asdict,
        "average_rating": average_rating,
        "review_count": len(reviews)
    })

@app.route('/recommendations', methods=['GET'])
async def get_recommendations():
    # This is a placeholder for your recommendation logic 
    recommendations = await db_manager.fetch_all("SELECT * FROM books LIMIT 5")  # Fetch some recommended books
    return jsonify([book._asdict for book in recommendations])  # Convert to dict for JSON response

@app.route('/generate-summary', methods=['POST'])
async def generate_summary():
    data = await request.json
    # Assume there's a function to generate a summary using your Llama3 model
    # summary = generate_summary_with_llama(data['content'])
    summary = "This is a placeholder summary."  # Placeholder response
    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(debug=True)
