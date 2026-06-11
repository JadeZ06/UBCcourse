from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os
import json

os.makedirs("responses", exist_ok=True)

# 0 = first page, then 50, 100, 150, 200...
MAX_OFFSET = 2000
PAGE_SIZE = 50


def save_response(response, filename):
    text = response.text()

    filepath = os.path.join("responses", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Saved: {filepath}")

    return text


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://wd10.myworkday.com/ubc/d/home.htmld")

    input(
        "\nLogin and go to Find Course Sections.\n"
        "DO NOT search yet.\n"
        "Press ENTER when ready.\n"
    )

    print("\nWaiting for first search response...")

    with page.expect_response(
        lambda r: "search.htmld" in r.url,
        timeout=120000
    ) as search_response_info:
        input(
            "\nNow perform your search in Workday.\n"
            "After the results appear, press ENTER here.\n"
        )

    search_response = search_response_info.value

    print("Got first page:")
    print(search_response.url)

    search_text = save_response(search_response, "page_0.json")

    search_data = json.loads(search_text)

    # First page usually has facetContainer directly.
    # Pagination pages may wrap it in body, so this handles both.
    search_body = search_data.get("body", search_data)

    total_count = search_body["facetContainer"]["paginationCount"]["value"]

    last_offset = ((total_count - 1) // PAGE_SIZE) * PAGE_SIZE

    last_offset = min(last_offset, MAX_OFFSET)

    print(f"\nTotal results: {total_count}")
    print(f"Last offset to capture: {last_offset}")

    # Now capture pagination pages by scrolling
    for offset in range(PAGE_SIZE, last_offset + PAGE_SIZE, PAGE_SIZE):
        print(f"\nWaiting for pagination/{offset}.htmld...")

        try:
            with page.expect_response(
                lambda r, offset=offset: f"pagination/{offset}.htmld" in r.url,
                timeout=60000
            ) as pagination_response_info:

                # Trigger Workday infinite scroll
                page.mouse.wheel(0, 6000)

            pagination_response = pagination_response_info.value

            print("Got pagination page:")
            print(pagination_response.url)

            save_response(
                pagination_response,
                f"page_{offset}.json"
            )

        except PlaywrightTimeoutError:
            print(f"No response for offset {offset}. Stopping.")
            break

    input("\nDone. Press ENTER to close browser.\n")
    browser.close()