import time
import logging
from scrapers_call import scrape_and_process
from generate_blog import generate_news_blog
from language_translate_api import translate_all_blogs
import chainlit as cl
from tools_config import tools
from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
import dotenv
from wordpress_blog_publish import publish_blog


dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the AI model
model = ChatOllama(model="llama3.2:3b", format="json", temperature=0.3, num_ctx=1024)
model = model.bind_tools(tools=tools)

# Create the prompt template for the AI model
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a helpful AI assistant. Use the provided tools when necessary else respond with your own knowledge. Also don't tell answer for illegal queries"),
    HumanMessagePromptTemplate.from_template("{input}"),
])

# Function to process user queries
def process_query(query: str) -> str:
    """
    Processes user queries by invoking the AI model and calling appropriate functions.
    """
    logging.info(f"Processing query: {query}")
    formatted_prompt = prompt.format_messages(input=query)
    logging.info(f"Formatted prompt: {formatted_prompt}")
    result = model.invoke(formatted_prompt)
    logging.info(result)
    
    if result.tool_calls:
        for tool_call in result.tool_calls:
            function_name = tool_call['name']
            args = tool_call['args']
            logging.info(f"Function call: {function_name}, Args: {args}")

            if function_name == "get_conversational_response":
                return args['response']
            
            elif function_name == 'analyze_news_query':
                news = scrape_and_process(args, query)
                blogs = generate_news_blog(news)
                translated_blogs = translate_all_blogs(blogs, args)
                for blog in translated_blogs:
                    publish_blog(blog)
                    time.sleep(5)
                return translated_blogs

    return result.content

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
