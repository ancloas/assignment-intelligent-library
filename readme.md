# Smart Library Project

The Smart Library project is an intelligent library system that offers book recommendations using machine learning models. Built with Python's Quart framework, the backend supports asynchronous web development. This README will guide you through the setup and deployment of the project locally and via Docker.

## Prerequisites

Ensure the following are installed:

- Python 3.8 or higher
- Docker (optional, for containerization)
- Docker Compose (optional, for managing multi-container Docker applications)
- A Hugging Face API key (required for model interaction)
- PostgreSQL

### Getting Hugging Face API Key
To get the Hugging Face API key for accessing models:
1. Go to [Hugging Face](https://huggingface.co/).
2. Sign up or log in to your account.
3. Navigate to the [API Tokens page](https://huggingface.co/settings/tokens).
4. Click **New Token** to create a token.
5. Copy the generated token and save it for later use in the `.env` file.

### Installing and Setting Up PostgreSQL on Windows

#### **1. Download and Install PostgreSQL**

1. **Download the PostgreSQL Installer**:
   - Visit the [PostgreSQL download page](https://www.postgresql.org/download/windows/).
   - Select the **Windows** installer option to download the installer package (e.g., from EnterpriseDB).

2. **Run the Installer**:
   - Once the installer is downloaded, run the installer file and follow the on-screen instructions.
   - **Choose Installation Directory**: The default directory is usually fine (`C:\Program Files\PostgreSQL\xx`).
   - **Select Components**: Ensure that the following components are selected:
     - PostgreSQL Server (required)
     - pgAdmin 4 (optional but useful for managing databases)
   - **Set a Password**: During installation, you'll be asked to set a password for the **postgres** user. Make sure to remember this password as it will be needed to access the database.
   - **Set Port**: The default port is `5432`, which you can leave as is.
   - **Set Locale**: The default locale is fine for most users.

3. **Complete Installation**:
   - Continue the installation, and PostgreSQL will be installed as a service on your machine.
   - After installation, PostgreSQL should start automatically.

#### **2. Verify PostgreSQL Installation**

1. Open **pgAdmin 4** (a graphical user interface for managing PostgreSQL databases).
   - You can access pgAdmin from the Start Menu.
   - It will prompt you for the password you set during installation.
   - You should be able to see the server running in pgAdmin.

2. Alternatively, open a **Command Prompt** and run:
   ```bash
   psql -U postgres
   ```

   This command connects to the PostgreSQL server using the postgres user and opens the PostgreSQL command line interface.

#### **3. Create a Database and User**
Now that PostgreSQL is installed and running, let's create a new database, a new user, and configure access.

Open the SQL Shell (psql):

Open the SQL Shell (psql) from the Start Menu or Command Prompt.
You will be asked for a few parameters like:
1. Server: Press Enter to use the default (localhost).
2. Database: Press Enter to use the default (postgres).
3. Port: Press Enter to use the default (5432).
4. Username: Press Enter to use postgres (or provide the username you want to use).
5. Password: Enter the password you set during installation.


##### Create a New Database: Once you are in the psql shell, create your new database by running the following SQL command:

sql
```
CREATE DATABASE smart_library; 
```

*Note: Above database related details, we will require these details to create environment variables*

## Setup and Run Locally

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/ancloas/assignment-intelligent-library.git
cd '.\assignment intelligent library\'
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
HUGGINGFACE_API_KEY=<your_huggingface_api_key>
POSTGRES_PORT= <port at which postgres sql is hosted>
POSTGRES_DB= <database name>
POSTGRES_USER= <db user name>
POSTGRES_PASSWORD= <db user password>
```

Replace the above placeholders with actual values:


### 5. Run the Application Locally
Run the application using Quart:

```
quart run
```
------------------------------------------------------------------------------------------------
# Docker Setup
You can also containerize the application with Docker. This allows the app to be deployed in an isolated environment.

## 1. Build Docker Image
Use Docker to build the image for the application:

```
docker build -t smart-library .
```
## 2. Run Docker Image
To run the container and start the application, use the following command:

```
docker run -p 5000:5000 --env-file .env smart-library
```
This will run the app inside a Docker container, accessible at http://localhost:5000.

-----------

# Docker Compose Setup
For easier management of services and dependencies, use Docker Compose.

## 1. Docker Compose File
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
## 2. Start the Application with Docker Compose

Run the following command to start the application using Docker Compose:

bash
```
docker-compose up --build
```
This command will build and run the containers. Once the process is complete, you can access the application at http://localhost:5000.
