from playwright.sync_api import sync_playwright
def ndtv_scrapper(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url,timeout=60000)
        load_more_button = page.locator("#loadmorenews_btn .btn_bm")
        load_more_button.click()
        page.wait_for_timeout(5000)
        links = page.locator('.NwsLstPg_ttl-lnk').evaluate_all("elements => elements.map(e => e.href)")
        news = []

        for link in links:
            try:
                page.goto(link,timeout=60000)
                heading = page.inner_text("h1.sp-ttl")  
                time = page.inner_text("span.pst-by_lnk")  
                label = link.split("/")[3]  
                content = page.locator("div.Art-exp_cn p").evaluate_all("elements => elements.map(el => el.innerText).join(' ')")

                news.append({"title": heading, "date_time": time, "label": label, "content": content})
            except:
                continue
        browser.close()
        return news
url = "https://www.ndtv.com/india"
news = ndtv_scrapper(url)
print("Scraping complete. Total articles:", len(news))
print(news)