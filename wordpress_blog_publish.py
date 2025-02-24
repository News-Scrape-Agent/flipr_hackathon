import requests
import dotenv
import os


dotenv.load_dotenv()

client_id = os.getenv("WORDPRESS_CLIENT_ID")
client_secret = os.getenv("WORDPRESS_CLIENT_SECRET")
username = os.getenv("WORDPRESS_USERNAME")
password = os.getenv("WORDPRESS_PASSWORD")
# redirect_uri = os.getenv("WORDPRESS_REDIRECT_URI")  

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
    "title": "This is the second blog post",
    "content": "This is the content of my new blog post created via the REST API.",
    "status": "publish"  # Use "draft" if you want to save it without publishing immediately
}

headers = {
    "Authorization": f"Bearer {access_token}"
}

post_response = requests.post(post_endpoint, data=post_data, headers=headers)
if post_response.status_code == 201:
    print("Post published successfully!")
else:
    print("Failed to publish post.")
    print("Status Code:", post_response.status_code)
    print("Response:", post_response.text)
