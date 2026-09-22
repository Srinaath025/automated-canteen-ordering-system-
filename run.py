import sys
import os

# Ensure the current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("=" * 60)
    print(" CanteenFlow - Automated Canteen Ordering System")
    print(" Starting server on http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
