import asyncio
import pandas as pd
import chainlit as cl
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

model = ChatOllama(model="llama3.2:3b", temperature=0.4, num_ctx=2048)

# Function to format the blogs
def format_blogs(blogs: list) -> list:
    formatted = []
    for blog in blogs:
        title = blog.split("\n")[0]
        content = "\n".join(blog.split("\n")[1:])

        if title.startswith("**Title:**"):
            title = title.replace("**Title:**", "").strip()
        elif title.startswith("**") and title.endswith("**"):
            title = title[2:-2]

        if content.startswith("**Content:**"):
            content = content.replace("**Content:**", "").strip()
        elif content.startswith("**") and content.endswith("**"):
            content = content[2:-2]

        formatted.append(f"{title}\n\n{content}")
    
    return formatted

# Function to create the prompt for generating blog posts
def create_blog_prompt(title: str, content: str) -> ChatPromptTemplate:
    if title:
        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are an expert journalist who writes concise, engaging, and informative news blog posts. Your goal is to summarize the news while maintaining clarity, factual accuracy, and a compelling narrative."),
            HumanMessage(content=f"""
            **Headline:** {title}
            **Content:** {content}

            Generate a concise blog-style article (50-100 words). Keep it engaging, factual, and to the point while preserving key details.
            - Start with a strong lead sentence summarizing the news.
            - Provide key details in a coherent flow (who, what, where, when, why).
            - Avoid fluff—keep it concise and impactful.
            - End with a brief analysis, quote, or future implication if relevant.

            **Output Format:**  
            - **Title:** (Use a catchy, yet accurate title)
            - **Content:** (Concise, well-structured blog post in 50-100 words)
            """)
        ])
    else:
        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are an expert journalist who writes concise, engaging, and informative news blog posts. Your goal is to summarize the news while maintaining clarity, factual accuracy, and a compelling narrative."),
            HumanMessage(content=f"""
            **Content:** {content}

            Generate a concise blog-style article (50-100 words). Keep it engaging, factual, and to the point while preserving key details.
            - Start with a strong lead sentence summarizing the news.
            - Provide key details in a coherent flow (who, what, where, when, why).
            - Avoid fluff—keep it concise and impactful.
            - End with a brief analysis, quote, or future implication if relevant.

            **Output Format:**  
            - **Title:** (Use a catchy, yet accurate title)
            - **Content:** (Concise, well-structured blog post in 50-100 words)
            """)
        ])
    
    return prompt_template

def to_async_iter(sync_iterable, delay=0):
    async def gen():
        for item in sync_iterable:
            yield item
            if delay:
                await asyncio.sleep(delay)
    return gen()

# Function to generate a blog with streaming to keep connection alive
async def generate_blog_streaming(prompt_messages, row_title):
    # Create a message that will be updated with streaming content
    msg = cl.Message(content=f"⏳ Generating blog for: **{row_title}**")
    await msg.send()
    
    # To track the generated content
    generated_text = ""
    
    # Function to handle each token as it's generated
    async def handle_token(token: str):
        nonlocal generated_text
        generated_text += token
        # Update the message every few tokens to avoid too many updates
        if len(token) > 0 and len(generated_text) % 10 == 0:
            msg.content = f"⏳ Generating: {generated_text}..."
            await msg.update()
            # Send a keep-alive signal every few tokens
            await asyncio.sleep(0.01)
    
    # Stream the response
    try:
        stream = model.stream(prompt_messages)
        stream = to_async_iter(model.stream(prompt_messages), delay=0.01)
        async for chunk in stream:
            if chunk.content:
                await handle_token(chunk.content)
                # Small delay to prevent overloading
                await asyncio.sleep(0.01)
    except Exception as e:
        msg.content = f"❌ Error generating blog: {str(e)}"
        await msg.update()
        return None, msg
    
    return generated_text, msg

# Main blog generation function
async def generate_news_blog(news_data: pd.DataFrame) -> list:
    total_articles = len(news_data)
    formatted_blogs = []
    
    for i, (_, row) in enumerate(news_data.iterrows()):
        article_progress_msg = cl.Message(content=f"⏳ Processing article {i+1}/{total_articles}: **{row['title'][:40]}...**")
        await article_progress_msg.send()
        
        # Keep connection alive with a small delay
        await asyncio.sleep(0.1)
        
        # Create the prompt for each row
        prompt = create_blog_prompt(row['title'], row['content'])
        formatted_prompt = prompt.format_messages()
        
        blog_content, article_msg = await generate_blog_streaming(formatted_prompt, row['title'][:40])
        
        if blog_content:
            formatted_blog = format_blogs([blog_content])[0]
            
            article_msg.content = f"**Blog {i+1}/{total_articles}**\n\n{formatted_blog}"
            await article_msg.update()
            
            formatted_blogs.append(formatted_blog)
            
        else:
            # Update progress
            article_progress_msg.content = f"❌ Failed to generate blog for article {i+1}/{total_articles}"
            await article_progress_msg.update()
        
        # Keep connection alive between articles
        await asyncio.sleep(0.5)
    
    # Save to CSV
    final_news_data = pd.DataFrame(formatted_blogs, columns=['blog'])
    final_news_data.to_csv('final_news_data.csv', index=False)
    
    return formatted_blogs