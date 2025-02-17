from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.run(
        port=8080,
        debug=True  # This will be overridden by FLASK_DEBUG from .env
    ) 