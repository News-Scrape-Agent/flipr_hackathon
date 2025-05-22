import asyncio
import difflib
from datetime import datetime
from playwright.async_api import async_playwright

# List of predefined states and cities
STATES = ["Punjab", "Haryana", "Himachal Pradesh", "J K", "Uttarakhand", "Uttar Pradesh", "Rajasthan", "Madhya Pradesh", "Chhattisgarh"]
CITIES = ["Amritsar", "Bathinda", "Chandigarh", "Delhi", "Jalandhar", "Ludhiana", "Patiala", "Shaharnama"]

BASE_URL = "https://www.tribuneindia.com/news/"

def get_best_matching_location(user_location: str, choices: list) -> str:
    """Finds the best match for a user-provided location."""
    match = difflib.get_close_matches(user_location[0].lower(), [c.lower() for c in choices], n=1, cutoff=0.6)
    return choices[[c.lower() for c in choices].index(match[0])] if match else None

async def tribune_city_scraper(url: str = BASE_URL, max_articles: int = 5, location: list = ["delhi"]) -> list:
    """Scrapes news articles for the best-matching state or city using Playwright."""
    extracted_links = []
    news = []
    # Get the best match for the provided location
    matched_state = get_best_matching_location(location, STATES)
    matched_city = get_best_matching_location(location, CITIES)

    # Determine whether to scrape state or city
    scrape_type = "state" if matched_state else "city"
    matched_location = matched_state if matched_state else matched_city

    if not matched_location:
        print(f"No matching state or city found for '{location}'. Skipping scraping.")
        return []

    scrape_url = f"{BASE_URL}{scrape_type}/{matched_location.lower().replace(' ', '-')}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print("Searching for location based news on Tribune India...")
            await page.goto(scrape_url, timeout=20000)
            await page.wait_for_selector("article.card-df h2 a", timeout=10000)

            links = await page.eval_on_selector_all(
                "article.card-df h2 a", 
                "elements => elements.map(el => el.href)"
            )
            extracted_links = list(set(links[:min(2 * max_articles, len(links))]))

        except Exception as e:
            print(f"Error scraping {matched_location}: {e}")

        ctr = 0
        for url in extracted_links:
            try:
                await page.goto(url, timeout=20000, wait_until="domcontentloaded")
                await page.route("**/*", lambda route: asyncio.create_task(
                    route.abort() if route.request.resource_type in ["image", "stylesheet", "font", "media"] else route.continue_()))

                h1_text = await page.text_content('h1.post-header')
                if not h1_text:
                    h1_text = 'No title found'

                elems = await page.query_selector_all("span.updated_time")
                if len(elems) >= 2:
                    elem = await elems[1].inner_text()
                    dt = elem.replace("Updated At :", "").replace("IST", "").strip()
                    date_time = datetime.strptime(dt, "%I:%M %p %b %d, %Y")
                else:
                    date_time = "No date found"

                p_elements = await page.query_selector_all('div#story-detail p')
                p_texts_content = [await p.text_content() for p in p_elements]
                if len(p_texts_content) == 0:
                    continue
                article = ' '.join(p_texts_content)
                
                news.append({"title": h1_text, "date_time": date_time, "content": article, "location": location[0].lower()})
                ctr += 1
                if ctr >= max_articles:
                    break

            except Exception as e:
                print(f"Error scraping article: {e}")
                continue

        await browser.close()
        
    print("Scraping complete. Total articles scraped:", len(news))
    return news