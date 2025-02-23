import asyncio
from playwright.async_api import async_playwright

states = ["Punjab", "Haryana", "Himachal Pradesh", "J K", "Uttarakhand", "Uttar Pradesh", "Rajasthan", "Madhya Pradesh", "Chhattisgarh"]
cities = ["Amritsar", "Bathinda", "Chandigarh", "Delhi", "Jalandhar", "Ludhiana", "Patiala", "Shaharnama"]

base_url = "https://www.tribuneindia.com/news/"

# TODO: Add Date time to the news
async def tribune_city_scraper(url: str = base_url, max_articles: int = 20):
    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        extracted_links = []
        state_urls = []
        for state in states:
            url = "https://www.tribuneindia.com/news/state/" + state.lower().replace(" ", "-")
            await page.goto(url, timeout=60000) 

            await page.wait_for_selector("article.card-df h2 a", timeout=10000)

            links = await page.eval_on_selector_all(
                "article.card-df h2 a",
                "elements => elements.map(el => el.href)"
            )
            links = links[:min(5, len(links))]
            state_urls.append((links, state))
        
        extracted_links.append(state_urls)
        
        city_urls = []
        for city in cities:
            url = "https://www.tribuneindia.com/news/city/" + city.lower()
            await page.goto(url, timeout=60000)

            await page.wait_for_selector("article.card-df h2 a", timeout=10000)

            links = await page.eval_on_selector_all(
                "article.card-df h2 a", 
                "elements => elements.map(el => el.href)"
            )
            links = links[:min(5, len(links))]
            city_urls.append((links, city))
        
        extracted_links.append(city_urls)

        news = []
        for links, location in extracted_links:
            for url in links:
                await page.goto(url, timeout=60000)

                h1_text = await page.text_content('h1.post-header')

                p_elements = await page.query_selector_all('div.story-detail p')
                p_texts_content = [await p.text_content() for p in p_elements]
                article = ' '.join(p_texts_content)
                
                news.append({"title": h1_text, "content": article, "location": location})

        await browser.close()
        return news

# asyncio.run(tribune_city_scraper())