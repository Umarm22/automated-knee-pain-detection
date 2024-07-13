import os
from flask import Flask, request, render_template, redirect, url_for, flash
from keras.models import load_model
import cv2
import numpy as np

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' 

model_path = 'model_improved.h5'
model = load_model(model_path)

uploads_dir = os.path.join(app.root_path, 'static/uploads')
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    resized = cv2.resize(img, (256, 256)) 
    normalized = resized / 255.0  
    return np.expand_dims(normalized, axis=-1) 

def get_actual_label(image_path):
   
    label_dict = {
        'image1.png': 'Normal',
        'image2.png': 'Doubtful',
        
    }
    filename = os.path.basename(image_path)
    return label_dict.get(filename, 'Unknown')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file:
            try:
               
                file_path = os.path.join(uploads_dir, file.filename)
                file.save(file_path)
                processed_image = preprocess_image(file_path)

                prediction = model.predict(np.array([processed_image]))
                predicted_class = np.argmax(prediction)
                severity_levels = ['Normal', 'Doubtful', 'Mild', 'Moderate', 'Severe']
                predicted_label = severity_levels[predicted_class]
                actual_label = get_actual_label(file_path)
                
                print(f"Predicted Label: {predicted_label}, Actual Label: {actual_label}, Image Path: {file_path}")
                return render_template('index.html', prediction=predicted_label, actual_label=actual_label, image='uploads/' + file.filename)
            except Exception as e:
                print(f"Error processing file: {e}")
                flash('An error occurred while processing the file')
                return redirect(request.url)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
