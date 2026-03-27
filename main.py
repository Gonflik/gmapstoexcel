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
        "Дерматологічні клініки Україна",
        max_pages=3,
        max_results=50,
        language="uk",
        region="UA",
        enrich_emails=True,
        enrich_socials=True,
    )

    print("[Save] Exporting...")
    excel_path = exporter.to_excel(results, filename="dermatologi_kyiv_data.xlsx")
    #csv_path = exporter.to_csv(results, filename="it_companies_lviv.csv")

    print(f"[Done] Saved Excel to: {excel_path.resolve()}")
    #print(f"[Done] Saved CSV to: {csv_path.resolve()}")


if __name__ == "__main__":
    main()