# Capturing Workday Search Results

This script captures raw search results from UBC Workday and saves them as JSON files for later processing.

**Note:** Workday searches are limited to approximately **2,000 results**. If a search returns more than 2,000 results, use a more specific search term.

## Step 1: Start the Capture Script

```bash
python3 capture.py
```

The script will display:

```text
Login and go to Find Course Sections.
DO NOT search yet.
Press ENTER when ready.
```

1. Log in to Workday.
2. Open **Find Course Sections**.
3. Do **not** perform a search yet.
4. Return to the terminal and press Enter.

## Step 2: Perform a Search

The script will begin waiting for the first search response:

```text
Waiting for first search response...
```

Perform your search in Workday. Once the results appear, return to the terminal and press Enter.

The first page will be saved automatically:

```text
Got first page:
Saved: responses/page_0.json

Total results: 1084
Last offset to capture: 1050
```

## Step 3: Capture Pagination Results

After saving the first page, the script will wait for pagination requests and save each page automatically:

```text
Waiting for pagination/50.htmld...
Saved: responses/page_50.json

Waiting for pagination/100.htmld...
Saved: responses/page_100.json

Waiting for pagination/150.htmld...
Saved: responses/page_150.json
```

This process continues until all result pages have been captured.

## Step 4: Build the Dataset

After the capture is complete, run:

```bash
python3 build_dataset.py
```

The processed dataset will be generated as:

```text
output/courses.json
```
