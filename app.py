import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- 1. गूगल शीट से कनेक्शन ---
def connect_to_sheet():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # Streamlit Secrets से चाबी उठाना
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        # आपकी सही शीट आईडी
        sheet = client.open_by_key("1b2uu70b8y-cDX8FVDI0JbQzrV7LYDUXwVtN09vACJmw").sheet1
        return sheet
    except Exception as e:
        st.error(f"Sheet Connection Error: {e}")
        return None

# --- 2. इन्वेंटरी और मेन्यू सेटअप ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        "Hotdog Buns": 100, "Normal Sausages": 50, "Veg Sausages": 30,
        "Cheese Sausages": 20, "Chicken Sausages": 40, "Fries (kg)": 10.0,
        "Chicken Nuggets (Pcs)": 200, "Pizza Pockets (Pcs)": 100,
        "Coke Syrup (Liters)": 5.0, "Sauces/Toppings (Units)": 200
    }

MENU_DATABASE = {
    "New York's Hotdog": [99, 45, {"Normal Sausages": 1, "Hotdog Buns": 1}],
    "Cheese Hotdog": [109, 50, {"Cheese Sausages": 1, "Hotdog Buns": 1}],
    "Breakfast Hotdog": [109, 50, {"Normal Sausages": 1, "Hotdog Buns": 1}],
    "Chicago's Hotdog": [119, 55, {"Normal Sausages": 1, "Hotdog Buns": 1}],
    "BBQ Hotdog": [129, 60, {"Normal Sausages": 1, "Hotdog Buns": 1}],
    "Veg Indian Hotdog": [129, 60, {"Veg Sausages": 1, "Hotdog Buns": 1}],
    "Chili Hotdog": [129, 60, {"Normal Sausages": 1, "Hotdog Buns": 1}],
    "Coney Onion Hotdog": [139, 65, {"Normal Sausages": 1, "Hotdog Buns": 1}],
    "Mexican Street Hotdog": [149, 70, {"Chicken Sausages": 1, "Hotdog Buns": 1}],
    "Loaded Hotdog": [159, 75, {"Normal Sausages": 1, "Hotdog Buns": 1}],
    "Small Fries": [59, 20, {"Fries (kg)": 0.1}],
    "Medium Fries": [79, 30, {"Fries (kg)": 0.15}],
    "Large Fries": [119, 45, {"Fries (kg)": 0.2}],
    "Chicken Nuggets (6 Pcs)": [109, 50, {"Chicken Nuggets (Pcs)": 6}],
    "Chicken Nuggets (9 Pcs)": [149, 70, {"Chicken Nuggets (Pcs)": 9}],
    "Chicken Nuggets Bucket (15 Pcs)": [229, 110, {"Chicken Nuggets (Pcs)": 15}],
    "Pizza Pockets (3 Pcs)": [89, 40, {"Pizza Pockets (Pcs)": 3}],
    "Pizza Pockets (5 Pcs)": [139, 65, {"Pizza Pockets (Pcs)": 5}],
    "Cold Drink (Small)": [20, 10, {"Coke Syrup (Liters)": 0.03}],
    "Cold Drink (Medium)": [40, 15, {"Coke Syrup (Liters)": 0.05}],
    "Cold Drink (Large)": [50, 20, {"Coke Syrup (Liters)": 0.08}], 
    "Party Pack": [70, 30, {"Coke Syrup (Liters)": 0.15}],
    "Small Meal (Add-on)": [69, 30, {"Fries (kg)": 0.1, "Coke Syrup (Liters)": 0.03}],
    "Medium Meal (Add-on)": [99, 45, {"Fries (kg)": 0.15, "Coke Syrup (Liters)": 0.05}],
    "Big Meal (Add-on)": [139, 65, {"Fries (kg)": 0.2, "Coke Syrup (Liters)": 0.08}]
}

st.title("🌭 NY Hotdog - Billing System")

# --- 3. बिलिंग इंटरफ़ेस ---
st.header("🧾 New Bill")
col1, col2 = st.columns(2)
with col1:
    cust_name = st.text_input("Customer Name", "Guest")
with col2:
    staff_name = st.selectbox("Staff", ["Manager", "Staff 1", "Staff 2"])

selected_items = st.multiselect("Select Items", list(MENU_DATABASE.keys()))
discount = st.number_input("Discount (₹)", min_value=0, value=0)

if st.button("Complete Transaction"):
    if selected_items:
        total_amount = sum(MENU_DATABASE[i][0] for i in selected_items)
        total_cost = sum(MENU_DATABASE[i][1] for i in selected_items)
        grand_total = total_amount - discount
        profit = grand_total - total_cost
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        # स्टॉक कम करना
        for item in selected_items:
            reqs = MENU_DATABASE[item][2]
            for ingredient, qty in reqs.items():
                st.session_state.inventory[ingredient] -= qty

        # गूगल शीट में डेटा भेजना
        sheet = connect_to_sheet()
        if sheet:
            sheet.append_row([curr_time, staff_name, cust_name, ", ".join(selected_items), grand_total, profit])
            st.success(f"✅ Bill Saved to Google Sheet! Total: ₹{grand_total}")
        else:
            st.warning("⚠️ Data saved locally but failed to reach Google Sheet. Check Secrets!")

# --- 4. इन्वेंटरी और रिपोर्ट ---
st.markdown("---")
st.header("📦 Inventory Status")
st.table(pd.DataFrame(st.session_state.inventory.items(), columns=["Item", "Stock Remaining"]))

if st.button("Refresh Sales Report"):
    sheet = connect_to_sheet()
    if sheet:
        data = sheet.get_all_records()
        if data:
            st.dataframe(pd.DataFrame(data))
