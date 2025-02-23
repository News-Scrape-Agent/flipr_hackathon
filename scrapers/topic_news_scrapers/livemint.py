from playwright.async_api import async_playwright
import asyncio
import requests
from bs4 import BeautifulSoup

async def scrape_page_content():
    links = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        topic = "jee mains"
        print(f"🔍 Searching for: {topic}")
        await page.goto("https://www.livemint.com/search", timeout=60000)

        # Fill the search input field
        await page.fill("#searchField", topic)

        # Press Enter to search
        await page.press("#searchField", "Enter")

        # Wait for results to load
        await page.wait_for_selector(".listingNew")

        # Extract news article links
        links = await page.eval_on_selector_all(
            ".headline a",
            "elements => elements.map(el => el.href)"
        )
        await asyncio.sleep(5)
        print(f"✅ Found {len(links)} links for '{topic}'")
        await browser.close()

    news = []
    for url in links:
        response = requests.get(url)

        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the <h2> tag content
        h1_tag = soup.find('h1', id="article-0")
        h1_text = h1_tag.get_text() if h1_tag else 'No <h1> tag found'

        # Extract all text content from story_para_ classes
        story_paras = soup.find_all('div', class_="storyParagraph", id=lambda x: x and x.startswith('article-index'))
        story_texts = [para.get_text() for para in story_paras]
        article_text = ' '.join(story_texts)

        # Extract the "First Published" date and time
        first_published = soup.find('div', class_=lambda x: x and x.startswith('storyPage_date'))
        first_published_text = first_published.get_text(strip=True) if first_published else 'No First Published date found'

        # Print the extracted content
        print('H2 Tag Content:', h1_text)
        print('Story Paragraphs:', article_text)
        print('First Published Date and Time:', first_published_text)

        news.append({'title': h1_text, 'content': article_text, 'first_published': first_published_text})

    return news

asyncio.run(scrape_page_content())