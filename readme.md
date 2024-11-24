# Smart Library Project

The Smart Library project is an intelligent library system that offers book recommendations using machine learning models. Built with Python's Quart framework, the backend supports asynchronous web development. This README will guide you through the setup and deployment of the project locally and via Docker.

## Prerequisites

Ensure the following are installed:

- Python 3.8 or higher
- Docker (optional, for containerization)
- Docker Compose (optional, for managing multi-container Docker applications)
- A Hugging Face API key (required for model interaction)

## Setup and Run Locally

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/ancloas/assignment-intelligent-library.git
cd ASSIGNMENT INTELLIGENT LIBRARY
```

### 2. Set up a Virtual Environment

It’s recommended to use a virtual environment to avoid package conflicts:

bash
```
python -m venv .venv
source venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### 3. Install Dependencies
Install the necessary Python dependencies:

bash
```
pip install -r requirements.txt

```

### 4. Configure Environment Variables
Create a .env file in the project root directory and add the following:
```
FLASK_APP=yourapp.py
FLASK_RUN_HOST=0.0.0.0
HUGGINGFACE_API_KEY=your_huggingface_api_key
DATABASE_URL=your_database_url
```

Replace the placeholders with actual values:

HUGGINGFACE_API_KEY is required to interact with Hugging Face models.
DATABASE_URL is for connecting the application to your database.

### 5. Run the Application Locally
Run the application using Quart:

```
quart run
```
------------------------------------------------------------------------------------------------
# Docker Setup
You can also containerize the application with Docker. This allows the app to be deployed in an isolated environment.

1. Build Docker Image
Use Docker to build the image for the application:

```
docker build -t smart-library .
```
2. Run Docker Image
To run the container and start the application, use the following command:

```
docker run -p 5000:5000 --env-file .env smart-library
```
This will run the app inside a Docker container, accessible at http://localhost:5000.

-----------

## Docker Compose Setup
For easier management of services and dependencies, use Docker Compose.

### 1. Docker Compose File
Ensure you have the following docker-compose.yml file in the project root:

yaml
```
version: '3.11'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_APP=yourapp.py
      - FLASK_RUN_HOST=0.0.0.0
    env_file:
      - .env
    volumes:
      - .:/app
    networks:
      - app_network
    restart: unless-stopped

networks:
  app_network:
    driver: bridge

```    
### 2. Start the Application with Docker Compose

Run the following command to start the application using Docker Compose:

bash
```
docker-compose up --build
```
This command will build and run the containers. Once the process is complete, you can access the application at http://localhost:5000.
