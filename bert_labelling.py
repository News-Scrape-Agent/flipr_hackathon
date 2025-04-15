import torch
import pickle
import os
import gdown
import zipfile
import warnings
from dotenv import load_dotenv
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification

warnings.filterwarnings("ignore")

load_dotenv()

# Load tokenizer and model
MODEL_DIR = os.getenv("MODEL_DIR") 
gdrive_file_id = "1FTyhLrMiHEawCVfklvjOJsb2Tt5lNt0D" 
zip_path = "bert_model.zip"

# Check if folder exists
if not os.path.exists(MODEL_DIR):
    print(f"'{MODEL_DIR}' not found. Downloading from Google Drive...")

    # Download from Google Drive using gdown
    gdown.download(f"https://drive.google.com/uc?id={gdrive_file_id}", zip_path, quiet=False)

    # Extract ZIP into bert_model/
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(MODEL_DIR)

    # Clean up
    os.remove(zip_path)
    print(f"Model downloaded and extracted to {MODEL_DIR}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

# Load LabelEncoder to map numeric predictions back to category names
label_encoder_path = os.path.join(MODEL_DIR, "label_encoder.pkl")
with open(label_encoder_path, "rb") as f:
    encoder = pickle.load(f)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def predict_category(text):
    """Function to predict category of given text."""
    # Tokenize input text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    
    # Move tensors to device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Run inference
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Get predicted class index
    predicted_class_idx = torch.argmax(outputs.logits, dim=-1).item()
    
    # Convert index to category name
    predicted_category = encoder.classes_[predicted_class_idx]
    
    return predicted_category.lower()