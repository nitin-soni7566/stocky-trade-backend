import pandas as pd
import re

MASTER_FILE = "nsecash.csv"
NIFTY_200_FILE = "nifty200.csv"
OUTPUT_FILE = "nifty200_master.csv"


def clean_text(value):
    value = str(value).upper().strip()
    value = re.sub(r"[^A-Z0-9]", "", value)
    return value


def load_master_file():
    master = pd.read_csv(
        MASTER_FILE,
        header=None,
        sep=",",
        engine="python",
        on_bad_lines="skip",
    )

    print("Master columns found:", master.shape[1])

    if master.shape[1] == 15:
        master.columns = [
            "segment",
            "token",
            "symbol",
            "tradingsymbol",
            "instrument_type",
            "expiry",
            "ticksize",
            "lotsize",
            "optiontype",
            "strike",
            "priceprec",
            "multiplier",
            "isin",
            "pricemult",
            "company",
        ]

    elif master.shape[1] == 6:
        master.columns = [
            "segment",
            "token",
            "symbol",
            "tradingsymbol",
            "instrument_type",
            "company",
        ]

    else:
        print(master.head())
        raise ValueError(f"Unsupported master column count: {master.shape[1]}")

    return master


def load_nifty200_file():
    nifty = pd.read_csv(NIFTY_200_FILE)

    print("Nifty columns:", list(nifty.columns))

    symbol_col = None
    company_col = None

    for col in nifty.columns:
        col_clean = col.strip().lower()

        if col_clean in ["symbol", "symbols", "ticker"]:
            symbol_col = col

        if col_clean in ["company name", "company", "name"]:
            company_col = col

    if not symbol_col and not company_col:
        print(nifty.head())
        raise ValueError("No Symbol or Company Name column found in nifty200.csv")

    nifty_keys = set()

    if symbol_col:
        nifty_keys.update(nifty[symbol_col].dropna().apply(clean_text))

    if company_col:
        nifty_keys.update(nifty[company_col].dropna().apply(clean_text))

    return nifty_keys


def main():
    master = load_master_file()
    nifty_keys = load_nifty200_file()

    master["symbol_key"] = master["symbol"].apply(clean_text)
    master["tradingsymbol_key"] = master["tradingsymbol"].apply(clean_text)
    master["company_key"] = master["company"].apply(clean_text)

    result = master[
        master["symbol_key"].isin(nifty_keys)
        | master["tradingsymbol_key"].isin(nifty_keys)
        | master["company_key"].isin(nifty_keys)
    ].copy()

    result.drop(
        columns=["symbol_key", "tradingsymbol_key", "company_key"],
        inplace=True,
    )

    result.to_csv(OUTPUT_FILE, index=False)

    print("Total found:", len(result))

    if len(result) > 0:
        print(result[["segment", "token", "symbol", "tradingsymbol", "company"]])
    else:
        print("No matches found. Check nifty200.csv column values.")


if __name__ == "__main__":
    main()