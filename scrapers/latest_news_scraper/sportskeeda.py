import requests
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

def sportskeeda_link_scraper(url: str, num_links: int = 10):
    response = requests.get(url)

    # Parse the HTML content of the webpage
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all divs whose class starts with "category-region"
    target_classes = ["feed-featured-content-primary", "feed-featured-content-secondary"]
    featured_divs = soup.find_all("div", class_=lambda x: x in target_classes if x else False)

    # Extract only <a> href links inside these divs
    links = []
    for div in featured_divs:
        for a_tag in div.find_all("a", href=True):
            full_link = requests.compat.urljoin(url, a_tag["href"])  # Convert relative to absolute URL
            links.append(full_link)

    links = links[:min(num_links, len(links))]
    return links


async def sportskeeda_scraper():

    url = 'https://www.sportskeeda.com/'
    links = sportskeeda_link_scraper(url)

    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=True)  # Run in headless mode for faster execution
        page = await browser.new_page()

        news = []
        for url in links:
            # Go to the webpage
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")  # Ensures the page content is fully loaded

            heading = await page.locator('h1#heading.title').text_content()
            heading = heading.strip() if heading else "No heading found"

            time_tag = await page.locator('div.article-box div.date-pub.timezone-date').text_content()
            time_text = time_tag.strip() if time_tag else "No time found"
            
            # Extract article content
            article_content = []
            paragraphs = await page.locator('p[data-imp-id^="article_paragraph"]').all()

            for p in paragraphs:
                p_text = await p.text_content()
                if p_text:
                    article_content.append(p_text.strip())

            article_content = "\n".join(article_content)

            news.append({"title": heading, "date_time": time_text, "content": article_content})

        # Close the browser
        await browser.close()

    return news

# Run the Playwright script
asyncio.run(sportskeeda_scraper())