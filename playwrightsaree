import csv
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.kaitharinesavu.com"
SAREES_URL = BASE_URL + "/collections/sarees"
OUTPUT_CSV = "one_saree_product.csv"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(SAREES_URL)
    page.wait_for_load_state("networkidle")

    # Wait for product cards to load (not necessarily visible)
    page.wait_for_selector("a[href*='/products/']", timeout=10000, state="attached")

    # Scroll down slightly in case of lazy loading
    page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
    page.wait_for_timeout(1500)

    # Get first product URL
    first_product = page.locator("a[href*='/products/']").first
    href = first_product.get_attribute("href")
    product_url = href if href.startswith("http") else BASE_URL + href

    print(f"🔗 Found first product: {product_url}")

    # Open product page
    product_page = browser.new_page()
    product_page.goto(product_url)
    product_page.wait_for_load_state("networkidle")

    # --- Extract product details safely ---

    try:
        title = product_page.locator("h1").inner_text()
    except:
        title = ""

    try:
        meta_title = product_page.title()
    except:
        meta_title = ""

    try:
        meta_desc = product_page.locator("head > meta[name='description']").get_attribute("content")
    except:
        meta_desc = ""

    try:
        desc_locator = product_page.locator(".product-single__description")
        description = desc_locator.inner_text() if desc_locator.count() > 0 else ""
    except:
        description = ""

    try:
        img_locator = product_page.locator(".product-single__photo img").first
        img_url = img_locator.get_attribute("src")
        img_alt = img_locator.get_attribute("alt")
        if img_url and img_url.startswith("//"):
            img_url = "https:" + img_url
    except:
        img_url = ""
        img_alt = ""

    # --- Write to CSV ---
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Product URL", "Title", "Meta Title",
            "Meta Description", "Description",
            "Image URL", "Image ALT"
        ])
        writer.writerow([
            product_url, title, meta_title,
            meta_desc, description,
            img_url, img_alt
        ])

    print(f"\n✅ 1 Product saved to {OUTPUT_CSV}")
    browser.close()
