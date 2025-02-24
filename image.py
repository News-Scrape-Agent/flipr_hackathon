import pandas as pd
import torch
from diffusers import StableDiffusionPipeline
import os

# summary_df = pd.read_csv("summaries.csv") 

# summary_df = summary_df.head(5)

# if "summary" not in summary_df.columns:
#     raise ValueError("The DataFrame does not contain a 'summary' column.")

# summary_df["summary"] = summary_df["summary"].fillna("").astype(str)

prompt = "A tense crime scene in an urban Indian neighborhood, with police officers surrounding "

# Load the Stable Diffusion model
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4").to(device)

# Create a directory to save images
output_dir = "generated_images"
os.makedirs(output_dir, exist_ok=True)

# Function to generate and save images
def generate_image(text):
    image = pipe(text).images[0]  # Generate image from text
    image_path = os.path.join(output_dir, f"summary.png")
    image.save(image_path)  # Save the image
    return image_path

# Generate images for each summary
# summary_df["image_path"] = summary_df["summary"].apply(lambda text: generate_image(text, summary_df.index[summary_df["summary"] == text][0]))

path = generate_image(prompt)

# # Display results
# print(summary_df[["summary", "image_path"]])
