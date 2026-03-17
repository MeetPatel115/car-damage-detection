#import all the nessaccary liabraries 
from flask import Flask, request, render_template, jsonify, send_from_directory, flash
from PIL import Image
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import io
import base64
import pickle
#making the app instance
app = Flask(__name__)

# calling the model and asssigning the variable to each model
model_paths = ['Models/ft_model_2.keras', 'Models/ft_model_3.keras', 'Models/ft_model_4.keras']  # Add all model paths
models = [tf.keras.models.load_model(path) for path in model_paths]

# Image preprocessing function
def recounstracring_img(img_path):
    image = Image.open(img_path).convert('RGB')
    image = image.resize((256, 256))  # Adjust size to match your model's input
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image


# Dictionary to map class indices to car parts
labels = [
    # {
    #     0: True,
    #     1: False
    # },
    {
        0: False,
        1: True
    },
    {
        0: 'Front',
        1: 'Rear',
        2: 'Side'
    },
    {
        0: 'Minor',
        1: 'Moderate',
        2: 'Severe'
    }
]

# Prediction function
def predict(model, file_path, model_index = 0):
    converted_image = recounstracring_img(file_path)
    prediction = model.predict(converted_image)
    print(prediction)
    damage_class = np.argmax(prediction)
    damage_label = labels[model_index].get(damage_class, 'unknown')


    # Prepare the image for displaying
    image_array_display = np.squeeze(converted_image)
    plt.imshow(image_array_display)
    plt.title(f"Predicted Class: {damage_class}")
    plt.axis('off')

    # Save the plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()

    return {
        "prediction": prediction.tolist(),
        "damage_class": int(damage_class),
        "damage_label":damage_label,
        "image_base64": image_base64
    }

# Route for file upload and prediction
@app.route('/assessment', methods=['GET', 'POST'])
def upload_and_predict():
    if 'file' not in request.files:
        print('First if.')
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        file.save(file.filename)

        predictions = list()
        model_index = 0
        for model in models:
            result = predict(model, file.filename, model_index = model_index)
            print('Predicted Result:', result)
            predictions.append(result)
            print('Model Result', result['damage_class'], result['damage_label'])
            model_index += 1

        # Collect results from all models
        result = [
            predictions[0]['damage_label'],  # The predicted label from the first model
            predictions[1]['damage_label'],
            predictions[2]['damage_label']
        ]

        if result[0]:
            result[1] = result[2] = 'Unknown'

        print(result)

        # Return the results to the template
        return render_template('result.html', result=result, scroll='third', filename=file.filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

 #checking the submit button if not working then it will return the index   
@app.route('/assessment')
def assess():
    return render_template('index_demo.html',result=None,scroll='third')
#checking the <a> tag of the html if found then give the value of it
@app.route('/available/<a>')
def available(a):
    # Implement the logic based on 'a'
    return f"You selected: {a}"
#checking the file name 
@app.route('/send_file/<filename>')
def send_file(filename):
    return send_from_directory('Phase 4', filename)

# Home route
@app.route('/')
def home():
    return render_template('index_demo.html')  # Create an HTML form for file upload
#calling the main object of the code
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)