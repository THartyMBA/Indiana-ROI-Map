# indiana_roi_map.py
"""
Indiana County ROI & Property-Tax Heatmap  🗺️🏡
────────────────────────────────────────────────────────────────────────────
**Proof-of-concept**

• Pulls LIVE data from the U.S. Census ACS 5-Year API (2022 release):  
  - Median Gross Rent  (B25064_001E)  
  - Median Home Value  (B25077_001E)  
  - Median Property Taxes (B25092_001E)

• Calculates  
  **Rental ROI  ≈  (Median Rent × 12) ÷ Median Home Value**  
  **Tax Rate     ≈  Median Taxes   ÷ Median Home Value**

• Joins the metrics to TIGER/Line county polygons, filters state = Indiana.

• Interactive Folium choropleth inside Streamlit.  
  Users can switch between *ROI* and *Tax Rate*, hover a county for exact %,
  and download the underlying dataset.

> Demo-grade only — no caching, auth, or SLA monitoring.  
> Need a production geospatial analytics stack? → https://drtomharty.com/bio
"""
# ─────────────────────────────────── imports ──────────────────────────────
import io, json, requests
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import streamlit as st

# ──────────────────────────── data loaders ────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_acs_indiana():
    url = (
        "https://api.census.gov/data/2022/acs/acs5?"
        "get=NAME,B25064_001E,B25077_001E,B25092_001E"
        "&for=county:*&in=state:18"
    )
    resp = requests.get(url, timeout=30).json()
    cols = resp[0]
    df   = pd.DataFrame(resp[1:], columns=cols)
    df[["B25064_001E","B25077_001E","B25092_001E"]] = df[
        ["B25064_001E","B25077_001E","B25092_001E"]
    ].astype(float)
    df["fips"] = df["state"] + df["county"]
    df["roi"]  = (df["B25064_001E"] * 12) / df["B25077_001E"]
    df["tax_rate"] = df["B25092_001E"] / df["B25077_001E"]
    return df[["NAME","fips","roi","tax_rate"]]

@st.cache_data(show_spinner=False)
def load_indiana_county_shapes():
    shp_url = (
        "https://www2.census.gov/geo/tiger/GENZ2018/shp/"
        "cb_2018_us_county_500k.zip"
    )
    gdf = gpd.read_file(shp_url)
    gdf = gdf[gdf["STATEFP"] == "18"]  # Indiana
    gdf["fips"] = gdf["STATEFP"] + gdf["COUNTYFP"]
    return gdf[["fips","geometry","NAME"]]

# ─────────────────────────────── UI ───────────────────────────────────────
st.set_page_config(page_title="Indiana Rental ROI Map", layout="wide")
st.title("📍 Indiana County Rental ROI & Property-Tax Heatmap")

st.info(
    "🔔 **Demo Notice**  \n"
    "Live ACS data, single-file Streamlit app. "
    "For enterprise analytics or multi-state support, "
    "[contact me](https://drtomharty.com/bio).",
    icon="💡"
)

with st.spinner("Fetching data…"):
    df  = fetch_acs_indiana()
    gdf = load_indiana_county_shapes()
    merged = gdf.merge(df, on="fips")

metric = st.radio("Metric", ["Rental ROI (%)", "Property Tax Rate (%)"], index=0,
                  help="ROI = (median rent × 12) ÷ median home value")

if metric.startswith("Rental"):
    merged["value"] = merged["roi"] * 100
    legend = "Rental ROI (%)"
else:
    merged["value"] = merged["tax_rate"] * 100
    legend = "Property Tax Rate (%)"

# ─── create folium map ────────────────────────────────────────────────────
center = [40.27, -86.13]  # Indiana centroid
m = folium.Map(location=center, zoom_start=7, tiles="cartodbpositron")

folium.Choropleth(
    geo_data=json.loads(merged.to_json()),
    name="choropleth",
    data=merged,
    columns=["fips", "value"],
    key_on="feature.properties.fips",
    fill_color="YlGnBu",
    fill_opacity=0.8,
    line_opacity=0.2,
    legend_name=legend,
).add_to(m)

# tooltips
folium.GeoJson(
    merged,
    name="labels",
    style_function=lambda x: {"fillOpacity": 0, "color": "transparent"},
    tooltip=folium.features.GeoJsonTooltip(
        fields=["NAME", "value"],
        aliases=["County", legend],
        localize=True,
        sticky=False,
    ),
).add_to(m)

folium_static(m, width=900, height=600)

# ─── download button ──────────────────────────────────────────────────────
st.download_button(
    "⬇️ Download metrics CSV",
    data=merged[["NAME","roi","tax_rate"]].rename(
        columns={"NAME":"county","roi":"rental_roi","tax_rate":"property_tax_rate"}
    ).to_csv(index=False).encode(),
    file_name="indiana_county_roi_tax.csv",
    mime="text/csv",
)
