import requests
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from playwright.async_api import async_playwright


URL = 'https://www.sportskeeda.com/'
async def sportskeeda_scraper(url: str = URL, max_articles: int = 10) -> list:
    try:
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to retrieve page, status code: {response.status_code}")
            return []
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

        links = links[:min(2 * max_articles, len(links))]
    except requests.exceptions.RequestException as e:
        print(f"Error getting the response from {url}: {e}")

    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
        except Exception as e:
            print(f"Error opening a new page: {e}")
            return []

        news = []
        print("Searching for latest news on Sportskeeda...")

        ctr = 0
        for url in links:
            try:
                await page.goto(url, timeout=20000, wait_until='domcontentloaded')
                await page.route("**/*", lambda route: asyncio.create_task(
                    route.abort() if route.request.resource_type in ["image", "stylesheet", "font", "media"] else route.continue_()))
            
                heading = await page.locator('h1#heading.title').text_content()
                heading = heading.strip() if heading else "No title found"

                time_tag = await page.locator('div.article-box div.date-pub.timezone-date').text_content()
                date_time = time_tag.strip() if time_tag else None
                if date_time:
                    if ('GMT' in date_time):
                        date_time = date_time.replace("Modified", "").replace("GMT", "").replace(",", "").strip()
                        dt = datetime.strptime(date_time, "%b %d %Y %H:%M")
                        date_time = dt + timedelta(hours=5, minutes=30)        # Convert to IST manually (GMT + 5:30)
                    else:
                        date_time = date_time.replace("Modified", "").replace("IST", "").replace(",", "").strip()
                        date_time = datetime.strptime(date_time, "%b %d %Y %H:%M")

                # Extract article content
                article_content = []
                paragraphs = await page.locator('p[data-imp-id^="article_paragraph"]').all()
                if (len(paragraphs) == 0):
                    continue

                for p in paragraphs:
                    p_text = await p.text_content()
                    if p_text:
                        article_content.append(p_text.strip())

                article_content = "\n".join(article_content)

                news.append({"title": heading, "date_time": date_time, "content": article_content})
                ctr += 1
                if ctr >= max_articles:
                    break

            except Exception as e:
                print(f"Error navigating to {url}: {e}")
                continue    

        await browser.close()

    print("Scraping complete. Total articles scraped:", len(news))
    return news