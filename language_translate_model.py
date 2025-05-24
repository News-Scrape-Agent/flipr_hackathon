import torch
import dotenv
import asyncio
import chainlit as cl
from threading import Thread
from LangTransModel.processor import IndicProcessor
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, TextIteratorStreamer

dotenv.load_dotenv()

user_lang_to_flores = {
    "assamese": "asm_Beng",
    "bengali": "ben_Beng",
    "bhojpuri": "bho_Deva",
    "dogri": "doi_Deva",
    "english": "eng_Latn",
    "gujarati": "guj_Gujr",
    "hindi": "hin_Deva",
    "kannada": "kan_Knda",
    "kashmiri": "kas_Deva",
    "konkani": "gom_Deva",
    "maithili": "mai_Deva",
    "malayalam": "mal_Mlym",
    "marathi": "mar_Deva",
    "manipuri": "mni_Mtei",
    "nepali": "npi_Deva",
    "odia": "ory_Orya",
    "oriya": "ory_Orya",
    "punjabi": "pan_Guru",
    "sanskrit": "san_Deva",
    "santali": "sat_Olck",
    "sindhi": "snd_Deva",
    "tamil": "tam_Taml",
    "telugu": "tel_Telu",
    "urdu": "urd_Arab",
    "chhattisgarhi": "hne_Deva",
    "magahi": "mag_Deva",
    "mizo": "lus_Latn",
    "khasi": "kha_Latn",
    "mundari": "unr_Deva",
    "gondi": "gon_Deva",
    "awadhi": "awa_Deva",
    "bodo": "brx_Deva"
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

src_lang, tgt_lang = "eng_Latn", "hin_Deva"
model_name = "ai4bharat/indictrans2-en-indic-dist-200M"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

model = AutoModelForSeq2SeqLM.from_pretrained(model_name, trust_remote_code=True, torch_dtype=torch.float16).to(DEVICE)

ip = IndicProcessor(inference=True)

def to_async_iter(sync_iterable, delay=0):
    async def gen():
        for item in sync_iterable:
            yield item
            if delay:
                await asyncio.sleep(delay)
    return gen()

# Function to translate a single blog with streaming output
async def translate_blog_streaming(blog_text: str, tgt_lang: str, blog_idx: int, total_blogs: int):
    # Create a message for this translation
    msg = cl.Message(content=f"⏳ Translating blog {blog_idx+1}/{total_blogs} to {tgt_lang.split('_')[0]}")
    await msg.send()
    
    preprocessed = ip.preprocess_batch([blog_text], src_lang=src_lang, tgt_lang=tgt_lang)[0]
    
    # Track the translation progress
    translated_text = ""
    
    # Setup the streamer
    streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True, timeout=10.0)
    
    inputs = tokenizer(preprocessed, return_tensors="pt", truncation=True, padding=True).to(DEVICE)
    
    # Start generation in a separate thread
    generation_kwargs = {
        **inputs,
        "streamer": streamer,
        "max_length": 512,
        "num_beams": 1,         # num_beams support only value = 1 for streaming currently
        "temperature": 0.7,     # Add some temperature to compensate for lack of beam search
        "top_p": 0.9,           # Use nucleus sampling for better quality without beam search
    }
    
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()
    
    # Stream the translation
    try:
        # Show progress indicator
        progress_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        progress_idx = 0
        
        # Stream tokens as they're generated
        for token in streamer:
            translated_text += token
            if len(translated_text) % 10 == 0:  # Update UI every 10 characters
                progress_char = progress_chars[progress_idx % len(progress_chars)]
                msg.content = f"{progress_char} Translating: {translated_text}..."
                await msg.update()
                progress_idx += 1
                await asyncio.sleep(0.01)  # Keep connection alive
                
        final_text = ip.postprocess_batch([translated_text], lang=tgt_lang)[0]
        
        msg.content = f"✅ Translation {blog_idx+1}/{total_blogs}:\n\n{final_text}"
        await msg.update()
        
        return final_text, msg
        
    except Exception as e:
        msg.content = f"❌ Translation error: {str(e)}"
        await msg.update()
        return None, msg

# Main function to translate all blogs with streaming UI updates
async def translate_all_blogs_streaming(blogs: list, args) -> list:
    if args.get('language'):
        target_lang = args.get('language')
        
        if target_lang.lower() == 'english':
            return blogs
        
        tgt_lang = user_lang_to_flores.get(target_lang.lower())
        print(tgt_lang)
        if not tgt_lang:
            error_msg = cl.Message(content=f"⚠️ Language '{target_lang}' is not supported.")
            await error_msg.send()
            return blogs
            
        main_msg = cl.Message(content=f"🌐 Starting translation to {target_lang}")
        await main_msg.send()
        
        translated_blogs = []
        total_blogs = len(blogs)
        
        for i, blog in enumerate(blogs):
            translated_blog, blog_msg = await translate_blog_streaming(blog, tgt_lang, i, total_blogs)
            if translated_blog:
                translated_blogs.append(translated_blog)
            else:
                translated_blogs.append(blog)
                
            # Small delay between translations
            await asyncio.sleep(0.3)
            
        # Update the main message
        main_msg.content = f"✅ Translated {len(translated_blogs)} blogs to {target_lang}"
        await main_msg.update()
            
        return translated_blogs
    
    else:
        return blogs