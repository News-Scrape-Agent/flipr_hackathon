import aiohttp
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup

# URL of the website
URL = "https://www.livemint.com/latest-news"

async def livemint_scraper(url: str = URL, num_articles: int = 5) -> list:
    # Send a request to the website
    headers = {"User-Agent": "Mozilla/5.0"}
    news = []
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Failed to retrieve page, status code: {response.status}")
                    return news
                
                # Parse the HTML
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                print("Searching for latest news on Live Mint...")
                
                # Find all <li> elements with the given class
                articles = soup.find_all("div", class_="listingNew")
                
                links = []
                for article in articles:
                    # Find the h2 tag inside div with class 'headline'
                    h2_tag = article.find("h2", class_="headline")
                    if h2_tag:
                        # Find the <a> tag inside <h2>
                        a_tag = h2_tag.find("a")
                        if a_tag and "href" in a_tag.attrs:
                            link = a_tag["href"]
                            full_link = f"https://www.livemint.com{link}" if link.startswith("/") else link
                            links.append(full_link)

                cnt = 0
                # Process each article link
                for url in links:
                    try:
                        async with session.get(url) as article_response:
                            if article_response.status == 200:
                                # Parse the HTML content of the webpage
                                article_html = await article_response.text()
                                article_soup = BeautifulSoup(article_html, 'html.parser')
                                
                                # Extract the <h1> tag content
                                h1_tag = article_soup.find('h1', id="article-0")
                                h1_text = h1_tag.get_text() if h1_tag else 'No title found'
                                
                                # Extract all text content from story_para_ classes
                                story_paras = article_soup.find_all('div', class_="storyParagraph", id=lambda x: x and x.startswith('article-index'))
                                if (len(story_paras) == 0):
                                    continue

                                story_texts = [para.get_text() for para in story_paras]
                                article_text = ' '.join(story_texts)
                                
                                # Extract the "First Published" date and time
                                first_published = article_soup.find('div', class_=lambda x: x and x.startswith('storyPage_date'))
                                first_published_text = first_published.get_text(strip=True) if first_published else "No date found"

                                for prefix in ["Updated", "Published"]:  # optional fallback if prefix changes
                                    if first_published_text.startswith(prefix):
                                        dt = first_published_text.replace(prefix, "").replace("IST", "").replace(",", "").strip()
                                        date_time = datetime.strptime(dt, "%d %b %Y %I:%M %p")
                                    else:
                                        date_time = first_published_text
                                
                                news.append({'title': h1_text, 'date_time': date_time, 'content': article_text})
                                cnt += 1
                                if cnt >= num_articles:
                                    break

                            else:
                                print(f"Failed to retrieve the article, status code: {article_response.status}")
                    except Exception as e:
                        print(f"An error occurred while scraping the article {url}: {e}")
        except Exception as e:
            print(f"An error occurred while scraping the website: {e}")
        
    print("Scraping complete. Total articles scraped:", len(news))
    return news