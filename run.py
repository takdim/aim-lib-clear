import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', os.environ.get('PORT', 5000)))
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true') if 'FLASK_DEBUG' in os.environ else app.config.get('DEBUG', False)
    app.run(debug=debug, port=port)
