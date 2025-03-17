from flask import Flask, jsonify
from flask_cors import CORS
from config import configure_app, db
from flasgger import Swagger


app = Flask(__name__)

configure_app(app)

CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "ngrok-skip-browser-warning"]}},
    supports_credentials=True
    )
swagger = Swagger(app)


with app.app_context():
    db.create_all()

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True)
