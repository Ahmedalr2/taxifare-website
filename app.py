import streamlit as st
import requests
from datetime import datetime

st.title("🚖 TaxiFareModel Front")

st.markdown("""
Welcome!  
Use this simple interface to estimate the price of a taxi ride in NYC 🗽.
""")

# 1️⃣ Collect input parameters
st.subheader("Enter your ride details:")

pickup_date = st.date_input("Pickup date", datetime.now())
pickup_time = st.time_input("Pickup time", datetime.now().time())

pickup_longitude = st.number_input("Pickup longitude", value=-73.985428, format="%.6f")
pickup_latitude = st.number_input("Pickup latitude", value=40.748817, format="%.6f")

dropoff_longitude = st.number_input("Dropoff longitude", value=-73.985428, format="%.6f")
dropoff_latitude = st.number_input("Dropoff latitude", value=40.748817, format="%.6f")

passenger_count = st.number_input("Number of passengers", min_value=1, max_value=8, value=1)

# Combine date and time into a single string
pickup_datetime = f"{pickup_date} {pickup_time}"

# 2️⃣ Build the parameters dictionary
params = {
    "pickup_datetime": pickup_datetime,
    "pickup_longitude": pickup_longitude,
    "pickup_latitude": pickup_latitude,
    "dropoff_longitude": dropoff_longitude,
    "dropoff_latitude": dropoff_latitude,
    "passenger_count": passenger_count
}

# 3️⃣ API URL
url = 'https://taxifare.lewagon.ai/predict'
# You can change it to your own API endpoint later if you have one

# 4️⃣ Call the API when user clicks the button
if st.button("Get Fare Prediction 💰"):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        prediction = response.json().get("fare", None)
        if prediction:
            st.success(f"Predicted fare: **${round(prediction, 2)}**")
        else:
            st.warning("No prediction received from the API.")
    else:
        st.error(f"Error: {response.status_code}. Could not reach the API.")

st.markdown("""
---
💡 *Tip:* You can easily replace the API URL above with your own endpoint once you deploy your model!
""")
