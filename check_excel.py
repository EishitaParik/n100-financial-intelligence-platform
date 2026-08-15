import pandas as pd

print("=" * 70)
print("FINANCIAL RATIOS EXCEL")
print("=" * 70)

df = pd.read_excel("data/raw/financial_ratios.xlsx")

print("\nColumns:")
print(df.columns.tolist())

print("\nCOALINDIA rows:")
print(
    df[
        df.astype(str).apply(
            lambda row: row.str.contains(
                "COALINDIA",
                case=False,
                na=False
            ).any(),
            axis=1
        )
    ].to_string(index=False)
)

print("\n" + "=" * 70)
print("PROFIT & LOSS EXCEL")
print("=" * 70)

pl = pd.read_excel("data/raw/profitandloss.xlsx")

print("\nColumns:")
print(pl.columns.tolist())

print("\nCOALINDIA rows:")
print(
    pl[
        pl.astype(str).apply(
            lambda row: row.str.contains(
                "COALINDIA",
                case=False,
                na=False
            ).any(),
            axis=1
        )
    ].to_string(index=False)
)
