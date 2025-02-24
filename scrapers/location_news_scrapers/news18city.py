import time
import requests
import difflib
from bs4 import BeautifulSoup

# URL of the website (Replace with the actual URL)
BASE_URL = "https://www.news18.com/cities/"

# List of predefined city news pages
CITIES = [
    "mumbai-news", "new-delhi-news", "bengaluru-news", "hyderabad-news",
    "chennai-news", "ahmedabad-news", "pune-news", "noida-news",
    "gurgaon-news", "kolkata-news", "jaipur-news", "lucknow-news",
    "patna-news", "kanpur-news"
]

def get_best_matching_city(user_city: str) -> str:
    """Finds the best match for the user-provided city name."""
    formatted_city = user_city[0].lower().replace(" ", "-") + "-news"
    match = difflib.get_close_matches(formatted_city, CITIES, n=1, cutoff=0.6)
    return match[0] if match else None

def news18_cities_scraper(base_url: str = BASE_URL, max_articles: int = 5, location: list = ["delhi"]) -> list:
    """Scrapes news articles for a specified city using fuzzy matching."""
    extracted_links = []
    headers = {"User-Agent": "Mozilla/5.0"}

    # Get the best-matching city name
    matched_city = get_best_matching_city(location)
    if not matched_city:
        print(f"No matching city found for '{location}'. Skipping scraping.")
        return []

    # Construct the city news URL
    url = f"{base_url}{matched_city}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch data for {matched_city} (HTTP {response.status_code})")
        return []

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all <li> elements with the given class
    list_items = soup.find_all("li", class_="jsx-bdfb1b623b8585e8")

    # Extract article links
    city_urls = []
    for item in list_items:
        link_tag = item.find("a")
        link = link_tag["href"] if link_tag else None
        if link and link.startswith("/"):
            link = f"https://www.news18.com{link}"
        if link:
            city_urls.append(link)

    # Store only up to `max_articles` unique links
    extracted_links = list(set(city_urls[:min(max_articles, len(city_urls))]))
        
    news = []
    for link in extracted_links:
        response = requests.get(link)

        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the <h2> tag content
        h2_tag = soup.find('h2', id=lambda x: x and x.startswith('asubttl'))
        h2_text = h2_tag.get_text() if h2_tag else 'No <h2> tag found'

        # Extract all text content from story_para_ classes
        story_paras = soup.find_all('p', class_=lambda x: x and x.startswith('story_para_'))
        story_texts = [para.get_text() for para in story_paras]
        article_text = ' '.join(story_texts)

        # Extract the "First Published" date and time
        first_published = soup.find('ul', class_='fp')
        first_published_text = first_published.get_text(strip=True) if first_published else 'No First Published date found'

        news.append({"title": h2_text, "date_time": first_published_text, "content": article_text})
    print("Scraping complete. Total articles:", len(news))
    return news