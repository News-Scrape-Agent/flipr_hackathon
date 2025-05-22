import aiohttp
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://indianexpress.com/section/cities/"

async def indian_express_cities_scraper(url: str = URL, max_articles: int = 5, location: list = ["delhi"]) -> list:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Failed to retrieve page, status code: {response.status}")
                    return []
                
                html = await response.text()
                news = []
                print("Searching for location based news on Indian Express...")
                
                soup = BeautifulSoup(html, "html.parser")
                target_ul = soup.find("ul", class_="page_submenu")
                cities_url = [url + (str(a.text).lower()) + '/' for a in target_ul.find_all("a", href=True)]
                cities_url = cities_url[1:]
                
                for city_url in cities_url:
                    try:
                        async with session.get(city_url, timeout=10) as city_response:
                            if city_response.status == 200:
                                city_html = await city_response.text()
                                city_soup = BeautifulSoup(city_html, "html.parser")
                                new_div = city_soup.find("div", id="north-east-data")
                                if not new_div:
                                    continue
                                    
                                news_links = [a["href"] for a in new_div.find_all("a", href=True)]
                                news_links = list(set(news_links))
                                news_links = news_links[:min(2 * max_articles, len(news_links))]
                                
                                cnt = 0
                                for link in news_links:
                                    try:
                                        async with session.get(link, timeout=10) as link_response:
                                            if link_response.status == 200:
                                                link_html = await link_response.text()
                                                link_soup = BeautifulSoup(link_html, "html.parser")
                                                
                                                headline = link_soup.find("h1", itemprop="headline")
                                                title = headline.text if headline else "No title found"
                                                
                                                date_time_element = link_soup.find("span", itemprop="dateModified")
                                                date_time = date_time_element["content"] if date_time_element else "No date found"
                                                if date_time != "No date found":
                                                    date_time = datetime.fromisoformat(date_time)
                                                
                                                content_div = link_soup.find("div", id="pcl-full-content")
                                                if content_div:
                                                    paragraphs = content_div.find_all("p")
                                                    full_content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                                                else:
                                                    continue
                                                
                                                news.append({"title": title, "date_time": date_time, "content": full_content, "location": city_url.split('/')[-2]})
                                                cnt += 1
                                                if cnt >= max_articles:
                                                    break
                                                
                                            else:
                                                print(f"Failed to retrieve page, status code: {link_response.status}")
                                                continue
                                    except asyncio.TimeoutError:
                                        print(f"Timeout error for {link}")
                                        continue
                                    except Exception as e:
                                        print(f"Error processing {link}: {e}")
                                        continue
                            else:
                                print(f"Failed to retrieve page, status code: {city_response.status}")
                                continue
                    except asyncio.TimeoutError:
                        print(f"Timeout error for {city_url}")
                        continue
                    except Exception as e:
                        print(f"Error processing {city_url}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error getting the response from {url}: {e}")
            return []
    
    print("Scraping complete. Total articles scraped:", len(news))
    return news