import aiohttp
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://www.indiatvnews.com/"

async def india_tv_news_cities_scraper(url: str = URL, max_articles: int = 5, location: list = ["delhi"]) -> list:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Failed to retrieve page, status code: {response.status}")
                    return []
                
                html = await response.text()
                news = []
                print("Searching for location based news on IndiaTV...")

                soup = BeautifulSoup(html, "html.parser")
                state_divs = soup.find_all("div", class_="box")
                state_div = state_divs[-1]
                state_links = [a["href"] for a in state_div.find_all("a", href=True)]
                
                for state_link in state_links:
                    try:
                        async with session.get(state_link, timeout=6) as state_response:
                            if state_response.status == 200:
                                state_html = await state_response.text()
                                state_soup = BeautifulSoup(state_html, "html.parser")
                                news_ul = state_soup.find_all("ul", class_="news-list")
                                news_links = [a["href"] for news_div in news_ul for a in news_div.find_all("a", href=True)]
                                
                                news_links = list(set(news_links))
                                news_links = news_links[:min(2 * max_articles, len(news_links))]
                                
                                ctr = 0
                                for news_link in news_links:
                                    if len(news_link.split('/')) != 5:
                                        continue
                                    try:
                                        async with session.get(news_link, timeout=6) as news_response:
                                            if news_response.status == 200:
                                                news_html = await news_response.text()
                                                news_soup = BeautifulSoup(news_html, "html.parser")
                                                
                                                headline = news_soup.find("h1", class_="arttitle")
                                                title = headline.text.strip() if headline else "No title found"
                                                
                                                date_time = news_soup.find("time")
                                                date_time = date_time["datetime"] if date_time else "No date found"
                                                if date_time != "No date found":
                                                    date_time = datetime.fromisoformat(date_time)
                                                
                                                content_div = news_soup.find("div", class_="content", id="content")
                                                if content_div:
                                                    paragraphs = content_div.find_all("p")
                                                    full_content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                                                else:
                                                    continue
                                                
                                                news.append({"title": title, "date_time": date_time, "content": full_content, "location": state_link.split('/')[-1]})
                                                ctr += 1
                                                if ctr >= max_articles:
                                                    break
                                                
                                            else:
                                                print(f"Failed to retrieve page, status code: {news_response.status}")
                                                continue
                                    except asyncio.TimeoutError:
                                        print(f"Timeout error for {news_link}")
                                        continue
                                    except Exception as e:
                                        print(f"Error processing {news_link}: {e}")
                                        continue
                            else:
                                print(f"Failed to retrieve page, status code: {state_response.status}")
                                continue
                    except asyncio.TimeoutError:
                        print(f"Timeout error for {state_link}")
                        continue
                    except Exception as e:
                        print(f"Error processing {state_link}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error getting the response from {url}: {e}")
            return []

    print("Scraping complete. Total articles scraped:", len(news))
    return news