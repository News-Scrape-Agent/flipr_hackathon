import pandas as pd
import torch
from PIL import Image
from diffusers import StableDiffusionPipeline
import os

class StableDiffusionGenerator:
    def __init__(self, prompt, model_name="CompVis/stable-diffusion-v1-4", output_dir="generated_images"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        print(f"Loading model: {model_name}")
        self.pipe = StableDiffusionPipeline.from_pretrained(model_name)
        self.pipe = self.pipe.to(self.device)

        self.prompt = prompt

    def _generate_image(self):
        with torch.autocast(self.device):
            result = self.pipe(self.prompt)
        return result.images[0]

    def _save_image(self, image: Image.Image, filename: str):
        path = os.path.join(self.output_dir, filename)
        image.save(path)
        return path

    def generate_and_save(self, filename="summary.png"):
        print(f"Generating image for prompt: {self.prompt}")
        image = self._generate_image(self.prompt)
        return self._save_image(image, filename)