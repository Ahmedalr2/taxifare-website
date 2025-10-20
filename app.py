import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Taxi Fare Predictor", page_icon="🚕", layout="centered")

# --- Header ---
st.markdown("""
<h1 style='text-align:center; color:#FFD700;'>🚖 NYC Taxi Fare Predictor</h1>
<p style='text-align:center; color:gray;'>Select your pickup and dropoff locations to estimate your fare!</p>
<hr style="border:1px solid #f0f0f0;">
""", unsafe_allow_html=True)

# --- Initialize session states ---
if "pickup" not in st.session_state:
    st.session_state.pickup = None
if "dropoff" not in st.session_state:
    st.session_state.dropoff = None

# --- Ride Details ---
st.markdown("### 🗓️ Ride Details")

pickup_datetime = st.text_input(
    "📅 Pickup Date & Time (YYYY-MM-DD HH:MM:SS)",
    value=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)
passenger_count = st.number_input("👥 Passenger Count", min_value=1, max_value=8, value=1)

# --- Map Section ---
st.markdown("### 🗺️ Select Pickup & Dropoff on Map")

# Default center
nyc_center = [40.758, -73.9855]

# Create map and add existing markers
m = folium.Map(location=nyc_center, zoom_start=12)

if st.session_state.pickup:
    folium.Marker(
        st.session_state.pickup,
        tooltip="Pickup",
        icon=folium.Icon(color="green", icon="play"),
    ).add_to(m)

if st.session_state.dropoff:
    folium.Marker(
        st.session_state.dropoff,
        tooltip="Dropoff",
        icon=folium.Icon(color="red", icon="flag"),
    ).add_to(m)

if st.session_state.pickup and st.session_state.dropoff:
    folium.PolyLine(
        [st.session_state.pickup, st.session_state.dropoff],
        color="blue",
        weight=4,
        opacity=0.7
    ).add_to(m)

map_click = st_folium(m, width=700, height=500)

# --- Map Interaction ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🟢 Set as Pickup"):
        if map_click and map_click.get("last_clicked"):
            st.session_state.pickup = (
                map_click["last_clicked"]["lat"],
                map_click["last_clicked"]["lng"],
            )
            st.success(f"Pickup set at {st.session_state.pickup}")
        else:
            st.warning("Click a location on the map first!")

with col2:
    if st.button("🔴 Set as Dropoff"):
        if map_click and map_click.get("last_clicked"):
            st.session_state.dropoff = (
                map_click["last_clicked"]["lat"],
                map_click["last_clicked"]["lng"],
            )
            st.success(f"Dropoff set at {st.session_state.dropoff}")
        else:
            st.warning("Click a location on the map first!")

# --- Reset Button ---
if st.button("♻️ Reset Locations"):
    st.session_state.pickup = None
    st.session_state.dropoff = None
    st.rerun()

# --- When both points are selected ---
if st.session_state.pickup and st.session_state.dropoff:
    pickup_lat, pickup_lon = st.session_state.pickup
    dropoff_lat, dropoff_lon = st.session_state.dropoff

    distance_km = geodesic(st.session_state.pickup, st.session_state.dropoff).km
    duration_min = (distance_km / 35) * 60  # assume 35 km/h average

    st.markdown(f"""
    ### 📊 Trip Summary
    - Pickup: **{pickup_lat:.4f}, {pickup_lon:.4f}**
    - Dropoff: **{dropoff_lat:.4f}, {dropoff_lon:.4f}**
    - Distance: **{distance_km:.2f} km**
    - Estimated Duration: **{duration_min:.1f} min**
    - Passengers: **{passenger_count}**
    """)

    # --- Predict Fare ---
    if st.button("💰 Predict Fare"):
        url = "https://taxifare.lewagon.ai/predict"
        params = {
            "pickup_datetime": pickup_datetime,
            "pickup_longitude": pickup_lon,
            "pickup_latitude": pickup_lat,
            "dropoff_longitude": dropoff_lon,
            "dropoff_latitude": dropoff_lat,
            "passenger_count": passenger_count
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            prediction = response.json().get("fare", None)
            if prediction:
                base_fare = 2.5
                distance_fee = distance_km * 1.5
                time_fee = (duration_min / 60) * 3
                total_estimate = base_fare + distance_fee + time_fee

                st.success(f"🚕 Predicted Fare: **${round(prediction, 2)}**")
                st.markdown("### 💡 Fare Breakdown:")
                st.write(f"• Base Fare: ${base_fare:.2f}")
                st.write(f"• Distance Fee: ${distance_fee:.2f}")
                st.write(f"• Time Fee: ${time_fee:.2f}")
                st.info(f"**Approximate total:** ${total_estimate:.2f}")
            else:
                st.warning("⚠️ No prediction received from API.")
        else:
            st.error(f"❌ API Error: {response.status_code}")

# --- Footer ---
st.markdown("""
---
<p style='text-align:center; color:gray;'>
Built with ❤️ using <b>Streamlit</b> + <b>Folium</b><br>
Interactive Taxi Fare Prediction App
</p>
""", unsafe_allow_html=True)
