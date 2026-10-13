from flask import Flask
from app.routes import main_bp

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Register Blueprint
app.register_blueprint(main_bp)

if __name__ == '__main__':
    print("Starting Local AI Meeting Assistant on http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)