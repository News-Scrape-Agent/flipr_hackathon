import requests
import dotenv
import os

dotenv.load_dotenv()

def translate_text(text, target_lang='fr', source_lang='en'):
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

text = "Work hard and party harder"
translated = translate_text(text, target_lang='hindi')
print(translated)  