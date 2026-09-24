"""
M10 PMLS - Assignment 2 : Developing an API for Excel
Skin Clinic Marketing Campaign Analysis
"""

from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# -------------------------------------------------
# Create FastAPI app
# -------------------------------------------------
app = FastAPI(
    title="Skin Clinic Campaign Analysis API",
    description="Campaign response-rate analysis for Excel",
    version="1.0.0",
)

DATA_FILE = Path(__file__).parent / "skin_clinic_campaign.csv"

AGE_ORDER = ["<30", "30-50", ">50"]
PRODUCT_ORDER = ["1-4", "5-8", ">8"]


# -------------------------------------------------
# Health check endpoint
# -------------------------------------------------
@app.get("/health")
def health_check():
    return {"message": "Skin Clinic Campaign Analysis API is running"}


# -------------------------------------------------
# Data loading
# -------------------------------------------------
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)

    # Normalise the text columns so Yes/yes/YES all behave the same
    for col in ["Gender", "AgeGroup", "Purchase_Last_Quarter", "Response_to_Campaign"]:
        df[col] = df[col].astype(str).str.strip()

    # Binary flag used for every response-rate calculation
    df["Responded"] = (df["Response_to_Campaign"].str.lower() == "yes").astype(int)

    # Product usage bands required by Task 4
    df["Product_Usage"] = df["Unique_Products_Purchased"].apply(product_band)

    return df


def product_band(n: int) -> str:
    """Bucket the number of unique products bought in the last year."""
    if n <= 4:
        return "1-4"
    if n <= 8:
        return "5-8"
    return ">8"


# -------------------------------------------------
# Generic response-rate builder
# -------------------------------------------------
def response_rate(df: pd.DataFrame, column: str, analysis: str, order=None) -> pd.DataFrame:
    """Return customers, responders and response rate (%) for one dimension."""
    grouped = (
        df.groupby(column)
        .agg(Customers=("Responded", "size"), Responders=("Responded", "sum"))
        .reset_index()
    )

    grouped["Response_Rate_%"] = (
        grouped["Responders"] / grouped["Customers"] * 100
    ).round(2)

    # Keep the business-friendly ordering (<30, 30-50, >50) rather than A-Z
    if order:
        grouped[column] = pd.Categorical(grouped[column], categories=order, ordered=True)
        grouped = grouped.sort_values(column)
    else:
        grouped = grouped.sort_values("Response_Rate_%", ascending=False)

    grouped.insert(0, "Analysis", analysis)
    grouped = grouped.rename(columns={column: "Segment"})

    return grouped[["Analysis", "Segment", "Customers", "Responders", "Response_Rate_%"]]


# -------------------------------------------------
# The four required tables
# -------------------------------------------------
def build_tables(df: pd.DataFrame) -> dict:
    return {
        "gender": response_rate(df, "Gender", "Gender"),
        "age": response_rate(df, "AgeGroup", "Age Group", order=AGE_ORDER),
        "purchase": response_rate(
            df, "Purchase_Last_Quarter", "Purchase in Last Quarter"
        ),
        "products": response_rate(
            df, "Product_Usage", "Product Usage", order=PRODUCT_ORDER
        ),
    }


def clean(df: pd.DataFrame) -> list:
    """Make the frame JSON-safe and return it as a list of row dictionaries."""
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
    df = df.astype({"Customers": int, "Responders": int})
    return df.to_dict(orient="records")


# -------------------------------------------------
# API endpoint for Excel 
# -------------------------------------------------
@app.get("/campaign-analysis")
def campaign_analysis(table: str = "all"):
    """
    Campaign response-rate analysis in tabular form.

    table=all       -> all four analyses stacked into one table (default)
    table=gender    -> Task 1
    table=age       -> Task 2
    table=purchase  -> Task 3
    table=products  -> Task 4
    """
    try:
        df = load_data()
        tables = build_tables(df)

        key = table.strip().lower()

        if key in tables:
            return clean(tables[key])

        if key in ("all", ""):
            stacked = pd.concat(tables.values(), ignore_index=True)

            overall = pd.DataFrame(
                [
                    {
                        "Analysis": "Overall",
                        "Segment": "All Customers",
                        "Customers": len(df),
                        "Responders": int(df["Responded"].sum()),
                        "Response_Rate_%": round(df["Responded"].mean() * 100, 2),
                    }
                ]
            )

            return clean(pd.concat([overall, stacked], ignore_index=True))

        return {"error": f"Unknown table '{table}'. Use all, gender, age, purchase or products."}

    except Exception as e:
        return {"error": str(e)}


# -------------------------------------------------
# Landing page for RENDER
# -------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
      <head><title>Skin Clinic Campaign Analysis API</title></head>
      <body style="font-family:Segoe UI,Arial,sans-serif;max-width:700px;margin:40px auto">
        <h2>Skin Clinic Campaign Analysis API</h2>
        <p>M10 PMLS - Assignment 2: Developing an API for Excel</p>
        <ul>
          <li><a href="/campaign-analysis">/campaign-analysis</a> - all four analyses</li>
          <li><a href="/campaign-analysis?table=gender">/campaign-analysis?table=gender</a></li>
          <li><a href="/campaign-analysis?table=age">/campaign-analysis?table=age</a></li>
          <li><a href="/campaign-analysis?table=purchase">/campaign-analysis?table=purchase</a></li>
          <li><a href="/campaign-analysis?table=products">/campaign-analysis?table=products</a></li>
          <li><a href="/health">/health</a> &middot; <a href="/docs">/docs</a></li>
        </ul>
      </body>
    </html>
    """
