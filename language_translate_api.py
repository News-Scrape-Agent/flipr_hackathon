import requests
import textwrap
import dotenv
import time
import os

dotenv.load_dotenv()

language_codes = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Russian": "ru",
    "Chinese (Simplified)": "zh",
    "Chinese (Traditional)": "zh-TW",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Hindi": "hi",
    "Bengali": "bn",
    "Urdu": "ur",
    "Turkish": "tr",
    "Persian": "fa",
    "Greek": "el",
    "Hebrew": "he",
    "Polish": "pl",
    "Swedish": "sv",
    "Danish": "da",
    "Finnish": "fi",
    "Norwegian": "no",
    "Hungarian": "hu",
    "Czech": "cs",
    "Slovak": "sk",
    "Thai": "th",
    "Vietnamese": "vi",
    "Indonesian": "id",
    "Malay": "ms",
    "Filipino": "fil",
    "Swahili": "sw"
}

def translate_text(text, target_lang = "hindi", source_lang='en'):
    target_lang = language_codes.get(target_lang)
    print(target_lang)
    if not target_lang:
        return "Sorry, the target language is not supported"
    
    url = "https://api.mymemory.translated.net/get"
    params = {
        "q": text,
        "langpair": f"{source_lang}|{target_lang}",
        "key": os.getenv('MYMEMORY_TRANSLATE_KEY')
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json()
        if 'matches' in result and result['matches']:
            return result['responseData']['translatedText']
        else:
            return "Translation not found"
    else:
        return f"Error: {response.status_code}"

def translate_all_blogs_api(blogs, args):
    if (args.get('language')):
        target_lang = args.get('language')
        
        if target_lang.lower() == 'english':
            return blogs
        
        translated_blogs = []
        for blog in blogs:
            chunks = textwrap.wrap(blog, 250)  # Split blog into 250-character chunks
            translated_chunks = [translate_text(chunk, target_lang.capitalize()) for chunk in chunks]
            translated_blog = " ".join(translated_chunks)  # Concatenate translated chunks
            translated_blogs.append(translated_blog)
            time.sleep(1)
        return translated_blogs
    
    else:
        return blogs