"""
This script is used to call the scrapers for the different websites as per LLMs Response of User's Query.
"""
import os
import importlib
import pandas as pd
from pathlib import Path

# Leave Indian Express City Scraper as its giving Timeout Error
# Leave NDTV Search Scraper as Too much hardcoding is required

def load_scrapers(folder_path):
    scrapers = []
    folder = Path(folder_path)
    
    if folder.exists():
        for file in folder.glob("*.py"):
            module_name = f"{folder.name}.{file.stem}"  # Convert path to module name
            module = importlib.import_module(module_name)  # Import dynamically
            if hasattr(module, "run_scraper"):
                scrapers.append(module.run_scraper)  # Add function reference
                
    return scrapers

# Load all scrapers from respective folders
topic_news_scrapers = load_scrapers("scrapers/topic_news_scrapers")
latest_news_scrapers = load_scrapers("scrapers/latest_news_scrapers")
location_news_scrapers = load_scrapers("scrapers/location_news_scrapers")

# Function to run selected scrapers based on user query
def run_selected_scrapers(query):
    results = []

    if query['topic']:
        for scraper in topic_news_scrapers:
            results.extend(scraper(query))

    if "latest_news" in query:
        for scraper in latest_news_scrapers:
            results.extend(scraper(query))

    if "location" in query:
        for scraper in location_news_scrapers:
            results.extend(scraper(query))
    
    return results

# Function to apply post-processing
# TODO: Implement case for all 3 in query and also using csv file check if city or state is present in the content
def post_process_results(data, query):
    df = pd.read_csv('indian_cities_and_states.csv')

    if query['topic'] and "location" in query:
        data = [item for item in data if query["location"].lower() in item["content"].lower()]
    
    if query['topic'] and query['latest_news']:
        data = [item for item in data if query["topic"].lower() in item["content"].lower()]
    
    return data

# Main function to handle the pipeline
def scrape_and_process(query):
    raw_data = run_selected_scrapers(query)
    processed_data = post_process_results(raw_data, query)
    return processed_data

def get_news(args):
    """
    Get the news based on the arguments provided.
    
    Arguments:
    - args: Dictionary containing the topic, location, latest or not.
    
    Returns:
    - news: A list of news articles.
    """
    latest_news = args.get('latest_news', False)
    topics = args.get('topics', [])
    locations = args.get('locations', 'delhi')
    query = {"latest_news" : latest_news, "topics" : topics, "locations" : locations}
    news = scrape_and_process(query)
    return news
