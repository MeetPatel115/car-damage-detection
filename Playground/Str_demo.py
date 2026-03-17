import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
import os

# Set up the folder and model path
folder_path = 'Phase 4'
model_path = os.path.join(folder_path, 'ft_model.keras')

# Load the TensorFlow model
model = tf.keras.models.load_model(model_path)

# Supported file extensions
allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}

# Function to check allowed file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Function to preprocess the image for the model
def preprocess_image(img):
    image = Image.open(img).convert('RGB')
    image = image.resize((224, 224))  # Resize to match the model's input size
    image = np.array(image) / 255.0  # Normalize the image
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

# Streamlit app layout
st.title("Image Damage Classification")

st.write("Upload an image to predict the damage class.")    

# File upload widget
uploaded_file = st.file_uploader("Choose an image file", type=['jpg', 'jpeg', 'png', 'gif'])

if st.button("Predict"):
    if uploaded_file is not None:
        if allowed_file(uploaded_file.name):
            try:
                # Display the uploaded image
                st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

                # Preprocess the image
                image = preprocess_image(uploaded_file)

                # Make prediction
                prediction = model.predict(image)
                damage_class = np.argmax(prediction)

                # Display the prediction result
                st.success(f"Predicted Damage Class: {damage_class}")
            except Exception as e:
                st.error(f"Error in processing the file: {e}")
        else:
            st.error("Invalid file format. Please upload a valid image.")
    else:
        st.error("Please upload an image before clicking 'Predict'.")