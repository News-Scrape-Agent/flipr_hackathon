# TODO: All the links are opening simultaneously. We need to open them one by one and extract the content.
import asyncio
from playwright.async_api import async_playwright

class NDTVScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.base_url = "https://www.ndtv.com/search?searchtext="

    def format_topic(self, topic):
        return topic.replace(" ", "-")

    async def scrape_links(self, topic, browser):
        """Fetch all article links for a given topic."""
        formatted_topic = self.format_topic(topic)
        search_url = f"{self.base_url}{formatted_topic}"

        page = await browser.new_page()
        await page.goto(search_url, timeout=60000)
        await page.wait_for_selector(".SrchLstPg_ttl", timeout=10000)

        links = await page.eval_on_selector_all("a.SrchLstPg_ttl", "elements => elements.map(el => el.href)")
        await page.close()
        return links

    async def scrape_article(self, link, browser):
        """Extracts title, date, category, and content from an article page."""
        try:
            page = await browser.new_page()
            await page.goto(link, timeout=30000)  
            await page.wait_for_selector("h1.sp-ttl", timeout=5000)  

            heading = await page.text_content("h1.sp-ttl") or "N/A"
            time = await page.text_content("span.pst-by_lnk") or "N/A"
            label = link.split("/")[3]  
            content = " ".join(await page.locator("div.Art-exp_cn p").all_inner_texts())

            await page.close()
            return {"title": heading, "date_time": time, "label": label, "content": content}
        except Exception as e:
            print(f"⚠️ Error scraping {link}: {e}")
            return None  

    async def scrape_news(self, topics):
        """Scrapes news articles for a list of topics."""
        results = {}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)

            for topic in topics:
                print(f"🔍 Searching for: {topic}")
                links = await self.scrape_links(topic, browser)
                news = []

                # Process each link asynchronously
                tasks = [self.scrape_article(link, browser) for link in links[:3]]
                articles = await asyncio.gather(*tasks)

                news.extend([article for article in articles if article])
                results[topic] = news

            await browser.close()

        return results

# Example Usage
async def main():
    topics = ["Alia Bhatt"]
    scraper = NDTVScraper(headless=False)
    news_data = await scraper.scrape_news(topics)

    # Print results
    for topic, articles in news_data.items():
        print(f"\n🔹 {topic} ({len(articles)} articles)")
        for article in articles:
            print(f"📰 {article['title']} ({article['date_time']}) - {article['label']}")

# Run the async function
asyncio.run(main())
