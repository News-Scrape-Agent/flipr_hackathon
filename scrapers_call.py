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


# Main function to run all selected scrapers based on user query
async def run_selected_scrapers(query: dict) -> list:
    raw_data = []

    # -------- Latest News --------
    if query.get('latest_news'):
        if query['latest_news']:
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
def post_process_results(df: pd.DataFrame, query: dict) -> pd.DataFrame:
    
    # Apply BERT Inference to predict the category of news articles
    df = df.dropna(subset=['content'])
    
    # Strip whitespace from all string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Special handling for content and date_time columns
    df['content'] = df['content'].fillna("").astype(str)
    df['title'] = df['title'].fillna("").astype(str)
    
    # Clean up date_time column - remove timezone info (+05:30)
    df['date_time'] = df['date_time'].fillna("")
    df['date_time'] = df['date_time'].astype(str).apply(lambda x: x.replace('+05:30', '').strip() if isinstance(x, str) else x)
    
    # Predict news categories
    df["news_label"] = df["content"].apply(predict_category)
    df.to_csv('labelled_news_data.csv')

    # Initialize variables to track what we have
    has_location = query.get('location') not in [None, [], '']
    has_latest = query.get('latest_news')
    has_topic = query.get('topic') not in [None, [], '']
    
    # Make a copy to avoid warnings
    processed_df = df.copy()
    
    # Create a standardized date column if possible
    try:
        # Try various date formats - use a more robust approach for production
        processed_df['parsed_date'] = pd.to_datetime(
            processed_df['date_time'], 
            errors='coerce',
            format='mixed'  # Try to infer format
        )
    except:
        # If date parsing fails, create a column with current date
        processed_df['parsed_date'] = pd.Timestamp.now()

    # Process based on the query combination
    if has_location and not has_latest and not has_topic:
        # Case 1: If only Location: then give priority to rows having location
        if 'location' in processed_df.columns:
            locations_lower = [loc.lower() for loc in query['location']]
            mask = processed_df['location'].astype(str).str.lower().isin(locations_lower)
            if mask.any():
                processed_df = processed_df[mask]
        
    elif not has_location and has_latest and not has_topic:
        # Case 2: If only Latest News: sort by date_time
        processed_df = processed_df.sort_values(by='parsed_date', ascending=False)
        
    elif not has_location and not has_latest and has_topic:
        # Case 3: If only Topic: check both news_label and content for the topics
        matched_indices = set()
        
        for topic in query['topic']:
            # Find rows where news_label contains the topic (case insensitive)
            label_matches = processed_df[
                processed_df['news_label'].str.lower().str.contains(topic.lower())
            ].index.tolist()
            
            # Find rows where content contains the topic (case insensitive)
            content_matches = processed_df[
                processed_df['content'].str.lower().str.contains(topic.lower())
            ].index.tolist()
            
            # Add all matches to our set
            matched_indices.update(label_matches)
            matched_indices.update(content_matches)
        
        # Filter the DataFrame to only include matched rows
        if matched_indices:
            processed_df = processed_df.loc[list(matched_indices)].drop_duplicates()
        
    elif has_location and has_latest and not has_topic:
        # Case 4: If Location + Latest News: select rows with location and then sort by date_time
        if 'location' in processed_df.columns:
            locations_lower = [loc.lower() for loc in query['location']]
            mask = processed_df['location'].astype(str).str.lower().isin(locations_lower)
            if mask.any():
                processed_df = processed_df[mask]
            
        # Sort by date_time regardless of location match
        processed_df = processed_df.sort_values(by='parsed_date', ascending=False)
        
    elif has_location and not has_latest and has_topic:
        # Case 5: If Location + Topic: select rows with location and then check both news_label and content
        location_df = processed_df
        
        if 'location' in processed_df.columns:
            locations_lower = [loc.lower() for loc in query['location']]
            mask = processed_df['location'].astype(str).str.lower().isin(locations_lower)
            if mask.any():
                location_df = processed_df[mask]
        
        matched_indices = set()
        
        for topic in query['topic']:
            # Check both news_label and content for matches
            label_matches = location_df[
                location_df['news_label'].str.lower().str.contains(topic.lower())
            ].index.tolist()
            
            content_matches = location_df[
                location_df['content'].str.lower().str.contains(topic.lower())
            ].index.tolist()
            
            matched_indices.update(label_matches)
            matched_indices.update(content_matches)
        
        if matched_indices:
            # Filter to matched rows and get top 5 from each label
            topic_df = location_df.loc[list(matched_indices)].drop_duplicates()
            processed_df = topic_df.groupby('news_label').apply(
                lambda x: x.nlargest(5, 'parsed_date')
            ).reset_index(drop=True)
        else:
            # No topic matches, keep location filtered results
            processed_df = location_df
        
    elif not has_location and has_latest and has_topic:
        # Case 6: If Topic + Latest News: check both news_label and content
        matched_indices = set()
        
        for topic in query['topic']:
            # Check both news_label and content for the topic
            label_matches = processed_df[
                processed_df['news_label'].str.lower().str.contains(topic.lower())
            ].index.tolist()
            
            content_matches = processed_df[
                processed_df['content'].str.lower().str.contains(topic.lower())
            ].index.tolist()
            
            matched_indices.update(label_matches)
            matched_indices.update(content_matches)
        
        if matched_indices:
            # Filter to matched rows and sort by date
            topic_df = processed_df.loc[list(matched_indices)].drop_duplicates()
            processed_df = topic_df.sort_values(by='parsed_date', ascending=False)
        else:
            # No topic matches, sort all by date
            processed_df = processed_df.sort_values(by='parsed_date', ascending=False)
        
    elif has_location and has_latest and has_topic:
        # Case 7: If Location + Latest News + Topic: check location, then both news_label and content
        location_df = processed_df
        
        if 'location' in processed_df.columns:
            locations_lower = [loc.lower() for loc in query['location']]
            mask = processed_df['location'].astype(str).str.lower().isin(locations_lower)
            if mask.any():
                location_df = processed_df[mask]
        
        matched_indices = set()
        
        for topic in query['topic']:
            # Check both news_label and content for the topic
            label_matches = location_df[
                location_df['news_label'].str.lower().str.contains(topic.lower())
            ].index.tolist()
            
            content_matches = location_df[
                location_df['content'].str.lower().str.contains(topic.lower())
            ].index.tolist()
            
            matched_indices.update(label_matches)
            matched_indices.update(content_matches)
        
        if matched_indices:
            # Filter to matched rows and sort
            topic_df = location_df.loc[list(matched_indices)].drop_duplicates()
            processed_df = topic_df.sort_values(by=['news_label', 'parsed_date'], ascending=[True, False])
        else:
            # No topic matches, sort location results by date
            processed_df = location_df.sort_values(by='parsed_date', ascending=False)

    # Clean up temporary columns
    if 'parsed_date' in processed_df.columns:
        processed_df = processed_df.drop('parsed_date', axis=1)
    
    # Limit to a reasonable number of articles
    processed_df = processed_df.head(10)
    
    return processed_df


# Main function to handle the pipeline
def scrape_and_process(args: dict, user_query: str) -> pd.DataFrame:
    latest_news = args.get('latest_news', False)
    topics = normalize_topic_param(args.get('topic'))
    locations = find_location_in_user_query(args, user_query)
    language = args.get('language', 'english')

    query = {"latest_news" : latest_news, "topic" : topics, "location" : locations, "language" : language}
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
