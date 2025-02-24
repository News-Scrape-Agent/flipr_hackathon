import torch
import pickle
import os
from dotenv import load_dotenv
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification

load_dotenv()

# Load tokenizer and model
MODEL_DIR = os.getenv("MODEL_DIR") 
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