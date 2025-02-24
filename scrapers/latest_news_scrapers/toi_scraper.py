import requests
from bs4 import BeautifulSoup
from datetime import datetime
import nltk

# Download necessary NLTK resources
nltk.download('punkt_tab')

# Function to categorize the news based on keywords
def categorize_news(headline, content):
    categories = {
        "Politics": ["election", "government", "policy", "politician"],
        "International News": ["world", "international", "foreign"],
        "National News": ["india", "national"],
        "Local News": ["local", "city", "town"],
        "Business and Finance": ["business", "finance", "market", "economy"],
        "Science and Technology": ["science", "technology", "tech", "research"],
        "Health and Wellness": ["health", "wellness", "medical", "fitness"],
        "Entertainment": ["entertainment", "movie", "film", "music"],
        "Sports": ["sport", "game", "tournament", "match"],
        "Lifestyle and Features": ["lifestyle", "feature", "trend"],
        "Opinion and Editorial": ["opinion", "editorial"],
        "Environment": ["environment", "climate", "nature"],
        "Education": ["education", "school", "college", "university"],
        "Crime and Justice": ["crime", "justice", "law", "court"],
        "Human Interest": ["human interest", "story", "people"],
        "Obituaries": ["obituary", "death", "passed away"],
        "Weather": ["weather", "forecast", "rain", "temperature"],
        "Religion and Spirituality": ["religion", "spirituality", "faith"],
        "Technology and Gadgets": ["technology", "gadget", "device"],
        "Automotive": ["car", "automobile", "vehicle"]
    }
    
    text = (headline + " " + content).lower()
    
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "General News"

def calculate_starttime(base_starttime, date):
    base_date = datetime(2010, 1, 1)
    target_date = datetime(date.year, date.month, date.day)
    delta = target_date - base_date
    return base_starttime + delta.days

# Function to fetch and parse the news articles for a specific date
def fetch_news(year, month, day, starttime):
    archive_url = f'https://timesofindia.indiatimes.com/{year}/{month}/{day}/archivelist/year-{year},month-{month},starttime-{starttime}.cms'
    print(f"Fetching news for {day}/{month}/{year} from URL: {archive_url}")
    try:
        response = requests.get(archive_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {archive_url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    span_tags = soup.find_all('span', style="font-family:arial ;font-size:12;color: #006699")
    if not span_tags:
        print(f"No articles found for {day}/{month}/{year}.")
    news_list = set()
    for span in span_tags:
        articles = span.find_all('a', href=True)
        for article in articles:
            article_url = article['href']
            if 'articleshow' not in article_url:
                continue
            if article_url.startswith('/'):
                article_url = f"https://timesofindia.indiatimes.com{article_url}"
                news_list.add(article_url)
    
    print(len(news_list), "new articles found for", day, month, year)
    return list(news_list)


base_starttime = 40179
start_year = 2025
start_month = 2
start_day = 19
current_date = datetime(start_year, start_month, start_day)
links = fetch_news(2025, 2, 19, calculate_starttime(base_starttime, current_date))