import requests
import dotenv
import os
import re

dotenv.load_dotenv()

def publish_blog(full_content: str):
    client_id = os.getenv("WORDPRESS_CLIENT_ID")
    client_secret = os.getenv("WORDPRESS_CLIENT_SECRET")
    username = os.getenv("WORDPRESS_USERNAME")
    password = os.getenv("WORDPRESS_PASSWORD")
    # redirect_uri = os.getenv("WORDPRESS_REDIRECT_URI")  
    
    pattern = r'\*\*Title:\*\*(.*?)\*\*'
    full_content = full_content[:5000]  # Limit content to 5000 characters
    title = full_content.split("\n")[0]  # Use the first line as the title
    match = re.search(pattern, title, re.DOTALL)
    if match:
        title =  match.group(1).strip()
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

    site = "yash2310blog.wordpress.com"
    post_endpoint = f"https://public-api.wordpress.com/rest/v1.1/sites/{site}/posts/new"

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
