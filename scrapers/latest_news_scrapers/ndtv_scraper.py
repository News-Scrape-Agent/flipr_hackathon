import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

URL = "https://www.ndtv.com/india"

async def ndtv_scraper(url: str = URL, max_articles: int = 5) -> list:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Searching for latest news on NDTV...")

        try:
            await page.goto(url, timeout=20000)
        except Exception as e:
            print(f"Error navigating to {url}: {e}")
            await browser.close()
            return []
        # Click "Load More" button
        load_more_button = page.locator("#loadmorenews_btn .btn_bm")
        try:
            await load_more_button.click()
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"Error clicking 'Load More' button: {e}")
            return []

        try:
            links = await page.locator('.NwsLstPg_ttl-lnk').evaluate_all(
                "elements => elements.map(e => e.href)"
            )
        except Exception as e:
            print(f"Error extracting links: {e}")
            return []
        
        news = []
        links = links[:min(2 * max_articles, len(links))]
        
        ctr = 0
        for link in links:
            try:
                await page.goto(link, timeout=20000, wait_until="domcontentloaded")
                await page.route("**/*", lambda route: asyncio.create_task(
                    route.abort() if route.request.resource_type in ["image", "stylesheet", "font", "media"] else route.continue_()))
                
                heading = await page.inner_text("h1.sp-ttl", timeout=10000)  

                date_elem = await page.query_selector("span[itemprop='dateModified']")
                date_time = await date_elem.get_attribute("content") if date_elem else None

                if date_time:
                    date_time = datetime.strptime(date_time, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
                else:
                    date_time = 'No date found'
                
                content = await page.locator("div.Art-exp_cn p").evaluate_all(
                    "elements => elements.map(el => el.innerText).join(' ')"
                )
                if not content:
                    continue

                news.append({"title": heading, "date_time": date_time, "content": content})
                ctr += 1
                if ctr >= max_articles:
                    break
                
            except Exception as e:
                print(f"Error scraping {link}: {e}")
                continue
        await browser.close()
        
        print("Scraping complete. Total articles scraped:", len(news))
        return news