import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Project paths
project_root = Path(__file__).resolve().parents[2]

excel_file = project_root / "output" / "peer_comparison.xlsx"

output_dir = project_root / "reports" / "radar_charts"
output_dir.mkdir(parents=True, exist_ok=True)

metrics = [
    "return_on_equity_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "compounded_profit_growth",
    "compounded_sales_growth",
    "asset_turnover",
]

labels = [
    "ROE",
    "NPM",
    "OPM",
    "D/E",
    "FCF",
    "PAT CAGR",
    "Sales CAGR",
    "Asset Turnover",
]

xls = pd.ExcelFile(excel_file)

for sheet in xls.sheet_names:

    df = pd.read_excel(xls, sheet_name=sheet)

    if df.empty:
        continue

    df = df.dropna(subset=["company_name"])

    peer_avg = df[metrics].mean()

    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))

    for _, row in df.iterrows():

        company = row["company_name"]
        company_id = row["company_id"]

        values = row[metrics].fillna(0).astype(float).values
        values = np.concatenate((values, [values[0]]))

        avg = peer_avg.values.astype(float)
        avg = np.concatenate((avg, [avg[0]]))

        fig = plt.figure(figsize=(7, 7))
        ax = plt.subplot(111, polar=True)

        ax.plot(angles, values, linewidth=2, label=company)
        ax.fill(angles, values, alpha=0.25)

        ax.plot(
            angles,
            avg,
            linestyle="--",
            linewidth=2,
            label="Peer Average",
        )

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)

        ax.set_title(
            f"{company}\n{sheet}",
            fontsize=12,
        )

        ax.legend(loc="upper right")

        plt.savefig(
            output_dir / f"{company_id}_radar.png",
            dpi=300,
            bbox_inches="tight",
        )

        plt.close()

print("=" * 60)
print("Radar charts generated successfully.")
print(f"Location: {output_dir}")
print("=" * 60)