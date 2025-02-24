import torch
import pickle
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd

# Load tokenizer and model
MODEL_DIR = "trained_model"  
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

# Load LabelEncoder to map numeric predictions back to category names
with open("label_encoder.pkl", "rb") as f:
    encoder = pickle.load(f)

# Set device (CPU/GPU)
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
    
    return predicted_category

# Example inference
text_sample = "The stock market saw a major rise today after the announcement."
predicted_label = predict_category(text_sample)
print(f"Predicted Category: {predicted_label}")

articles = pd.read_csv("news.csv")
articles = articles.head(5)

articles["content"] = articles["content"].fillna("").astype(str)

# Apply inference to each row
articles["predicted_category"] = articles["content"].apply(predict_category)

# Display results
print(articles)
