import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

URL = "https://www.tribuneindia.com/topic"
async def tribune_topic_scraper(url: str = URL, topics: list = [], max_articles: int = 5) -> list:

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        links = []
        print("Searching for topic based news on Tribune India...")

        for topic in topics:
            print(f"Searching for: {topic}")
            topic = topic.lower().replace(" ", "-")
            try:
                await page.goto(f"{url}/{topic}/", timeout=20000)

                await page.wait_for_selector("div.post-item.search_post", timeout=10000)

                # Extract all links
                topic_links = await page.eval_on_selector_all(
                    "div.post-featured-img-wrapper a",          # Target elements
                    "elements => elements.map(el => el.href)"
                )
                topic_links = topic_links[:min(2 * max_articles, len(topic_links))]
                links.append((topic_links, topic))
                
            except Exception as e:
                print(f"Error: {e}")
                continue

        news = []
        for topic_links, topic in links:
            ctr = 0
            for url in topic_links:
                try:
                    await page.goto(url, timeout=20000, wait_until="domcontentloaded")
                    await page.route("**/*", lambda route: asyncio.create_task(
                        route.abort() if route.request.resource_type in ["image", "stylesheet", "font", "media"] else route.continue_()))

                    h1_text = await page.text_content('h1.post-header')
                    if not h1_text:
                        h1_text = 'No title found'

                    div_text = await page.locator("div.timesTamp").inner_text()
                    parts = div_text.split(":", 1)
                    if len(parts) > 1:
                        elem = parts[1].strip() 
                        dt = elem.replace("IST", "").strip()
                        date_time = datetime.strptime(dt, "%I:%M %p %b %d, %Y")
                    else:
                        date_time = "No date found"

                    p_elements = await page.query_selector_all('div#story-detail p')
                    p_texts_content = [await p.text_content() for p in p_elements]
                    if len(p_texts_content) == 0:
                        continue
                    article = ' '.join(p_texts_content)
                    
                    news.append({"title": h1_text, "date_time": date_time, "content": article})
                    ctr += 1
                    if ctr >= max_articles:
                        break
                    
                except Exception as e:
                    print(f"Error: {e}")
                    continue

        await browser.close()
        
        print("Scraping complete. Total articles scraped:", len(news))
        return news