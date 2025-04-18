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

        raw_data.extend(latest_news_1[:2] + latest_news_2[:2] + latest_news_3[:2] + latest_news_4[:2] + latest_news_5[:2] + latest_news_6[:2])

    if query.get('location'):
        location = query["location"]

        location_news_1 = india_tv_cities_scraper.india_tv_news_cities_scraper(location=location)
        location_news_2 = ndtv_city_scraper.ndtv_cities_scraper(location=location)
        location_news_3 = news18city.news18_cities_scraper(location=location)
        location_news_4 = asyncio.run(tribuneindiacity.tribune_city_scraper(location=location))

        raw_data.extend(location_news_1[:2] + location_news_2[:2] + location_news_3[:2] + location_news_4[:2])

    if query.get('topic'):
        topic_news_1 = asyncio.run(indianexpress.indian_express_topic_scraper(topics=query['topic']))
        topic_news_2 = asyncio.run(livemint.livemint_topic_scraper(topics=query['topic']))
        topic_news_3 = news18.news18_topic_scraper(topics=query['topic'])
        topic_news_4 = asyncio.run(tribuneindia.tribune_topic_scraper(topics=query['topic']))

        raw_data.extend(topic_news_1[:2] + topic_news_2[:2] + topic_news_3[:2] + topic_news_4[:2])

    return raw_data


# Function to apply post-processing
def post_process_results(df: pd.DataFrame, query: list) -> pd.DataFrame:
    
    # Apply BERT Inference to predict the category of news articles
    df["content"] = df["content"].fillna("").astype(str)
    df["news_label"] = df["content"].apply(predict_category)
    df.to_csv('labelled_news_data.csv')

    # TODO: Process the DataFrame based on the query
    # For date_time fixing, we can hardcode time extraction for each scraper and obtain universal time format
    # If only Location: then give priority to rows having location
    # If only Latest News: sort by date_time
    # If only Topic: sort by news_label
    # If Location + Latest News: select rows with location and then sort by date_time
    # If Location + Topic: select rows with location and then group by news_label and select top 2 from each group
    # If Topic + Latest News: select rows with req. news_label and then sort by date_time
    # If Location + Latest News + Topic: select rows with location first then group by req. news_label and then sort by date_time


    return df


# Main function to handle the pipeline
def scrape_and_process(args: dict, user_query: str) -> pd.DataFrame:
    latest_news = args.get('latest_news', False)
    topics = normalize_topic_param(args.get('topic'))
    locations = find_location_in_user_query(args, user_query)

    query = {"latest_news" : latest_news, "topic" : topics, "location" : locations}
    print(query)

    # Call the scrapers and collect raw news data
    raw_data = asyncio.run(run_selected_scrapers(query))
    df = pd.DataFrame(raw_data)
    df = df.drop_duplicates(subset=['content'], keep='first').reset_index(drop=True)
    df.to_csv('raw_news_data.csv')

    # Filter the raw news data based on user query
    final_news_data = post_process_results(df, query)
    final_news_data.to_csv('final_news_data.csv')

    return final_news_data
