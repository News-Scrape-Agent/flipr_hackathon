import aiohttp
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://www.ndtv.com/"

async def ndtv_cities_scraper(url: str = URL, max_articles: int = 5, location: list = ["delhi"]) -> list:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=20) as response:
                if response.status != 200:
                    print("Failed to load main page")
                    return []
                
                html = await response.text()
                metros = []
                other_cities = []

                try:
                    soup = BeautifulSoup(html, "html.parser")
                    metro_elements = soup.select("div.dd-nav_in:not(.dd-nav_in-1-fl) ul.dd-nav_ul li a")
                    metros = [a.get("href") for a in metro_elements if a.get("href")][4:8]

                    other_elements = soup.select("div.dd-nav_in.dd-nav_in-1-fl ul.dd-nav_ul li a")
                    other_cities = [a.get("href") for a in other_elements if a.get("href")]
                except Exception as e:
                    print(f"Error parsing the main page: {e}")
                    return []

                cities_links = metros + other_cities
                news = []
                print("Searching for location based news on NDTV...")

                ctr = 0
                for city_link in cities_links:
                    try:
                        async with session.get(city_link, timeout=20) as city_resp:
                            if city_resp.status != 200:
                                print(f"Failed to load city page: {city_link}")
                                continue

                            city_html = await city_resp.text()
                            city_soup = BeautifulSoup(city_html, "html.parser")
                            news_links_elements = city_soup.select(".NwsLstPg_ttl-lnk")
                            links = list({a.get("href") for a in news_links_elements if a.get("href")})
                            links = list(set(links))
                            links = links[:min(2 * max_articles, len(links))]
                            
                            for article_link in links:
                                try:
                                    async with session.get(article_link, timeout=20) as article_resp:
                                        if article_resp.status != 200:
                                            print(f"Failed to load article page: {article_link}")
                                            continue

                                        article_html = await article_resp.text()
                                        article_soup = BeautifulSoup(article_html, "html.parser")
                                        
                                        heading_elem = article_soup.select_one("h1.sp-ttl")
                                        heading = heading_elem.get_text(strip=True) if heading_elem else "No title found"
                                        
                                        time_elem = article_soup.select_one("span[itemprop='dateModified']")
                                        date_time = time_elem.get('content') if time_elem else None
                                        if date_time:
                                            date_time = datetime.strptime(date_time, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
                                        else:
                                            date_time = 'No date found'
                                        
                                        parts = article_link.split("/")
                                        label = parts[3] if len(parts) > 3 else ""
                                        
                                        paragraphs = article_soup.select("div.Art-exp_cn p")
                                        content = " ".join(p.get_text(strip=True) for p in paragraphs)
                                        if not content:
                                            continue

                                        location = label[:-5] if label.endswith("-news") else label
                                        
                                        news.append({"title": heading, "date_time": date_time, "content": content, "location": location})
                                        ctr += 1
                                        if ctr >= max_articles:
                                            break
                                        
                                except Exception as e:
                                    print(f"Error processing article {article_link}: {e}")
                                    continue
                    except Exception as e:
                        print(f"Error processing city {city_link}: {e}")
                        continue

        except Exception as e:
            print(f"Error getting the response from {url}: {e}")
            return []
            
    print("Scraping complete. Total articles scraped:", len(news))
    return news