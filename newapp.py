import streamlit as st

# App title
st.title("🛍️ Discount Calculator App")

# Intro text
st.write("Enter product prices and apply a discount.")

# User input
prices_input = st.text_input("Enter prices (comma-separated)", "100, 250, 90")
discount = st.slider("Select discount (%)", min_value=0, max_value=100, value=10)

# Parse input
try:
    prices = [float(p.strip()) for p in prices_input.split(",") if p.strip()]
except ValueError:
    st.error("Please enter valid numbers, separated by commas.")
    prices = []

# Apply discount
if prices:
    discounted = [round(p * (1 - discount / 100), 2) for p in prices]

    st.subheader("Results")
    for original, new_price in zip(prices, discounted):
        st.write(f"💵 Original: {original} → Discounted: {new_price}")
else:
    st.info("Waiting for valid input...")