import asyncio
from playwright.async_api import async_playwright

states = ["Punjab", "Haryana", "Himachal Pradesh", "J K", "Uttarakhand", "Uttar Pradesh", "Rajasthan", "Madhya Pradesh", "Chhattisgarh"]
cities = ["Amritsar", "Bathinda", "Chandigarh", "Delhi", "Jalandhar", "Ludhiana", "Patiala", "Shaharnama"]

base_url = "https://www.tribuneindia.com/news/"

async def tribune_city_scraper(url: str = base_url, max_articles: int = 20):
    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        extracted_links = []
        for state in states:
            url = "https://www.tribuneindia.com/news/state/" + state.lower().replace(" ", "-")
            await page.goto(url, timeout=20000) 

            await page.wait_for_selector("article.card-df h2 a", timeout=10000)

            links = await page.eval_on_selector_all(
                "article.card-df h2 a",
                "elements => elements.map(el => el.href)"
            )
            links = links[:min(1, len(links))]
        
            extracted_links.append((links, state))
        
        for city in cities:
            url = "https://www.tribuneindia.com/news/city/" + city.lower()
            await page.goto(url, timeout=60000)

            await page.wait_for_selector("article.card-df h2 a", timeout=10000)

            links = await page.eval_on_selector_all(
                "article.card-df h2 a", 
                "elements => elements.map(el => el.href)"
            )
            links = links[:min(1, len(links))]
        
            extracted_links.append((links, city))

        news = []
        for links, location in extracted_links:
            for url in links:
                await page.goto(url, timeout=20000)

                h1_text = await page.text_content('h1.post-header')

                p_elements = await page.query_selector_all('div#story-detail p')
                p_texts_content = [await p.text_content() for p in p_elements]
                article = ' '.join(p_texts_content)

                published_time = await page.text_content('div.timesTamp span.updated_time')
                
                news.append({"title": h1_text, "date_time": published_time, "content": article, "location": location})

        await browser.close()
        return news

# asyncio.run(tribune_city_scraper())