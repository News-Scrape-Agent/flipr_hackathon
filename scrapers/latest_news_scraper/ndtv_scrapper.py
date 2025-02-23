import asyncio
from playwright.async_api import async_playwright

url = "https://www.ndtv.com/india"

async def ndtv_scrapper(url: str, max_articles: int = 10):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=60000)
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
        links = links[:min(max_articles, len(links))]
        
        for link in links:
            try:
                await page.goto(link, timeout=60000)
                heading = await page.inner_text("h1.sp-ttl")  
                time = await page.inner_text("span.pst-by_lnk")  
                label = link.split("/")[3]  
                content = await page.locator("div.Art-exp_cn p").evaluate_all(
                    "elements => elements.map(el => el.innerText).join(' ')"
                )

                news.append({"title": heading, "date_time": time, "label": label, "content": content })
            except Exception as e:
                print(f"Error scraping {link}: {e}")
                continue
        await browser.close()
        return news