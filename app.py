from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import uuid
import numpy as np
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template_string('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image and Text Upload</title>
    <meta http-equiv="refresh" content="0;url=/static/index.html">
</head>
<body>
</body>
</html>''')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'image1' not in request.files or 'image2' not in request.files or 'text' not in request.form:
        return jsonify({'success': False}), 400

    file1 = request.files['image1']
    file2 = request.files['image2']

    if file1.filename == '' or file2.filename == '':
        return jsonify({'success': False}), 400

    if file1 and allowed_file(file1.filename):
        filename1 = uuid.uuid4().hex + '_' + file1.filename
        file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))

    if file2 and allowed_file(file2.filename):
        filename2 = uuid.uuid4().hex + '_' + file2.filename
        file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))

    text = request.form['text']

    # img can get the picture
    img = Image.open(f'./uploads/{filename1}')

    image_urls = [
        f'/uploads/{filename1}'
    ]

    return jsonify({'success': True, 'images': image_urls})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Copy index.html to static folder for serving directly
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    with open(os.path.join(app.static_folder, 'index.html'), 'w') as f:
        f.write(html_content)

    app.run(debug=True)