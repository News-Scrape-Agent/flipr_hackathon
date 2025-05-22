import aiohttp
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://indianexpress.com/latest-news"

async def indian_express_scraper(url: str = URL, num_pages: int = 3, num_articles: int = 5) -> list:
    async with aiohttp.ClientSession() as session:
        # First get main page
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Failed to retrieve page, status code: {response.status}")
                return []
            
            news = []
            print("Searching for latest news on Indian Express...")
            
            links = []
            # Gather links from multiple pages
            for i in range(1, num_pages):
                try:
                    page_url = f"{url}/page/{i}/"
                    async with session.get(page_url, timeout=6) as page_response:
                        if page_response.status == 200:
                            page_html = await page_response.text()
                            page_soup = BeautifulSoup(page_html, "html.parser")
                            
                            target_div = page_soup.find("div", class_="nation")
                            if target_div:
                                divs = target_div.find_all("div")
                                links.extend([a["href"] for div in divs for a in div.find_all("a", href=True)])
                        else:
                            print(f"Failed to retrieve page, status code: {page_response.status}")
                except asyncio.TimeoutError:
                    print(f"Timeout error for page {i}")
                except Exception as e:
                    print(f"Error processing page {i}: {e}")

            links = list(set(links))
            
            cnt = 0
            # Process article links
            for link in links:
                try:
                    async with session.get(link, timeout=6) as link_response:
                        if link_response.status == 200:
                            link_html = await link_response.text()
                            link_soup = BeautifulSoup(link_html, "html.parser")
                            
                            headline = link_soup.find("h1", itemprop="headline")
                            title = headline.get_text(strip=True) if headline else "No title found"
                            
                            date_time_element = link_soup.find("span", itemprop="dateModified")
                            date_time = date_time_element.get("content", "No date found") if date_time_element else "No date found"
                            if date_time != "No date found":
                                date_time = datetime.fromisoformat(date_time)
                            
                            content_div = link_soup.find("div", id="pcl-full-content")
                            if content_div:
                                paragraphs = content_div.find_all("p")
                                full_content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                            else:
                                continue
                            
                            news.append({"title": title, "date_time": date_time, "content": full_content})
                            cnt += 1
                            if cnt >= num_articles:
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