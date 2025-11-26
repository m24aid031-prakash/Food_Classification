# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import torch
from torchvision import transforms
import torch.nn as nn
import io
from model_service import load_model, predict_topk
from fastapi.responses import JSONResponse

# Flask setup
app = Flask(__name__)
CORS(app)

# Load weights safely
model = load_model()

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['image']
    img_bytes = file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    results = predict_topk(model, image, topk=5)

    return jsonify({'prediction': [
                {"class": name, "probability": round(prob * 100, 2)}
                for name, prob in results
            ]})

if __name__ == '__main__':
    app.run(debug=True)
