import time
import dotenv
import asyncio
import logging
import chainlit as cl
from tools_config import tools
from scrapers_call import scrape_and_process
from generate_blog import generate_news_blog
from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from wordpress_blog_publish import publish_blog
from language_translate_api import translate_all_blogs_api
from language_translate_model import translate_all_blogs_streaming


dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the AI model
model = ChatOllama(model="llama3.2:3b", format="json", temperature=0.3, num_ctx=1024)
model = model.bind_tools(tools=tools)

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""
You are an AI assistant. When the human asks for news, decide three buckets:

1. latest_news: true if they want the most recent headlines (keywords: latest, today, current).
2. location: the place they mention, or empty if none.
3. topic: list drawn only from:
   ["sports", "world", "entertainment", "lifestyle",
    "politics", "environment", "crime", "business",
    "science", "health", "education" , ""].
4. language: the language they want news in, or empty if none.

Map user phrasing or synonyms (e.g. “tech” → “science”, “global” → “world”) to the closest canonical topic.  
If the user mentions multiple topics, include them all.  
If nothing matches, return an empty list.

Return via a single tool-call:
analyze_news_query(latest_news: <true/false>, location: "<place>", topic: [<…>])
"""),
    HumanMessagePromptTemplate.from_template("""  
Examples:
Q: “Show me the latest news in New Delhi.”  
→ analyze_news_query(latest_news: true,  location: "New Delhi", topic: [], language: "")

Q: “News about sports in Mumbai in hindi.”  
→ analyze_news_query(latest_news: false, location: "Mumbai", topic: ["sports"], language: "hindi")

Q: “Give me today’s headlines in hindi.”  
→ analyze_news_query(latest_news: true,  location: "", topic: [], language: "hindi")

Q: “Show me technology and gadgets news in english.”  
→ analyze_news_query(latest_news: false, location: "", topic: ["science"], language: "english")

Q: “What’s happening in finance and business?”  
→ analyze_news_query(latest_news: false, location: "", topic: ["business"], language: "")

Q: “Health updates and Covid stats today in gujrati.”  
→ analyze_news_query(latest_news: true, location: "", topic: ["health"], language: "gujrati")
                                             
Q: “Latest entertainment news in Tamil.”  
analyze_news_query(latest_news=True, location="", topic=["entertainment"], language="tamil")

Q: “What are the political updates from Kerala in Malayalam?”  
analyze_news_query(latest_news=False, location="Kerala", topic=["politics"], language="malayalam")

Q: “Show me sports news in Punjabi.”  
analyze_news_query(latest_news=False, location="", topic=["sports"], language="punjabi")

Q: “Tell me today’s headlines from Kolkata in Bengali.”  
analyze_news_query(latest_news=True, location="Kolkata", topic=[], language="bengali")

Now you respond on the user’s actual query:
“{input}”
"""),
])

# Function to process user queries
def process_query(query: str) -> str:
    """
    Processes user queries by invoking the AI model and calling appropriate functions,
    with a heuristic override for 'latest_news'.
    """
    logging.info(f"Processing query: {query}")

    # Heuristic: if the user mentions 'latest', 'today', or 'current', we want top headlines
    force_latest = any(token in query.lower() for token in ["latest", "today", "current"])

    # Build the prompt and call the model
    formatted_prompt = prompt.format_messages(input=query)
    logging.info(f"Formatted prompt: {formatted_prompt}")
    result = model.invoke(formatted_prompt)
    logging.info(result)

    # If the model chose to call our news-analysis tool:
    if result.tool_calls:
        for tool_call in result.tool_calls:
            tool_name = tool_call["name"]
            args = tool_call["args"]
            logging.info(f"Function call: {tool_name}, Args: {args}")

            if tool_name == "get_conversational_response":
                return args["response"]

            elif tool_name == "analyze_news_query":
                # Override the model’s flag if our heuristic tripped
                if force_latest:
                    logging.info("Heuristic detected 'latest' intent → forcing latest_news=True")
                    args["latest_news"] = True

                # Now call the scrapers
                news = scrape_and_process(args, query)
                blogs = asyncio.run(generate_news_blog(news))[:5]
                translated_blogs = asyncio.run(translate_all_blogs_streaming(blogs, args))
                # for blog in translated_blogs:
                #     publish_blog(blog)
                #     time.sleep(5)
                return

# Chainlit event handler for incoming messages
@cl.on_message
async def main(message: cl.Message):
    """
    Handles incoming user messages, processes them, and sends responses.

    Args:
    message (cl.Message): The incoming user message
    """
    logging.info(f"Received message: {message.content}")

    if message.content:
        query = message.content
        response = process_query(query)
        logging.info(f"Generated Response: {response}")
        await cl.Message(content=response).send()
