import os
import asyncio
import re
from playwright.async_api import async_playwright, Page

# Configuration
BASE_URL = "https://www.lawcommission.gov.np"
START_URL = "https://www.lawcommission.gov.np/category/1757/"  # Nepal Acts Collection (नेपाल ऐन संग्रह) - 300 Acts
DOWNLOAD_DIR = r"c:\Users\hp\Desktop\task\vidhi_ai\data\raw"
MAX_PAGES = 70  # Enough to get all 300+ Acts (approximately 60 pages)

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

        pages_scraped = 0
        current_page_num = 1
        total_downloaded = 0

        while pages_scraped < MAX_PAGES:
            catalog_url = f"{START_URL}?page={current_page_num}"
            print(f"\n{'='*70}")
            print(f"Scraping Catalog Page {current_page_num}: {catalog_url}")
            print(f"{'='*70}")
            
            await page.goto(catalog_url, wait_until='networkidle')
            await asyncio.sleep(2)  # Wait for page to fully load
            
            # Extract links to the individual Act pages
            links = await page.evaluate('''() => {
                const anchors = Array.from(document.querySelectorAll('.category-1-grid .card__title a'));
                return anchors.map(a => ({title: a.innerText.trim(), url: a.href}));
            }''')

            if not links:
                print("No acts found on this page. Ending pagination.")
                break

            print(f"Found {len(links)} acts on this page.")

            # Process each link
            for idx, link in enumerate(links, 1):
                print(f"\n[{idx}/{len(links)}] Processing: {link['title'][:50]}...")
                
                # Open Act page in new tab
                act_page = await context.new_page()
                try:
                    await download_pdf(act_page, link['url'], link['title'])
                    total_downloaded += 1
                except Exception as e:
                    print(f"  ✗ Error downloading: {e}")
                finally:
                    await act_page.close()
                    await asyncio.sleep(1)  # Be respectful - 1 second delay
            
            # Check if there's a next page
            next_exists = await page.evaluate('''() => {
                const nextBtn = document.querySelector('.pagination .next__pagination');
                return nextBtn !== null;
            }''')
            
            pages_scraped += 1
            
            if not next_exists:
                print(f"\n{'='*70}")
                print("No more pages found. Scraping complete!")
                print(f"{'='*70}")
                break
            
            # Move to next page
            current_page_num += 1
            print(f"\nMoving to page {current_page_num}...")

        await browser.close()
        
        print(f"\n{'='*70}")
        print(f"SCRAPING SUMMARY")
        print(f"{'='*70}")
        print(f"Pages scraped: {pages_scraped}")
        print(f"Total Acts downloaded: {total_downloaded}")
        print(f"{'='*70}")

if __name__ == "__main__":
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    asyncio.run(scrape_catalog())

