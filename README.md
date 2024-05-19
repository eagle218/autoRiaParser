# FastAPI Advertisement App

This project is a FastAPI-based web application for managing AutoRIA advertisements. It includes user authentication and uses SQLAlchemy for database interactions.

## Features

- FastAPI for the web framework
- SQLAlchemy for ORM
- JWT-based authentication
- Redis for caching

## Requirements

- Python 3.9+
- SQLite (or any other database supported by SQLAlchemy)
- Redis (for caching)
- pip (Python package installer)

## Installation

1. **Clone the repository:**

   ```sh
   git clone git clone https://github.com/yourusername/your-repo-name.git
   cd autoRiaParser
   ```
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
## Running the Application

1. Start the FastAPI server:
    ```
    uvicorn app.main:app --reload
    ```
2. Access the interactive API documentation:
   Open your browser and go to http://127.0.0.1:8000/docs to view the Swagger UI documentation.

## Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request. 
I welcome all improvements, from minor typo fixes to new features.
