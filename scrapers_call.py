"""
This script is used to call the scrapers 
for the different websites as per 
LLMs Response of User's Query.
"""
import asyncio
import pandas as pd
import chainlit as cl
from bert_labelling import predict_category
from process_user_query import find_location_in_user_query, normalize_topic_param
from scrapers.latest_news_scrapers import india_tv_scraper, indian_express_scraper, ndtv_scraper, mint_scraper, news18_scraper, sportskeeda
from scrapers.location_news_scrapers import india_tv_cities_scraper, ndtv_city_scraper, news18city, tribuneindiacity
from scrapers.topic_news_scrapers import indianexpress, livemint, news18, tribuneindia


# Run selected scrapers based on user query
SCRAPER_TIMEOUT = 60

# Wrapper for running each scraper safely
async def run_scraper(name, scraper_fn):
    try:
        msg = cl.Message(content=f"⏳ Running `{name}` scraper...")
        await msg.send()

        result = await asyncio.wait_for(scraper_fn, timeout=SCRAPER_TIMEOUT)

        msg.content = f"✅ `{name}` completed. Scraped {len(result)} articles."
        await msg.update()
        return result

    except asyncio.TimeoutError:
        msg.content = f"⚠️ `{name}` timed out after {SCRAPER_TIMEOUT}s."
        await msg.update()
        return []

    except Exception as e:
        msg.content = f"❌ `{name}` failed with error: {str(e)}"
        await msg.update()
        return []


# Main function that runs all selected scrapers
async def run_selected_scrapers(query: dict) -> list:
    raw_data = []

    # -------- Latest News --------
    if query.get('latest_news'):
        latest_tasks = await asyncio.gather(
            run_scraper("India TV", india_tv_scraper.india_tv_news_scraper()),
            run_scraper("Indian Express", indian_express_scraper.indian_express_scraper()),
            run_scraper("NDTV", ndtv_scraper.ndtv_scraper()),
            run_scraper("Livemint", mint_scraper.livemint_scraper()),
            run_scraper("News18", news18_scraper.news18_scraper()),
            run_scraper("Sportskeeda", sportskeeda.sportskeeda_scraper())
        )
        for news in latest_tasks:
            raw_data.extend(news[:2])

    # -------- Location News --------
    if query.get('location'):
        location = query['location']
        location_tasks = await asyncio.gather(
            run_scraper("India TV (City)", india_tv_cities_scraper.india_tv_news_cities_scraper(location=location)),
            run_scraper("NDTV (City)", ndtv_city_scraper.ndtv_cities_scraper(location=location)),
            run_scraper("News18 (City)", news18city.news18_cities_scraper(location=location)),
            run_scraper("Tribune India (City)", tribuneindiacity.tribune_city_scraper(location=location)),
        )
        for news in location_tasks:
            raw_data.extend(news[:2])

    # -------- Topic News --------
    if query.get('topic'):
        topic = query['topic']
        topic_tasks = await asyncio.gather(
            run_scraper("Indian Express (Topic)", indianexpress.indian_express_topic_scraper(topics=topic)),
            run_scraper("Livemint (Topic)", livemint.livemint_topic_scraper(topics=topic)),
            run_scraper("News18 (Topic)", news18.news18_topic_scraper(topics=topic)),
            run_scraper("Tribune India (Topic)", tribuneindia.tribune_topic_scraper(topics=topic)),
        )
        for news in topic_tasks:
            raw_data.extend(news[:2])

    return raw_data

# Function to apply post-processing
def post_process_results(df: pd.DataFrame, query: list) -> pd.DataFrame:
    
    # Apply BERT Inference to predict the category of news articles
    df['title'] = df['title'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    df['content'] = df['content'].apply(lambda x: x.strip() if isinstance(x, str) else x)

    df['title'] = df['title'].fillna("").astype(str)
    df["content"] = df["content"].fillna("").astype(str)
    
    df["news_label"] = df["content"].apply(predict_category)
    df.to_csv('labelled_news_data.csv')

    # TODO: Process the DataFrame based on the query
    # In each row of raw_data, must remove leading and trailing spaces from content in every column
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
    filtered_news_data = post_process_results(df, query)
    filtered_news_data.to_csv('filtered_news_data.csv')

    return filtered_news_data
