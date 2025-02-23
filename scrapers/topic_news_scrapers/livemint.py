import asyncio
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

url = "https://www.livemint.com/search"
async def livemint_topic_scraper(url: str, topics: list, max_articles: int = 10) -> list:
    links = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        for topic in topics:
            print(f"🔍 Searching for: {topic}")

            await page.fill("#searchField", topic)

            await page.press("#searchField", "Enter")

            await page.wait_for_selector(".listingNew")

            topic_links = await page.eval_on_selector_all(
                ".headline a",
                "elements => elements.map(el => el.href)"
            )
            await asyncio.sleep(5)
            print(f"✅ Found {len(links)} links for '{topic}'")

            links.append((topic_links[:min(max_articles, len(links))], topic))

        await browser.close()

    news = []
    for links, topic in links:
        for url in links:
            response = requests.get(url)

            soup = BeautifulSoup(response.content, 'html.parser')

            h1_tag = soup.find('h1', id="article-0")
            h1_text = h1_tag.get_text() if h1_tag else 'No <h1> tag found'

            story_paras = soup.find_all('div', class_="storyParagraph", id=lambda x: x and x.startswith('article-index'))
            story_texts = [para.get_text() for para in story_paras]
            article_text = ' '.join(story_texts)

            first_published = soup.find('div', class_=lambda x: x and x.startswith('storyPage_date'))
            first_published_text = first_published.get_text(strip=True) if first_published else 'No First Published date found'

            news.append({'title': h1_text, 'date_time': first_published_text, 'content': article_text, 'topic': topic})

    return news