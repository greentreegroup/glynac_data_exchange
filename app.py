from flask import Flask, jsonify
from flask_cors import CORS
from frontend.src.app.api.zscore import zscore_bp


app = Flask(__name__)
CORS(app)  # allow cross domain communication
app.register_blueprint(zscore_bp)
@app.route('/')
def home():
    return "Flask Backend is Running!"

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from Flask backend!"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
