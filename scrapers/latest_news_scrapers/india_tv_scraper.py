import aiohttp
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://www.indiatvnews.com/latest-news"

async def india_tv_news_scraper(url: str = URL, max_articles: int = 5) -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Failed to retrieve page, status code: {response.status}")
                return []
            
            html = await response.text()
            news = []
            print("Searching for latest news on IndiaTV...")
            soup = BeautifulSoup(html, "html.parser")
            columns = soup.find_all("div", class_="box")
            
            links = []
            for column in columns[:-4]:
                links.extend([a['href'] for a in column.find_all("a", href=True)])
            
            links = list(set(links))
            links = links[:min(2 * max_articles, len(links))]

            ctr = 0
            for link in links:
                try:
                    async with session.get(link, timeout=6) as link_response:
                        if link_response.status == 200:
                            link_html = await link_response.text()
                            link_soup = BeautifulSoup(link_html, "html.parser")
                            
                            headline = link_soup.find("h1", class_="arttitle")
                            title = headline.text.strip() if headline else "No title found"
                            
                            date_time = link_soup.find("time")
                            date_time = date_time["datetime"] if date_time else "No date found"
                            if date_time != "No date found":
                                date_time = datetime.fromisoformat(date_time)
                            
                            content_div = link_soup.find("div", class_="content", id="content")
                            if content_div:
                                paragraphs = content_div.find_all("p")
                                full_content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                            else:
                                continue
                            
                            news.append({"title": title, "date_time": date_time, "content": full_content})
                            
                            ctr += 1
                            if ctr >= max_articles:
                                break
                        else:
                            print(f"Failed to retrieve page, status code: {link_response.status}")
                            continue
                except asyncio.TimeoutError:
                    print(f"Timeout error for link {link}")
                    continue
                except Exception as e:
                    print(f"Error processing {link}: {e}")
                    continue

    print("Scraping complete. Total articles scraped:", len(news))
    return news