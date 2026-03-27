from pathlib import Path
from typing import Any
import pandas as pd


class PlacesExporter:
    COLUMNS = [
        "name",
        "address",
        "rating",
        "website",
        "phone",
        "email",
        "instagram",
        "facebook",
        "linkedin",
        "tiktok",
    ]

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _to_dataframe(self, places: list[dict[str, Any]]) -> pd.DataFrame:
        df = pd.DataFrame(places)

        for column in self.COLUMNS:
            if column not in df.columns:
                df[column] = None

        return df[self.COLUMNS]

    def to_excel(
        self,
        places: list[dict[str, Any]],
        filename: str = "places.xlsx",
        sheet_name: str = "Places",
    ) -> Path:
        df = self._to_dataframe(places)
        output_path = self.output_dir / filename
        df.to_excel(output_path, index=False, sheet_name=sheet_name)
        return output_path

    def to_csv(
        self,
        places: list[dict[str, Any]],
        filename: str = "places.csv",
    ) -> Path:
        df = self._to_dataframe(places)
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        return output_path