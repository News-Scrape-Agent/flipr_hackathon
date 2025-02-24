import pandas as pd
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

model = ChatOllama(model="llama3.2:3b", temperature=0.4, num_ctx=2048)

def create_blog_prompt(title, content):
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

# Function to generate blog post
def generate_news_blog(news_data: pd.DataFrame) -> list:
    blogs = []
    for _, row in news_data.iterrows():
        # Create the prompt for each row
        prompt = create_blog_prompt(row['title'], row['content'])
        response = model.invoke(prompt)
        blogs.append(response.content)

    return blogs

