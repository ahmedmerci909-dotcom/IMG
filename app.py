from flask import Flask, send_file, abort, jsonify, request
import os
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)

# إعدادات
app.config['IMAGE_FOLDER'] = 'images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 1. الحصول على صورة معينة
@app.route('/image/<filename>')
def get_image(filename):
    try:
        filename = secure_filename(filename)
        file_path = os.path.join(app.config['IMAGE_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Image not found'}), 404
        
        # تحديد نوع الملف
        ext = filename.split('.')[-1].lower()
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp'
        }
        
        return send_file(file_path, mimetype=mime_types.get(ext, 'application/octet-stream'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 2. صورة عشوائية
@app.route('/random-image')
def random_image():
    try:
        images = [f for f in os.listdir(app.config['IMAGE_FOLDER']) 
                  if allowed_file(f)]
        
        if not images:
            return jsonify({'error': 'No images found'}), 404
        
        random_img = random.choice(images)
        return send_file(os.path.join(app.config['IMAGE_FOLDER'], random_img))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 3. قائمة جميع الصور
@app.route('/images')
def list_images():
    try:
        images = [f for f in os.listdir(app.config['IMAGE_FOLDER']) 
                  if allowed_file(f)]
        
        return jsonify({
            'count': len(images),
            'images': images,
            'urls': [f'/image/{img}' for img in images],
            'random': '/random-image'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 4. رفع صورة جديدة (اختياري)
@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': f'/image/{filename}'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 5. صفحة رئيسية (للترحيب)
@app.route('/')
def home():
    return jsonify({
        'name': 'Image API',
        'version': '1.0',
        'endpoints': {
            '/images': 'List all images',
            '/image/<filename>': 'Get specific image',
            '/random-image': 'Get random image',
            '/upload': 'Upload new image (POST)'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)