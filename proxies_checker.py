import asyncio
import csv
import configparser
from playwright.async_api import async_playwright

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.google.com/'
}
GOTO_TIMEOUT = 60
WAIT_TIMEOUT = 10

async def run(playwright: async_playwright, proxy: dict, url: str, selectors: list) -> dict:
    row = {'server': proxy['server'], 'username': proxy['username'], 'password': proxy['password']}
    try:
        browser = await playwright.chromium.launch(proxy=proxy, headless=True)
        context = await browser.new_context(user_agent=USER_AGENT, extra_http_headers=HEADERS)
        page = await context.new_page()
        await page.goto(url, timeout = GOTO_TIMEOUT*1000)
        row['Connection'] = 'STATUS_OK'
        for i, selector in enumerate(selectors):
            try:
                locator = page.locator(selector)
                # Wait for at least 5 seconds
                await asyncio.sleep(10)
                # Get the content of the element
                content = await locator.inner_text()
                row[f'selector_{i+1}'] = content
            except Exception as e:
                row[f'selector_{i+1}'] = 'FAILURE'
        await browser.close()
    except Exception as e:
        print(f'Error: {e}')
        row['Connection'] = 'STATUS_ERR'
    return row

async def main():
    # Read the configuration from the config.ini file
    config = configparser.ConfigParser()
    config.read('config.ini')
    url = config['DEFAULT']['url'].strip()
    selectors = [ i.strip() for i in config['DEFAULT']['selectors'].split(',') ]
    GOTO_TIMEOUT, WAIT_TIMEOUT = [ int(i.strip()) for i in config['DEFAULT']['timeout'].split(',') ]
    max_concurrent_tasks = int(config['DEFAULT']['max_concurrent_tasks'].strip())

    async with async_playwright() as playwright:
        # Read the proxy information from the CSV file
        with open('proxies.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            proxies = [row for row in reader]

        tasks = []
        for proxy in proxies:
            tasks.append(asyncio.ensure_future(run(playwright, proxy, url, selectors)))
            if len(tasks) >= max_concurrent_tasks:
                rows = await asyncio.gather(*tasks)
                tasks.clear()
                # Write the rows to the output.csv file
                with open('output.csv', 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=['server', 'username', 'password', 'Connection'] + [f'selector_{i+1}' for i in range(len(selectors))])
                    writer.writerows(rows)
        if tasks:
            rows = await asyncio.gather(*tasks)
            # Write the rows to the output.csv file
            with open('output.csv', 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['server', 'username', 'password', 'Connection'] + [f'selector_{i+1}' for i in range(len(selectors))])
                writer.writerows(rows)

if __name__ == '__main__':
    asyncio.run(main())
