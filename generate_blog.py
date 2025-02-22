import scrapers_call
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

model = ChatOllama(model="llama3.2:3b", temperature=0.4, num_ctx=2048)

# Create the prompt template for the AI model
prompt_template = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are an expert journalist who writes concise, engaging, and informative news blog posts. Your goal is to summarize the news while maintaining clarity, factual accuracy, and a compelling narrative."),
    HumanMessage(content="""  
    **Headline:** {headline}  
    **News Content:** {content}  

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

# Function to generate blog post
def generate_news_blog(headline, content):
    prompt = prompt_template.format_messages(headline=headline, content=content)
    response = model.invoke(prompt)
    return response.content

