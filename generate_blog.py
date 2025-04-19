import asyncio
import pandas as pd
import chainlit as cl
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

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

# Function to generate a blog with streaming to keep connection alive
async def generate_blog_streaming(prompt_messages, row_title):
    # Create a message that will be updated with streaming content
    msg = cl.Message(content=f"⏳ Generating blog for: **{row_title}**")
    await msg.send()
    
    # To track the generated content
    generated_text = ""
    
    # Stream the response
    try:
        # Use invoke instead of stream for better compatibility
        # Keep the connection alive by periodically updating the UI
        update_interval = 0.5  # Update UI every 0.5 seconds
        start_time = asyncio.get_event_loop().time()
        
        # Start a background task
        generation_task = asyncio.create_task(model.ainvoke(prompt_messages))
        
        # Update the UI periodically while waiting for the completion
        while not generation_task.done():
            current_time = asyncio.get_event_loop().time()
            elapsed = current_time - start_time
            
            # Update the message with time elapsed
            msg.content = f"⏳ Generating blog for: **{row_title}** ({elapsed:.1f}s elapsed)"
            await msg.update()
            
            # Wait a bit before updating again
            await asyncio.sleep(update_interval)
        
        # Get the result once complete
        response = await generation_task
        generated_text = response.content
        
    except Exception as e:
        msg.content = f"❌ Error generating blog: {str(e)}"
        await msg.update()
        return None, msg
    
    return generated_text, msg

# Main blog generation function
async def generate_news_blog(news_data: pd.DataFrame) -> list:
    # Process articles with a delay between them to keep connection alive
    total_articles = len(news_data)
    formatted_blogs = []
    
    for i, (_, row) in enumerate(news_data.iterrows()):
        # Create a progress update for this article
        article_progress_msg = cl.Message(content=f"⏳ Processing article {i+1}/{total_articles}: **{row['title'][:40]}...**")
        await article_progress_msg.send()
        
        # Keep connection alive with a small delay
        await asyncio.sleep(0.1)
        
        # Create the prompt for each row
        prompt = create_blog_prompt(row['title'], row['content'])
        formatted_prompt = prompt.format_messages()
        
        # Generate blog with streaming to keep connection alive
        blog_content, article_msg = await generate_blog_streaming(formatted_prompt, row['title'][:40])
        
        if blog_content:
            # Format the blog for display
            formatted_blog = format_blogs([blog_content])[0]
            
            # Update the message with the final generated blog - correct way
            article_msg.content = f"**Blog {i+1}/{total_articles}**\n\n{formatted_blog}"
            await article_msg.update()
            
            # Add to our blog messages list
            formatted_blogs.append(formatted_blog)
            
        else:
            # Update progress - correct way
            article_progress_msg.content = f"❌ Failed to generate blog for article {i+1}/{total_articles}"
            await article_progress_msg.update()
        
        # Keep connection alive between articles
        await asyncio.sleep(0.5)
    
    # Save to CSV
    final_news_data = pd.DataFrame(formatted_blogs, columns=['blog'])
    final_news_data.to_csv('final_news_data.csv', index=False)
    
    return formatted_blogs