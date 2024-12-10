from flask import Flask, request, jsonify, send_from_directory, render_template_string, render_template,redirect,make_response,url_for
import os
import uuid
import numpy as np
from PIL import Image
from databse import UserRegistrationSystem

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
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    name = str(request.form.get('name'))
    pwd = str(request.form.get('pwd'))
    db = UserRegistrationSystem("users.db")
    code,msg=db.verify_login(name,pwd)
    if code == True:
        return redirect(url_for('goto_transfer', username=f'{name}'))
    else:
        response = make_response(f'<script>alert("{msg}");</script>')
        return response


#注册
@app.route('/register', methods=['POST',"GET"])
def register():
    name = str(request.form.get('username'))#username
    pwd = str(request.form.get('pwd'))#pwd
    db = UserRegistrationSystem("users.db")
    if name=="55b0a265-2b6d-8c2c-3494-2d0b85cabd38" and pwd=="55b0a265-2b6d-8c2c-3494-2d0b85cabd38":#测试用，重置已注册用户数据库
        db.clear()
        return
    code,msg=db.register(name,pwd)
    #注册成功
    if code == True:
        response = make_response(f'<script>alert("{msg}");</script>')
        return response
    else:
        response = make_response(f'<script>alert("{msg}");</script>')
        return response

@app.route('/goto_transfer')
def goto_transfer():
    name = request.args.get('name')
    print(f"{name}")
    return render_template('transfer.html')

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
    app.run(debug=True)