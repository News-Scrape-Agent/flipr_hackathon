import asyncio
from playwright.async_api import async_playwright

URL = "https://indianexpress.com/search/"

async def indian_express_topic_scraper(url: str = URL, topics: list = [], max_articles: int = 10) -> list:
    news = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Change to False for debugging
        page = await browser.new_page()

        for topic in topics:
            print(f"🔍 Searching for: {topic}")
            await page.goto(url, timeout=60000)

            # Fill the search input field
            await page.fill(".srch-npt", topic)

            # Click the search button
            await page.click(".srch-btn")

            # Wait for search results
            await page.wait_for_selector("#search-listing-results .search-result")

            # Extract valid news article links
            links = await page.eval_on_selector_all(
                "#search-listing-results .search-result h3 a",
                "elements => elements.map(el => el.href)"
            )

            links = links[:min(max_articles, len(links))]

            # Visit each news article to extract details
            for link in links:
                try:
                    await page.goto(link, timeout=60000)

                    # Extract title
                    title_elem = await page.query_selector("h1[itemprop='headline']")
                    title = await title_elem.text_content() if title_elem else "No Title"

                    # Extract date
                    date_elem = await page.query_selector("span[itemprop='dateModified']")
                    date_time = await date_elem.get_attribute("content") if date_elem else "No Date"

                    # Extract content
                    content_elem = await page.query_selector("div#pcl-full-content")
                    paragraphs = await content_elem.query_selector_all("p") if content_elem else []
                    full_content = "\n".join([await p.text_content() for p in paragraphs])

                    news.append({"title": title, "date_time": date_time, "content": full_content, "topic": topic})

                except Exception as e:
                    print(f"❌ Error processing {link}: {e}")
                    continue

        await browser.close()
    
    return news