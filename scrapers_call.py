"""
This script is used to call the scrapers for the different websites as per LLMs Response of User's Query.
"""
import asyncio
import pandas as pd
from scrapers.latest_news_scrapers import india_tv_scraper, indian_express_scraper, ndtv_scraper, mint_scraper, news18_scraper, sportskeeda
from scrapers.location_news_scrapers import india_tv_cities_scraper, ndtv_city_scraper, news18city, tribuneindiacity
from scrapers.topic_news_scrapers import indianexpress, livemint, news18, tribuneindia

# Left Indian Express City Scraper as its giving Timeout Error
# Left NDTV Search Scraper as Too much hardcoding is required

latest_news_scrapers = [india_tv_scraper, indian_express_scraper, ndtv_scraper, mint_scraper, news18_scraper, sportskeeda]
location_news_scrapers = [india_tv_cities_scraper, ndtv_city_scraper, news18city, tribuneindiacity]
topic_news_scrapers = [indianexpress, livemint, news18, tribuneindia]

async def get_state(location):
    # Check if the location is a city
    df = pd.read_csv('indian_cities_and_states.csv')
    if location in df["cities"].values:
        return df.loc[df["cities"] == location, "state"].values[0].lower()
    else:
        return location.lower()
    
# Function to run selected scrapers based on user query
async def run_selected_scrapers(query):
    results = []

    if query['latest_news']:
        latest_news_1 = india_tv_scraper.india_tv_news_scraper()
        latest_news_2 = indian_express_scraper.indian_express_scraper()
        latest_news_3 = asyncio.run(ndtv_scraper.ndtv_scraper())
        latest_news_4 = mint_scraper.livemint_scraper()
        latest_news_5 = news18_scraper.news18_scraper()
        latest_news_6 = asyncio.run(sportskeeda.sportskeeda_scraper())

        results.extend([latest_news_1, latest_news_2, latest_news_3, latest_news_4, latest_news_5, latest_news_6])

    if "location" in query:
        location = query["location"]
        if isinstance(location, str):  # Ensure it's a list
            state = await get_state(location)
            if state.lower() != location.lower():
                location = [location, state]
            else:
                location = [location]

        location_news_1 = india_tv_cities_scraper.india_tv_news_cities_scraper(location=location)
        location_news_2 = ndtv_city_scraper.ndtv_cities_scraper(location=location)
        location_news_3 = news18city.news18_cities_scraper(location=location)
        location_news_4 = tribuneindiacity.tribune_city_scraper(location=location)

        results.extend([location_news_1, location_news_2, location_news_3, location_news_4])

    if query.get('topic'):
        topic_news_1 = asyncio.run(indianexpress.indian_express_topic_scraper(topics=query['topic']))
        topic_news_2 = asyncio.run(livemint.livemint_topic_scraper(topics=query['topic']))
        topic_news_3 = news18.news18_topic_scraper(topics=query['topic'])
        topic_news_4 = asyncio.run(tribuneindia.tribune_topic_scraper(topics=query['topic']))

        results.extend([topic_news_1, topic_news_2, topic_news_3, topic_news_4])
    
    return results

# Function to apply post-processing
# TODO: Implement case for all 3 in query and also using csv file check if city or state is present in the content
def post_process_results(data, query):
    state = get_state(query['location'])

    if query['topic'] and "location" in query:
        data = [item for item in data if query["location"].lower() in item["content"].lower()]
    
    if query['topic'] and query['latest_news']:
        data = [item for item in data if query["topic"].lower() in item["content"].lower()]
    
    return data

# Main function to handle the pipeline
async def scrape_and_process(query):
    raw_data = await run_selected_scrapers(query)
    # processed_data = post_process_results(raw_data, query)
    return raw_data
