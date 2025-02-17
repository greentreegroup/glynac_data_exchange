from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/')
def home():
    return "Flask Backend is Running!"

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from Flask backend!"})

@app.route('/api/zscore', methods=['GET'])
def get_zscore_data():
    try:
        # read Excel file
        df = pd.read_excel("Final_Data_with_Stats.xlsx")
        # convert DataFrame to dictionary
        data = df.to_dict(orient="records")
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
