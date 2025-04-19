import pandas as pd
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

# Function to generate blog post
def generate_news_blog(news_data: pd.DataFrame) -> list:
    blogs = []
    news_data = news_data
    for _, row in news_data.iterrows():
        # Create the prompt for each row
        prompt = create_blog_prompt(row['title'], row['content'])
        formatted_prompt = prompt.format_messages()
        response = model.invoke(formatted_prompt)
        blogs.append(response.content)

    formatted_blogs = format_blogs(blogs)
    final_news_data = pd.DataFrame(formatted_blogs, columns=['blog'])
    final_news_data.to_csv('final_news_data.csv', index=False)

    return formatted_blogs

