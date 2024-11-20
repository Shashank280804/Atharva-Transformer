import os
import json
import cv2
import numpy as np
from flask_cors import CORS
from flask import Flask, request, jsonify, send_from_directory

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Ensure that the base directories are correctly configured
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')

# Configure upload and processed folders
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Ensure that the upload and processed directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        file = request.files['file']
        transformation = request.form.get('transformation', 'none')
        params = request.form.get('params', '{}')  # Default to empty JSON object

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Parse the params string into a Python dictionary
        try:
            params = json.loads(params)  # Deserialize JSON string to dictionary
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid params format'}), 400

        # Save the file to the upload folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Process the image using the transformation logic
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], f"processed_{file.filename}")
        process_image(filepath, output_path, transformation, params)

        return send_from_directory(app.config['PROCESSED_FOLDER'], f"processed_{file.filename}")
    except Exception as e:
        print(f"Error processing image: {e}")  # Log error for debugging
        return jsonify({'error': f'Internal Server Error: {e}'}), 500

def process_image(input_path, output_path, transformation, params):
    image = cv2.imread(input_path)
    if transformation == 'scaling':
        scale_factor = float(params.get('scale_factor', 1.0))
        if scale_factor <= 0:
            raise ValueError("Scale factor must be greater than 0")
        height, width = image.shape[:2]
        new_width = max(1, int(width * scale_factor))
        new_height = max(1, int(height * scale_factor))
        output = cv2.resize(image, (new_width, new_height))

    elif transformation == 'rotation':
        angle = float(params.get('angle', 0))
        height, width = image.shape[:2]
        rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)
        output = cv2.warpAffine(image, rotation_matrix, (width, height))

    elif transformation == 'translation':
        offset_x = int(params.get('offset_x', 0))
        offset_y = int(params.get('offset_y', 0))
        
        # Calculate the new size of the image after translation
        height, width = image.shape[:2]
        new_width = width + abs(offset_x)
        new_height = height + abs(offset_y)
        
        # Create a blank canvas (white background) with the new size
        canvas = np.ones((new_height, new_width, 3), dtype=np.uint8) * 255  # white canvas
        
        # Define the translation matrix
        translation_matrix = np.float32([[1, 0, offset_x], [0, 1, offset_y]])

        # Perform the translation and place the image onto the canvas
        output = cv2.warpAffine(image, translation_matrix, (new_width, new_height))
        
    elif transformation == 'shearing':
        shear_x = float(params.get('shear_x', 0))
        shear_y = float(params.get('shear_y', 0))
        height, width = image.shape[:2]
        shear_matrix = np.float32([[1, shear_x, 0], [shear_y, 1, 0]])
        output = cv2.warpAffine(image, shear_matrix, (width, height))

    elif transformation == 'reflection':
        axis = params.get('axis', 'x')
        if axis == 'x':
            output = cv2.flip(image, 0)
        elif axis == 'y':
            output = cv2.flip(image, 1)
        elif axis == 'xy':
            output = cv2.flip(image, -1)
        else:
            raise ValueError("Invalid reflection axis")
    else:
        raise ValueError("Invalid transformation type")

    # Save the processed image
    cv2.imwrite(output_path, output)

if __name__ == '__main__':
    app.run(debug=True)
