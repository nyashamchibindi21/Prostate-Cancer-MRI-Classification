import streamlit as st
import numpy as np
import tensorflow as tf
import pydicom
import PIL.Image as Image
import io

# Set Streamlit Page Config
st.set_page_config(page_title="Prostate Cancer Classifier", layout="wide")

# Load Model
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("prostate_cancer_classification_model.h5")

model = load_model()

# Sidebar
with st.sidebar:
    st.header("🔍 About This Tool")
    st.write(
        "This AI-powered tool helps classify MRI scans of the prostate as **Normal** or **Suspicious** using deep learning."
    )
    st.markdown("---")
    st.subheader("📌 Instructions")
    st.write("1️⃣ Upload an MRI scan (DICOM, JPG, or PNG).")
    st.write("2️⃣ AI will analyze and classify the scan.")
    st.write("3️⃣ View the prediction result and confidence score.")
    st.write("4️⃣ Consult a medical expert for further advice.")
    st.markdown("---")
    st.write("⚠️ **Disclaimer:** This is not a medical diagnosis tool.")

# Function to process image
def load_image(uploaded_file):
    try:
        file_bytes = uploaded_file.read()

        if uploaded_file.name.endswith('.dcm'):
            dicom_data = pydicom.dcmread(io.BytesIO(file_bytes))
            image_array = dicom_data.pixel_array
            image_array = ((image_array - image_array.min()) / (image_array.max() - image_array.min()) * 255).astype(np.uint8)
            image = Image.fromarray(image_array)
        else:
            image = Image.open(io.BytesIO(file_bytes))

        # Resize to model input size (224x224)
        image = image.convert("RGB").resize((224, 224))
        return image
    
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None

# Function to predict
def predict(image):
    img_array = np.array(image) / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    prediction = model.predict(img_array)[0]

    # Assuming binary classification
    classes = ["Normal", "Suspicious"]
    confidence = float(prediction[0])
    label = classes[int(confidence > 0.5)]
    return label, confidence

# Main Layout
st.title("🔬 Prostate Cancer MRI Classification")

uploaded_file = st.file_uploader("📤 Upload an MRI Scan (DICOM/JPG/PNG)", type=["dcm", "jpg", "png"])

if uploaded_file:
    image = load_image(uploaded_file)
    if image:
        st.image(image, caption="🖼️ Uploaded MRI", use_column_width=True)
        st.write("🔄 Processing...")

        label, confidence = predict(image)

        st.write(f"### 🎯 Prediction: **{label}**")
        st.write(f"🧠 Confidence Score: **{confidence:.2f}**")

        if label == "Suspicious":
            st.warning("⚠️ The scan shows signs of prostate cancer. Please consult a medical professional for further analysis.")
        else:
            st.success("✅ The scan appears normal. However, always follow up with a medical expert.")

        # Next Steps Section
        st.markdown("---")
        st.subheader("🩺 Next Steps")
        st.write("📌 **If the scan is suspicious:**")
        st.write("• Consult a radiologist for expert evaluation.")
        st.write("• Consider scheduling further diagnostic tests.")
        st.write("• Discuss treatment options with a medical professional.")

        st.write("📌 **If the scan is normal:**")
        st.write("• Maintain regular medical checkups.")
        st.write("• Follow healthy lifestyle practices to prevent risks.")
        st.write("• Always consult a doctor if you experience symptoms.")

