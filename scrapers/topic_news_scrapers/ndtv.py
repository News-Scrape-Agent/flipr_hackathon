import asyncio
from playwright.async_api import async_playwright

url = "https://www.ndtv.com/search?searchtext="
async def ndtv_topic_scraper(url: str, topics: list, max_articles: int = 10):

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        links = []
        for topic in topics:
            formatted_topic = topic.lower().replace(" ", "-")
            search_url = f"{url}{formatted_topic}"

            await page.goto(search_url, timeout=60000)  # 60 sec timeout
            await page.wait_for_selector(".SrchLstPg_ttl", timeout=10000)

            # Extract all links
            topic_links = await page.eval_on_selector_all(
                "a.SrchLstPg_ttl",  # Target elements
                "elements => elements.map(el => el.href)"
            )
            topic_links = topic_links[:min(max_articles, len(topic_links))]
            links.append((topic_links, topic))

        news = []
        for topic_links, topic in links:
            for url in topic_links:
                page = await browser.new_page()
                await page.goto(url, timeout=60000)

                # Extract article details
                heading = await page.text_content("h1.sp-ttl") or "N/A"
                time = await page.text_content("span.pst-by_lnk") or "N/A"
                content = " ".join(await page.locator("div.Art-exp_cn p").all_inner_texts())

                news.append({"title": heading, "date_time": time, "content": content, "topic": topic})

                await page.close()

        # Close the browser
        await browser.close()

        return news

# Example usage
async def main():
    topics = ["Alia Bhatt", "Tech News"]
    news_data = await ndtv_topic_scraper(url, topics)

    # Print results
    for article in news_data:
        print(f"📰 {article['title']} ({article['date_time']}) - {article['label']}")
        print(f"Content: {article['content'][:300]}...")  # Show first 300 chars of content

# Run the async function
asyncio.run(main())
