import aiohttp
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

URL = "https://www.livemint.com/search"

async def livemint_topic_scraper(url: str = URL, topics: list = [], max_articles: int = 5) -> list:
    links = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        print("🔍 Searching for topic based news on Live Mint")
        for topic in topics:
            print(f"🔍 Searching for: {topic}")

            await page.fill("#searchField", topic)
            await page.press("#searchField", "Enter")
            await page.wait_for_selector(".listingNew", timeout=10000)

            # Extract article links from 'h2.headline a'
            topic_links = await page.eval_on_selector_all(
                ".listingNew h2.headline a",
                "elements => elements.map(el => el.href)"
            )

            await asyncio.sleep(2)
            links.append((topic_links[:min(max_articles, len(topic_links))], topic))

        await browser.close()

    news = []
    async with aiohttp.ClientSession() as session:
        for topic_links, topic in links:
            for url in topic_links:
                try:
                    async with session.get(url) as response:
                        if response.status != 200:
                            print(f"Failed to retrieve {url}, status code: {response.status}")
                            continue
                            
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        h1_tag = soup.find('h1', id="article-0")
                        headh1_tag = soup.find('h1', class_="headline")
                        
                        if h1_tag:
                            h1_text = h1_tag.get_text()
                            story_paras = soup.find_all('div', class_="storyParagraph", id=lambda x: x and x.startswith('article-index'))
                            story_texts = [para.get_text() for para in story_paras]
                            article_text = ' '.join(story_texts)

                            first_published = soup.find('div', class_=lambda x: x and x.startswith('storyPage_date'))
                            first_published_text = first_published.get_text(strip=True) if first_published else 'No First Published date found'
                        elif headh1_tag:
                            h1_text = headh1_tag.get_text()
                            story_paras = soup.find_all('div', class_="liveSecIntro")
                            story_texts = [para.get_text() for para in story_paras]
                            article_text = ' '.join(story_texts)

                            first_published = soup.find('span', class_="articleInfo pubtime fl")
                            first_published_text = first_published.get_text(strip=True) if first_published else 'No First Published date found'
                        else:
                            h1_text = 'No <h1> tag found'
                            article_text = 'No article text found'
                            first_published_text = 'No First Published date found'

                        news.append({'title': h1_text, 'date_time': first_published_text, 'content': article_text})
                        
                except Exception as e:
                    print(f"Error processing {url}: {e}")
                    continue

    print("Scraping complete. Total articles scraped:", len(news))
    return news