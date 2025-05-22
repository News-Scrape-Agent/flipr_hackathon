import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

URL = "https://indianexpress.com/search/"

async def indian_express_topic_scraper(url: str = URL, topics: list = [], max_articles: int = 5) -> list:
    news = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("Searching for topic based news on Indian Express...")
        for topic in topics:
            print(f"Searching for: {topic}")
            await page.goto(url, timeout=60000)

            await page.fill(".srch-npt", topic)

            await page.click(".srch-btn")

            await page.wait_for_selector("#search-listing-results .search-result")

            # Extract valid news article links
            links = await page.eval_on_selector_all(
                "#search-listing-results .search-result h3 a",
                "elements => elements.map(el => el.href)"
            )

            links = links[:min(2 * max_articles, len(links))]

            # Visit each news article to extract details
            ctr = 0
            for link in links:
                try:
                    await page.goto(link, timeout=30000, wait_until="domcontentloaded")
                    await page.route("**/*", lambda route: asyncio.create_task(
                        route.abort() if route.request.resource_type in ["image", "stylesheet", "font", "media"] else route.continue_()))

                    # Extract title
                    title_elem1 = await page.query_selector("h1[itemprop='headline']")
                    title_elem2 = await page.query_selector("h1[class='article-main-head']")
                    if title_elem1:
                        title = await title_elem1.text_content()
                    elif title_elem2:
                        title = await title_elem2.text_content()
                    else:
                        title = "No title found"

                    # Extract date
                    date_elem = await page.query_selector("span[itemprop='dateModified']")
                    date_time = await date_elem.get_attribute("content") if date_elem else "No date found"
                    if date_time != "No date found":
                        date_time = datetime.fromisoformat(date_time)

                    # Extract content
                    content_elem = await page.query_selector("div#pcl-full-content")
                    paragraphs = await content_elem.query_selector_all("p") if content_elem else None
                    if not paragraphs:
                        continue

                    full_content = "\n".join([await p.text_content() for p in paragraphs])

                    news.append({"title": title.strip(), "date_time": date_time, "content": full_content})
                    ctr += 1
                    if ctr >= max_articles:
                        break

                except Exception as e:
                    print(f"Error processing {link}: {e}")
                    continue

        await browser.close()
    
    print("Scraping complete. Total articles scraped:", len(news))
    return news