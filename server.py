from flask import Flask, request, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
import time

app = Flask(__name__, static_url_path='')

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制文件大小为16MB

# 允许的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def serve_html():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        # 使用时间戳和原始文件名创建新的文件名
        filename = f"{int(time.time())}_{secure_filename(file.filename)}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({
            'filename': filename,
            'url': f'/uploads/{filename}'
        })
    
    return jsonify({'error': '不支持的文件类型'}), 400

@app.route('/uploads/<filename>', methods=['GET', 'DELETE'])
def handle_uploaded_file(filename):
    if request.method == 'GET':
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    elif request.method == 'DELETE':
        try:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return jsonify({'message': '文件已删除'}), 200
            else:
                return jsonify({'error': '文件不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/images')
def get_images():
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(filename):
            files.append({
                'filename': filename,
                'url': f'/uploads/{filename}'
            })
    return jsonify(files)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000) 