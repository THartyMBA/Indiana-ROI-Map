# indiana_roi_map.py
"""
Indiana County ROI & Property-Tax Heatmap  🗺️🏡
────────────────────────────────────────────────────────────────────────────
Fetches live ACS data, then overlays it on a filtered US-counties GeoJSON
(that we load via HTTP). No shapefile downloads, no geopandas install.

• Rental ROI  ≈ (Median Rent × 12) ÷ Median Home Value  
• Tax Rate   ≈ Median Taxes   ÷ Median Home Value  

Switch between metrics and download the CSV.
"""
import json, requests
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static

# ─────────────────────────────── ACS DATA ────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_acs_indiana():
    url = (
        "https://api.census.gov/data/2022/acs/acs5"
        "?get=NAME,B25064_001E,B25077_001E,B25092_001E"
        "&for=county:*&in=state:18"
    )
    resp = requests.get(url, timeout=30).json()
    cols = resp[0]
    df = pd.DataFrame(resp[1:], columns=cols)
    df[["B25064_001E","B25077_001E","B25092_001E"]] = df[
        ["B25064_001E","B25077_001E","B25092_001E"]
    ].astype(float)
    df["fips"] = df["state"] + df["county"]
    df["rental_roi"] = (df["B25064_001E"] * 12) / df["B25077_001E"]
    df["property_tax_rate"] = df["B25092_001E"] / df["B25077_001E"]
    return df[["NAME","fips","rental_roi","property_tax_rate"]]

# ─────────────────────── US COUNTIES GEOJSON ─────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_us_counties_geo():
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    gj = requests.get(url, timeout=30).json()
    # filter only Indiana (FIPS start with "18")
    feats = [f for f in gj["features"] if f["id"].startswith("18")]
    return {"type":"FeatureCollection", "features":feats}

# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Indiana Rental ROI Map", layout="wide")
st.title("📍 Indiana County Rental ROI & Property-Tax Heatmap")

st.info(
    "🔔 **Demo Notice**  \n"
    "Uses live ACS data + public GeoJSON (no shapefiles). "
    "For enterprise geospatial analytics, [contact me](https://drtomharty.com/bio).",
    icon="💡"
)

# load data & geojson
with st.spinner("Fetching data…"):
    df = fetch_acs_indiana()
    geojson = fetch_us_counties_geo()

metric = st.radio(
    "Metric",
    ["Rental ROI (%)", "Property Tax Rate (%)"],
    index=0,
    help="Rental ROI = (median rent × 12) ÷ median home value"
)

if metric.startswith("Rental"):
    df["value"] = df["rental_roi"] * 100
    legend = "Rental ROI (%)"
else:
    df["value"] = df["property_tax_rate"] * 100
    legend = "Property Tax Rate (%)"

# build map
m = folium.Map(location=[40.27, -86.13], zoom_start=7, tiles="cartodbpositron")

folium.Choropleth(
    geo_data=geojson,
    data=df,
    columns=["fips", "value"],
    key_on="feature.id",
    fill_color="YlGnBu",
    fill_opacity=0.8,
    line_opacity=0.2,
    legend_name=legend,
).add_to(m)

# tooltips
folium.GeoJson(
    geojson,
    name="labels",
    style_function=lambda _: {"fillOpacity": 0, "color": "transparent"},
    tooltip=folium.features.GeoJsonTooltip(
        fields=["NAME"],
        aliases=["County"],
        labels=False,
        sticky=False,
        toLocaleString=True,
        localize=True,
        style=("background-color: white; color: #333; font-family: arial; font-size: 12px; padding: 5px;"),
        value_formatter=lambda feat_id, feature: f"{df.loc[df.fips==feature['id'], 'value'].values[0]:.2f}%"
    ),
).add_to(m)

folium_static(m, width=900, height=600)

# download CSV
st.download_button(
    "⬇️ Download data CSV",
    data=df[["NAME","rental_roi","property_tax_rate"]]
         .rename(columns={"NAME":"county"})
         .to_csv(index=False)
         .encode(),
    file_name="indiana_county_roi_tax.csv",
    mime="text/csv"
)

