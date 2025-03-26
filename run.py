"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # HTTPS support
    

from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct paths to SSL certificates
    cert_path = os.path.join(base_dir, 'app', 'certificates', 'server.crt')
    key_path = os.path.join(base_dir, 'app', 'certificates', 'server.key')
    
    # Run the app with SSL context
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000, 
        ssl_context=(cert_path, key_path)
    )
    
"""
 # run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run without SSL for testing
    app.run(debug=True, host='0.0.0.0', port=5000)

