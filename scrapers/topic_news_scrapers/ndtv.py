import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

URL = "https://www.ndtv.com/search?searchtext="
async def ndtv_topic_scraper(url: str = URL, topics: list = [], max_articles: int = 5) -> list:

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("Searching for topic based news on NDTV...")
        
        links = []
        for topic in topics:
            print(f"Searching for: {topic}")
            formatted_topic = topic.lower().replace(" ", "-")
            search_url = f"{url}{formatted_topic}"

            try:
                await page.goto(search_url, timeout=20000)  # Timeout handling
                await page.wait_for_selector(".SrchLstPg_ttl", timeout=10000)

                # Extract links
                topic_links = await page.eval_on_selector_all(
                    "a.SrchLstPg_ttl", "elements => elements.map(el => el.href)"
                )
                topic_links = topic_links[:min(2 * max_articles, len(topic_links))]
                links.append((topic_links, topic))

            except PlaywrightTimeoutError:
                print(f"Timeout Error! Skipping: {search_url}")
                continue

        news = []
        for topic_links, topic in links:
            ctr = 0
            for url in topic_links:
                page = await browser.new_page()
                try:
                    await page.goto(url, timeout=20000, wait_until="domcontentloaded")
                    await page.route("**/*", lambda route: asyncio.create_task(
                        route.abort() if route.request.resource_type in ["image", "stylesheet", "font", "media"] else route.continue_()))

                    # Extract article details
                    heading = await page.text_content("h1.sp-ttl") or "No title found"

                    date_elem = await page.query_selector("span[itemprop='dateModified']")
                    date_time = await date_elem.get_attribute("content") if date_elem else None

                    if date_time:
                        date_time = datetime.strptime(date_time, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
                    else:
                        date_time = 'No date found'

                    content = " ".join(await page.locator("div.Art-exp_cn p").all_inner_texts())
                    if not content:
                        continue

                    news.append({"title": heading, "date_time": date_time, "content": content})
                    ctr += 1
                    if ctr >= max_articles:
                        break
                
                except PlaywrightTimeoutError:
                    print(f"Timeout Error! Skipping: {url}")
                    continue

                await page.close()

        # Close the browser
        await browser.close()

        print("Scraping Complete. Total articles scraped:", len(news))
        return news
