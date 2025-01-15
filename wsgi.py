import sys
from app import create_app

try:
    application = create_app()
except Exception as e:
    print(f"Error creating app: {str(e)}", file=sys.stderr)
    raise 