from flask import Flask, request, jsonify
from dotenv import load_dotenv
import base64
from functools import wraps
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
from datetime import datetime

load_dotenv()

USERNAME = os.getenv("AUTH_USERNAME")
PASSWORD = os.getenv("AUTH_PASSWORD")

def require_auth_json(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Basic '):
            return jsonify({'success': False, 'message': 'Missing or invalid Authorization header', 'data': None}), 401
        try:
            encoded_credentials = auth.split(' ')[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            input_username, input_password = decoded_credentials.split(':', 1)
        except Exception:
            return jsonify({'success': False, 'message': 'Invalid Authorization format', 'data': None}), 401
        if input_username != USERNAME or input_password != PASSWORD:
            return jsonify({'success': False, 'message': 'Invalid username or password', 'data': None}), 401
        if 'application/json' not in request.headers.get('Accept', ''):
            return jsonify({'success': False, 'message': 'Accept header must include application/json', 'data': None}), 406
        return f(*args, **kwargs)
    return decorated

# Load model TFLite
interpreter = tf.lite.Interpreter(model_path="model/model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

class_names = ['Bawang Bombai', 'Bawang Merah', 'Bawang Putih', 'Brokoli', 'Cabai Hijau',
               'Cabai Merah', 'Daging Sapi', 'Daging Unggas', 'Ikan', 'Jagung', 'Jahe', 'Jamur', 'Kacang Hijau',
               'Kacang Merah', 'Kacang Panjang', 'Kacang Tanah', 'Kembang Kol', 'Kentang', 'Kikil', 'Kol',
               'Labu Siam', 'Mie', 'Nasi', 'Petai', 'Sawi', 'Selada', 'Seledri', 'Telur Ayam', 'Telur Bebek',
               'Tempe', 'Terong', 'Timun', 'Tomat', 'Usus', 'Wortel']

def preprocess_image(image_bytes, target_size=(224, 224)):
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    image = image.resize(target_size)
    image_array = np.array(image, dtype=np.float32) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Welcome This API Eatzi</p>"

@app.route('/predict', methods=['POST'])
@require_auth_json
def predict():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file', 'data': None}), 400

    try:
        image_bytes = file.read()
        input_data = preprocess_image(image_bytes, target_size=(224, 224)).astype(np.float32)

        # TFLite inference
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])[0]

        predicted_index = int(np.argmax(output_data))
        predicted_label = class_names[predicted_index]
        confidence = float(np.max(output_data))

        return jsonify({
            'success': True,
            'message': 'Prediction successful',
            'data': {
                'predicted_class': predicted_label,
                'confidence': confidence,
                'raw_predictions': output_data.tolist()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Prediction failed',
            'data': None,
            'error': str(e)
        }), 500

@app.route('/feedback', methods=['POST'])
@require_auth_json
def feedback():
    try:
        value = request.form.get('data')
        if value not in ['0', '1']:
            return jsonify({'success': False, 'message': 'Invalid value. Only "1" (like) or "0" (dislike) are accepted.', 'data': None}), 400

        value = int(value)
        count_file = 'data/feedback_data.txt'
        log_file = 'data/feedback_log.txt'
        like_count, dislike_count = 0, 0

        if os.path.exists(count_file):
            with open(count_file, 'r') as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    like_count = int(lines[0].strip())
                    dislike_count = int(lines[1].strip())

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if value == 1:
            like_count += 1
            feedback_type = "Like"
        else:
            dislike_count += 1
            feedback_type = "Dislike"

        with open(count_file, 'w') as f:
            f.write(f'{like_count}\n{dislike_count}\n')
        with open(log_file, 'a') as log:
            log.write(f'[{timestamp}] {feedback_type}\n')

        return jsonify({
            'success': True,
            'message': 'Feedback recorded successfully.',
            'data': {'likes': like_count, 'dislikes': dislike_count}
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error while recording feedback.',
            'data': None,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
