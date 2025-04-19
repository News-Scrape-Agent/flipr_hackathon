import requests
import dotenv
import os
import re
from image import StableDiffusionGenerator

dotenv.load_dotenv()

def publish_blog(full_content: str, with_image: bool = False):
    client_id = os.getenv("WORDPRESS_CLIENT_ID")
    client_secret = os.getenv("WORDPRESS_CLIENT_SECRET")
    username = os.getenv("WORDPRESS_USERNAME")
    password = os.getenv("WORDPRESS_PASSWORD")
    # redirect_uri = os.getenv("WORDPRESS_REDIRECT_URI")  
    
    full_content = full_content[:5000]  # Limit content to 5000 characters

    title = full_content.split("\n")[0]  # Use the first line as the title
    content = "\n".join(full_content.split("\n")[1:])  # Use the rest as the content
    
    if not client_id or not client_secret or not username or not password:
        print("Missing environment variables. Please set the required variables and try again.")
        exit(1)

    token_url = "https://public-api.wordpress.com/oauth2/token"

    token_payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'password',
        'username': username,
        'password': password,
        # 'redirect_uri': redirect_uri, 
    }

    token_response = requests.post(token_url, data=token_payload)

    token_data = token_response.json()

    if "access_token" not in token_data:
        print("Error obtaining access token:", token_data)
        exit(1)

    access_token = token_data["access_token"]

    site = os.getenv("WORDPRESS_SITE_URL")
    post_endpoint = f"https://public-api.wordpress.com/rest/v1.1/sites/{site}/posts/new"

    if with_image:
        image_gen_model = StableDiffusionGenerator(prompt=title)
        image_path = image_gen_model.generate_and_save()

        media_url = f"https://public-api.wordpress.com/rest/v1.1/sites/{site}/media/new"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        with open(image_path, 'rb') as img:
            response = requests.post(media_url, headers=headers, files={'media[]': img})

        media_data = response.json()
        image_url = media_data['media'][0]['URL']
        # Add the image URL to the content
        content = f'<img src="{image_url}" alt="Alt text" style="max-width:100%; height:auto;">' + content 

    # Data for the new blog post
    post_data = {
        "title": title,
        "content": content,
        "status": "publish"  # Use "draft" if you want to save it without publishing immediately
    }

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    post_response = requests.post(post_endpoint, data=post_data, headers=headers, timeout=5)
    if post_response.status_code == 201 or post_response.status_code == 200:
        print("Post published successfully!")
    else:
        print("Failed to publish post.")
        print("Status Code:", post_response.status_code)
        print("Response:", post_response.text)
