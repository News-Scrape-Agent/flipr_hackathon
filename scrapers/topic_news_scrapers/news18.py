import aiohttp
import asyncio
from bs4 import BeautifulSoup

# URL of the website
URL = "https://www.news18.com/topics"

async def news18_topic_scraper(url: str = URL, topics: list = [], max_articles: int = 5) -> list:
    async with aiohttp.ClientSession() as session:
        headers = {"User-Agent": "Mozilla/5.0"}

        links = []
        print("🔍 Searching for topic based news on News18")

        for topic in topics:
            print(f"🔍 Searching for: {topic}")
            topic_formatted = topic.replace(" ", "-").lower()
            topic_url = f"{url}/{topic_formatted}/"
            
            try:
                async with session.get(topic_url, headers=headers) as response:
                    if response.status != 200:
                        print(f"Failed to fetch topic {topic} (HTTP {response.status})")
                        continue
                        
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    list_items = soup.find_all("li", class_="jsx-894ab2deeb1b9f4a")
                    topic_links = [item.find("a")["href"] if item.find("a") else "No link" for item in list_items]

                    topic_links = topic_links[:min(max_articles, len(topic_links))]
                    links.append((topic_links, topic))
            except Exception as e:
                print(f"Error fetching topic {topic}: {e}")
                continue

        news = []
        for topic_links, topic in links:
            for link in topic_links:
                try:
                    async with session.get(link) as article_response:
                        if article_response.status != 200:
                            print(f"Failed to fetch article {link} (HTTP {article_response.status})")
                            continue
                            
                        article_html = await article_response.text()
                        soup = BeautifulSoup(article_html, 'html.parser')

                        h2_tag = soup.find('h2', id=lambda x: x and x.startswith('asubttl'))
                        h2_text = h2_tag.get_text() if h2_tag else 'No <h2> tag found'

                        story_paras = soup.find_all('p', class_=lambda x: x and x.startswith('story_para_'))
                        story_texts = [para.get_text() for para in story_paras]
                        article_text = ' '.join(story_texts)

                        first_published = soup.find('ul', class_='fp')
                        first_published_text = first_published.get_text(strip=True) if first_published else 'No First Published date found'

                        news.append({'title': h2_text, 'date_time': first_published_text, 'content': article_text})
                        
                except Exception as e:
                    print(f"Error processing article {link}: {e}")
                    continue

    print("Scraping complete. Total articles scraped:", len(news))
    return news