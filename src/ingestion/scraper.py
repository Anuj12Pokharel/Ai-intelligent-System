import os
import asyncio
import re
from playwright.async_api import async_playwright, Page

# Configuration
BASE_URL = "https://www.lawcommission.gov.np"
START_URL = "https://www.lawcommission.gov.np/category/1806/" # Existing Laws
DOWNLOAD_DIR = r"c:\Users\hp\Desktop\task\vidhi_ai\data\raw"
MAX_PAGES = 5  # Safety limit for pagination

async def download_pdf(page: Page, url: str, title: str):
    """
    Navigates to the law page and attempts to find/download the PDF.
    Handles multiple PDF source patterns including flipbook widgets.
    """
    print(f"Processing: {title} -> {url}")
    try:
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state('networkidle', timeout=10000)
        
        # Try multiple PDF source patterns
        pdf_link = await page.evaluate('''() => {
            // Pattern 1: Standard <a> links ending in .pdf
            const links = Array.from(document.querySelectorAll('a'));
            const pdf = links.find(a => a.href && a.href.toLowerCase().endsWith('.pdf'));
            if (pdf) return pdf.href;
            
            // Pattern 2: Flipbook widget source attribute
            const flipbook = document.querySelector('[source], [pdf-source], [data-source], [data-pdf]');
            if (flipbook) {
                const src = flipbook.getAttribute('source') || 
                            flipbook.getAttribute('pdf-source') ||
                            flipbook.getAttribute('data-source') ||
                            flipbook.getAttribute('data-pdf');
                if (src && src.endsWith('.pdf')) return src;
            }
            
            // Pattern 3: Script tags containing PDF URLs
            const scripts = document.querySelectorAll('script');
            for (const script of scripts) {
                const text = script.textContent || '';
                const match = text.match(/(https?:\\/\\/[^"'\\s]+\\.pdf)/i);
                if (match) return match[1];
            }
            
            // Pattern 4: Iframe with PDF
            const iframe = document.querySelector('iframe[src*=".pdf"]');
            if (iframe) return iframe.src;
            
            return null;
        }''')

        if pdf_link:
            print(f"Found PDF: {pdf_link}")
            response = await page.request.get(pdf_link)
            if response.status == 200:
                safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()[:100]
                filename = f"{safe_title}.pdf"
                filepath = os.path.join(DOWNLOAD_DIR, filename)
                
                with open(filepath, "wb") as f:
                    f.write(await response.body())
                print(f"Downloaded: {filename}")
                return
            else:
                print(f"Failed to download PDF: Status {response.status}")
        
        # Fallback: Save HTML content for metadata/partial parsing
        print("No PDF found. Saving HTML for metadata extraction.")
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()[:100]
        filepath = os.path.join(DOWNLOAD_DIR, f"{safe_title}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(await page.content())
        print(f"Saved HTML fallback: {filepath}")

    except Exception as e:
        print(f"Error processing {url}: {e}")

async def scrape_catalog():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Headless=False to see what happens
        context = await browser.new_context()
        page = await context.new_page()

        current_url = START_URL
        pages_scraped = 0

        while current_url and pages_scraped < MAX_PAGES:
            print(f"--- Scraping Catalog Page: {current_url} ---")
            await page.goto(current_url)
            
            # Extract links to the individual Act pages
            # Based on actual DOM: <div class="category-1-grid"> contains <div class="grid__card">
            # Each card has <h3 class="card__title"><a href="...">Title</a></h3>
            links = await page.evaluate('''() => {
                const anchors = Array.from(document.querySelectorAll('.category-1-grid .card__title a'));
                return anchors.map(a => ({title: a.innerText.trim(), url: a.href}));
            }''')

            print(f"Found {len(links)} acts on this page.")

            # Process each link (Sequential for now to be polite)
            for link in links:
                await download_pdf(page, link['url'], link['title'])
                await asyncio.sleep(1)  # Be respectful - 1 second delay
            
            # Pagination: Look for "Next" button
            # Based on DOM: <a href="?page=2" class="pagination__btn next__pagination">
            next_url = await page.evaluate('''() => {
                const nextBtn = document.querySelector('.pagination .next__pagination');
                return nextBtn ? nextBtn.href : null;
            }''')
            
            current_url = next_url
            pages_scraped += 1
            if not next_url:
                print("No more pages.")
                break

        await browser.close()

if __name__ == "__main__":
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    asyncio.run(scrape_catalog())
