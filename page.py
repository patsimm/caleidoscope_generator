#!/usr/bin/python

import os, glob, sys, StringIO
from flask import Flask, request, redirect, url_for, send_file, render_template, abort
from werkzeug import secure_filename
from PIL import Image
from kaleidoscope import Kaleidoscope

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
           
def generate_upload_folder():
    upload_id = str(os.urandom(16).encode('hex'))
    while os.path.exists(os.path.join(UPLOAD_FOLDER, upload_id)):
        upload_id = str(os.urandom(16).encode('hex'))
    os.makedirs(os.path.join(UPLOAD_FOLDER, upload_id))
    return upload_id

@app.route('/', methods=['GET', 'POST'])
def upload_screen():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            extension = file.filename.rsplit('.', 1)[1]
            filename = "upload." + extension
            
            upload_id = generate_upload_folder()
            upload_folder = os.path.join(UPLOAD_FOLDER, upload_id)
            
            file.save(os.path.join(upload_folder, filename))
            return redirect(url_for('settings_screen', upload_id=upload_id))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
 
@app.route('/kldscp/<upload_id>')
def settings_screen(upload_id):
    if not os.path.exists(os.path.join(UPLOAD_FOLDER, upload_id)):
        abort(404)
    return render_template('settings_form.html', upload_id=upload_id)
    
@app.route('/image/<upload_id>', methods=['GET', 'POST'])
def gen_kaleidoscope(upload_id):
    upload_folder = os.path.join(UPLOAD_FOLDER, upload_id)
    if not os.path.exists(upload_folder):
        abort(404)
    upload_file = glob.glob(os.path.join(upload_folder, "upload.*"))[0]
    kaleidoscope = Kaleidoscope(Image.open(upload_file))
    
    rot = request.args.get('rot')
    msf = request.args.get('msf')
    mstr = request.args.get('mstr')
    mbl = request.args.get('mbl')
    bright = request.args.get('bright')
    if rot:
        kaleidoscope.rotations = int(rot)
    if msf:
        kaleidoscope.mask_size_factor = float(msf)
    if mstr:
        kaleidoscope.mask_strength = float(mstr)
    if mbl:
        kaleidoscope.mask_blur = int(mbl)
    if bright:
        kaleidoscope.brightness = float(bright)
    
    return send_file(kaleidoscope.get_bytes("PNG"), 
                     attachment_filename="kldscp.png",
                     as_attachment=False)

if __name__ == '__main__':
    app.debug = True
    app.run()
