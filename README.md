# gmapstoexcel
# FULL VIBED!!! SOMEONE NEEDED, A MENI VPADLU V TOMO SILNO ROZBIRATSA
A Python project that:

1. searches businesses with **Google Places API (New)**
2. maps the raw Google response into a clean schema
3. optionally enriches businesses with:
   - **emails** found on their websites
   - **social links** found on their websites
4. exports the final data to **Excel** and **CSV**

---

## SetUp

Follow these steps to run the project on your own machine.

### 1. Clone the project
```bash
git clone <your-repo-url>
cd gmapstoexcel
```

### 2. Create and activate a virtual environment

#### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

If you do not have a ready `requirements.txt`, install manually:

```bash
pip install requests beautifulsoup4 pandas openpyxl python-dotenv
```

### 4. Create a Google Cloud project
Go to Google Cloud Console and create a new project.

### 5. Enable **Places API (New)**
Inside your Google Cloud project:

- open **APIs & Services**
- go to **Library**
- search for **Places API (New)**
- enable it

### 6. Enable billing
Google Places API requires billing to be enabled on the project.

- open **Billing**
- link or create a billing account
- make sure the current project is linked to it

### 7. Create an API key
Inside **APIs & Services → Credentials**:

- click **Create Credentials**
- choose **API Key**

For first-time testing, it is easiest to start with a basic key and restrict it later.

### 8. Create a `.env` file
In the project root, create:

```text
.env
```

Put your API key inside it:

```env
GOOGLE_PLACES_API_KEY=your_api_key_here
```

### 9. Make sure `main.py` loads the environment
This project expects:

```python
from dotenv import load_dotenv
load_dotenv()
```

before reading `GOOGLE_PLACES_API_KEY`.

### 10. Run the project
Start the pipeline with:

```bash
python main.py
```

### 11. Check the output
If everything works, the script will:

- search businesses using Google Places API (New)
- enrich them with website emails/socials when possible
- save the results into the `output/` folder

Example output path:

```text
output/skincare_pakistan123.xlsx
```

The full saved path is also printed in the terminal.

---

## What it can get right now

For each business, the pipeline can produce:

- `name`
- `address`
- `rating`
- `website`
- `phone`
- `email`
- `instagram`
- `facebook`
- `linkedin`
- `tiktok`

---

## Current behavior

### Data source
Business search comes from **Google Places API (New)**.

### Email extraction
If a business has a website, the project:
- visits the homepage
- checks common contact/about pages
- extracts visible emails and `mailto:` links

### Social extraction
If a business has a website, the project:
- scans the website HTML
- extracts links to:
  - Instagram
  - Facebook
  - LinkedIn
  - TikTok

### No-website businesses
Right now, if a business has **no website**, email/social enrichment is skipped.

---

## Project structure

```text
gmapstoexcel/
├── client.py
├── mapper.py
├── email_extractor.py
├── website_social_extractor.py
├── pipeline.py
├── exporter.py
├── main.py
├── requirements.txt
└── README.md
```

---

## How it works

### `client.py`
Handles communication with **Google Places API (New)**.

Responsibilities:
- sends search requests
- handles retries
- handles pagination
- returns raw Google place objects

### `mapper.py`
Converts raw Google place objects into a clean internal schema.

It does **not** make network calls.

### `email_extractor.py`
Visits a business website and tries to extract emails.

### `website_social_extractor.py`
Visits a business website and tries to extract social links.

### `pipeline.py`
Orchestrates the full workflow:
- search
- map
- enrich
- return final list

### `exporter.py`
Exports results to:
- Excel (`.xlsx`)
- CSV (`.csv`)

### `main.py`
Entry point for running the full pipeline.

---

## Query examples

You can search in English, Ukrainian, or other languages supported by Google Places.

Examples:

```python
"Skincare clinic in Pakistan"
"Дерматологічні клініки Львів"
"айті компанії у Львові"
```

---

## Pagination

The project supports pagination through the Places API.

That means one query can return more than one page of businesses if Google provides additional pages.

You control this in `main.py` with:

- `max_pages`
- `max_results`

Example:

```python
results = pipeline.run(
    "Дерматологічні клініки Львів",
    max_pages=3,
    max_results=50,
    language="uk",
    region="UA",
    enrich_emails=True,
    enrich_socials=True,
)
```

### Important note
If you only get **20 results**, that usually means:
- Google only returned one page for that query
- or no `nextPageToken` was returned

It does **not** mean Excel is limited to 20 rows.

---

## Output schema

Each business becomes a dict like this:

```python
{
    "name": "SoftServe",
    "address": "вулиця ... Львів, Львівська область, Україна",
    "rating": 4.6,
    "website": "https://www.softserveinc.com/",
    "phone": "+380 ...",
    "email": "info@example.com",
    "instagram": "https://www.instagram.com/...",
    "facebook": "https://www.facebook.com/...",
    "linkedin": "https://www.linkedin.com/company/...",
    "tiktok": None,
}
```

---

## Example `main.py`

```python
import os
from client import PlacesClient
from pipeline import PlacesPipeline
from exporter import PlacesExporter
from dotenv import load_dotenv

load_dotenv()


def main():
    print("[Start] Initializing...")
    places_client = PlacesClient(api_key=os.getenv("GOOGLE_PLACES_API_KEY"))
    pipeline = PlacesPipeline(places_client)
    exporter = PlacesExporter()

    print("[Run] Starting pipeline...")
    results = pipeline.run(
        "Skincare clinic in Pakistan",
        max_pages=3,
        max_results=25,
        language="en",
        region="PK",
        enrich_emails=True,
        enrich_socials=True,
    )

    print("[Save] Exporting...")
    excel_path = exporter.to_excel(results, filename="skincare_pakistan.xlsx")

    print(f"[Done] Saved Excel to: {excel_path.resolve()}")


if __name__ == "__main__":
    main()
```

---

## Current limitations

- Google Places does **not** provide business emails directly
- Google Places does **not** provide Instagram/Facebook/etc directly
- email/social extraction only works if a website exists
- some websites:
  - hide emails with JavaScript
  - use contact forms only
  - block bots
- some businesses may not have any public contact info beyond phone

---

## Common first-run issues

### `REQUEST_DENIED`
Usually means one of these:
- billing is not enabled
- Places API (New) is not enabled
- API key is missing or incorrect
- `.env` was not loaded correctly

### Only 20 results returned
This usually means:
- Google only returned one page for that query
- or no `nextPageToken` was returned for additional pages

### No emails found
That is normal for some websites. Many businesses:
- hide emails
- use contact forms only
- do not publish email addresses publicly

---

## Future improvements

Possible next steps:
- deduplication
- logging instead of `print()`
- retry logic for website extraction
- `needs_manual_review` flag for no-website businesses
- async enrichment for faster runs
- fallback social discovery for businesses without websites
