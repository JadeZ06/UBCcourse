from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(
        "https://wd10.myworkday.com/ubc/d/home.htmld"
    )

    input(
        "\nLogin, go to Find Course Sections.\n"
        "DO NOT search yet.\n"
        "Press ENTER when ready.\n"
    )

    print("Waiting for search request...")

    with page.expect_response(
        lambda r: "search.htmld" in r.url,
        timeout=120000
    ) as response_info:

        input(
            "\nNow perform a search in Workday.\n"
            "Then press ENTER here.\n"
        )

    response = response_info.value

    print("URL:")
    print(response.url)

    text = response.text()

    with open("search.json", "w", encoding="utf-8") as f:
        f.write(text)

    print("Saved search.json")

    input("\nPress ENTER to close.")