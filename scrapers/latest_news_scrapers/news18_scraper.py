import aiohttp
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup

# URL of the website
URL = "https://www.news18.com/news/"

async def news18_scraper(url: str = URL, max_articles: int = 5) -> list:
    # Send a request to the website
    headers = {"User-Agent": "Mozilla/5.0"}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Failed to retrieve page, status code: {response.status}")
                return []
            
            # Parse the HTML
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            
            # Find all <li> elements with the given class
            list_items = soup.find_all("li", class_="jsx-1976791735")
            
            extracted_links = []
            # Extract and print the text content and links
            for item in list_items:
                try:
                    link_tag = item.find("a")  # Find the <a> tag
                    link = link_tag["href"] if link_tag else "No link"  # Get the href attribute if available
                    if link.startswith("/"):
                        link = f"https://www.news18.com{link}"
                    extracted_links.append(link)
                except Exception as e:
                    continue
            
            news = []
            print("Searching for latest news on News18...")
            extracted_links = extracted_links[:min(2 * max_articles, len(extracted_links))]

            ctr = 0
            for link in extracted_links:
                try:
                    async with session.get(link) as article_response:
                        if article_response.status != 200:
                            print(f"Failed to retrieve article, status code: {article_response.status}")
                            continue
                            
                        # Parse the HTML content of the webpage
                        article_html = await article_response.text()
                        article_soup = BeautifulSoup(article_html, 'html.parser')
                        
                        h2_tag = article_soup.find('h2', id=lambda x: x and x.startswith('asubttl'))
                        h2_text = h2_tag.get_text() if h2_tag else 'No title found'

                        first_published = article_soup.find('ul', class_='fp')
                        date_time = first_published.get_text(strip=True) if first_published else None
                        if date_time:
                            dt = date_time.replace("First Published:", "").replace(",", "").replace("IST", "").strip()
                            date_time = datetime.strptime(dt, "%B %d %Y %H:%M")
                        else:
                            date_time = "No date found"
                        
                        story_paras = article_soup.find_all('p', class_=lambda x: x and x.startswith('story_para_'))
                        story_texts = [para.get_text() for para in story_paras]
                        if (len(story_texts) == 0):
                            continue
                        article_text = ' '.join(story_texts)
                        
                        news.append({'title': h2_text, 'date_time': date_time, 'content': article_text})
                        ctr += 1
                        if ctr >= max_articles:
                            break
                        
                except Exception as e:
                    print(f"Error processing article {link}: {e}")
                    continue
    
    print("Scraping complete. Total articles scraped:", len(news))
    return news