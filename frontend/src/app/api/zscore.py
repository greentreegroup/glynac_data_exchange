from flask import Blueprint, jsonify
import pandas as pd

zscore_bp = Blueprint('zscore', __name__)

@zscore_bp.route('/api/zscore', methods=['GET'])
def get_zscore_data():
    try:
        # read Excel file
        df = pd.read_excel("Final_Data_with_Stats.xlsx")
        # turn DataFrame to dictionary
        data = df.to_dict(orient="records")
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
