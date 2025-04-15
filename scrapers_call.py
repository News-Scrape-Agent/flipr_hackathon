"""
This script is used to call the scrapers 
for the different websites as per 
LLMs Response of User's Query.
"""
import asyncio
import pandas as pd
from bert_labelling import predict_category
from process_user_query import find_location_in_user_query, normalize_topic_param
from scrapers.latest_news_scrapers import india_tv_scraper, indian_express_scraper, ndtv_scraper, mint_scraper, news18_scraper, sportskeeda
from scrapers.location_news_scrapers import india_tv_cities_scraper, ndtv_city_scraper, news18city, tribuneindiacity
from scrapers.topic_news_scrapers import indianexpress, livemint, news18, tribuneindia


# Run selected scrapers based on user query
async def run_selected_scrapers(query: list) -> list:
    raw_data = []

    if query.get('latest_news'):
        latest_news_1 = india_tv_scraper.india_tv_news_scraper()
        latest_news_2 = indian_express_scraper.indian_express_scraper()
        latest_news_3 = asyncio.run(ndtv_scraper.ndtv_scraper())
        latest_news_4 = mint_scraper.livemint_scraper()
        latest_news_5 = news18_scraper.news18_scraper()
        latest_news_6 = asyncio.run(sportskeeda.sportskeeda_scraper())

        raw_data.extend(latest_news_1[:1] + latest_news_2[:1] + latest_news_3[:1] + latest_news_4[:1] + latest_news_5[:1] + latest_news_6[:1])

    if query.get('location'):
        location = query["location"]
        print(location)
        location_news_1 = india_tv_cities_scraper.india_tv_news_cities_scraper(location=location)
        location_news_2 = ndtv_city_scraper.ndtv_cities_scraper(location=location)
        location_news_3 = news18city.news18_cities_scraper(location=location)
        location_news_4 = asyncio.run(tribuneindiacity.tribune_city_scraper(location=location))

        raw_data.extend(location_news_1[:1] + location_news_2[:1] + location_news_3[:1] + location_news_4[:1])

    if query.get('topic'):
        topic_news_1 = asyncio.run(indianexpress.indian_express_topic_scraper(topics=query['topic']))
        topic_news_2 = asyncio.run(livemint.livemint_topic_scraper(topics=query['topic']))
        topic_news_3 = news18.news18_topic_scraper(topics=query['topic'])
        topic_news_4 = asyncio.run(tribuneindia.tribune_topic_scraper(topics=query['topic']))

        raw_data.extend(topic_news_1[:1] + topic_news_2[:1] + topic_news_3[:1] + topic_news_4[:1])

    return raw_data


# Function to apply post-processing
def post_process_results(data: list, query: list) -> pd.DataFrame:
    
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=['content'], keep='first').reset_index(drop=True)
    df.to_csv('processed_news_data.csv')
    return df


# Main function to handle the pipeline
def scrape_and_process(args: dict, user_query: str) -> pd.DataFrame:
    latest_news = args.get('latest_news', False)
    topics = normalize_topic_param(args.get('topic'))
    locations = find_location_in_user_query(args, user_query)

    query = {"latest_news" : latest_news, "topic" : topics, "location" : locations}
    print(query)
    raw_data = asyncio.run(run_selected_scrapers(query))
    filtered_data = post_process_results(raw_data, query)
    filtered_data = filtered_data[:min(15, len(filtered_data))]  # Limit to 15 rows
    # Apply inference to each row
    filtered_data["content"] = filtered_data["content"].fillna("").astype(str)
    filtered_data["predicted_category"] = filtered_data["content"].apply(predict_category)
    filtered_data.to_csv('filtered_news_data.csv')

    return filtered_data
