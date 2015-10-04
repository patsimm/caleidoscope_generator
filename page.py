import os, glob
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from PIL import Image
from caleidoscope import Caleidoscope

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.debug = True
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
            return '''
            <img src=%s />
            ''' % url_for('open_caleidoscope', upload_id=upload_id)

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
    
@app.route('/uploads/<upload_id>')
def open_caleidoscope(upload_id):
    upload_folder = os.path.join(UPLOAD_FOLDER, upload_id)
    upload_file = glob.glob(os.path.join(upload_folder, "upload.*"))[0]
    caleidoscope = Caleidoscope(Image.open(upload_file))
    
    extension = upload_file.rsplit('.', 1)[1]
    cal_img = caleidoscope.generate()
    cal_img_path = os.path.join(upload_folder, "tmp." + extension)
    cal_img.save(cal_img_path)
    return send_from_directory(upload_folder, "tmp." + extension)

if __name__ == '__main__':
	app.run()
