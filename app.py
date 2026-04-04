import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. इन्वेंटरी का डेटाबेस (शुरुआती स्टॉक) ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        "Veg Sausage": 50,
        "Chicken Jumbo Sausage": 50,
        "Hotdog Buns": 100,
        "Fries (kg)": 10.0,
        "Coke Syrup (Liters)": 5.0,
        "Sauces/Toppings (Units)": 200
    }

if 'sales_history' not in st.session_state:
    st.session_state.sales_history = []

# --- 2. पूरा मेन्यू और उसकी इन्वेंटरी खपत (BOM) ---
# Format: { "Item Name": [Bikri Price, Cost Price, {Inventory_Item: Consumption_Qty}] }
MENU_DATABASE = {
    "Classic Veg Hotdog": [99, 45, {"Veg Sausage": 1, "Hotdog Buns": 1, "Sauces/Toppings (Units)": 2}],
    "Classic Chicken Hotdog": [129, 60, {"Chicken Jumbo Sausage": 1, "Hotdog Buns": 1, "Sauces/Toppings (Units)": 2}],
    "Jumbo Chicken Hotdog": [159, 75, {"Chicken Jumbo Sausage": 1, "Hotdog Buns": 1, "Sauces/Toppings (Units)": 3}],
    "Small Meal (Add-on)": [69, 35, {"Fries (kg)": 0.1, "Coke Syrup (Liters)": 0.05}],
    "Medium Meal (Add-on)": [99, 54, {"Fries (kg)": 0.15, "Coke Syrup (Liters)": 0.08}],
    "Big Meal (Add-on)": [139, 68.5, {"Fries (kg)": 0.2, "Coke Syrup (Liters)": 0.1}]
}

st.set_page_config(page_title="NYH POS", layout="wide")
st.title("🌭 New York's Hotdog - Ultimate Billing System")

# --- SIDEBAR: STAFF & TIME ---
st.sidebar.markdown(f"**Current Session:** {datetime.now().strftime('%d %b, %Y')}")
staff_name = st.sidebar.selectbox("Active Staff", ["Jaanu", "Staff-1", "Staff-2"])

# --- SECTION 1: BILLING INTERFACE ---
st.header("🧾 New Bill")
c1, c2, c3 = st.columns(3)

with c1:
    cust_name = st.text_input("Customer Name", "Guest")
    cust_phone = st.text_input("Mobile No.", "")
with c2:
    selected_items = st.multiselect("Select Items", list(MENU_DATABASE.keys()))
with c3:
    discount_val = st.number_input("Flat Discount (₹)", 0)

if st.button("Complete Transaction & Print"):
    total_bill = 0
    total_cost = 0
    
    for item in selected_items:
        price, cost, components = MENU_DATABASE[item]
        total_bill += price
        total_cost += cost
        
        # ऑटोमैटिक इन्वेंटरी अपडेट
        for ingredient, qty in components.items():
            st.session_state.inventory[ingredient] -= qty
            
    final_amount = total_bill - discount_val
    gst = final_amount * 0.05
    grand_total = final_amount + gst
    
    # सेल रिकॉर्ड करना
    st.session_state.sales_history.append({
        "Time": datetime.now().strftime("%H:%M"),
        "Customer": cust_name,
        "Total": grand_total,
        "Profit": grand_total - total_cost - gst,
        "Staff": staff_name
    })
    
    st.success(f"Bill Generated! Total: ₹{grand_total:.2f}")
    st.write(f"Customer: {cust_name} | Items: {', '.join(selected_items)}")

# --- SECTION 2: LIVE INVENTORY TRACKING ---
st.divider()
st.header("📦 Inventory Status")
inv_df = pd.DataFrame(st.session_state.inventory.items(), columns=["Item", "Stock Remaining"])
st.data_editor(inv_df) # यहाँ से आप स्टॉक मैन्युअली अपडेट भी कर सकते हैं

# --- SECTION 3: PROFIT & LOSS / REPORTS ---
st.header("📊 Daily Report (P&L)")
if st.session_state.sales_history:
    report_df = pd.DataFrame(st.session_state.sales_history)
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Sales", f"₹{report_df['Total'].sum():.2f}")
    col_b.metric("Total Profit", f"₹{report_df['Profit'].sum():.2f}")
    col_c.metric("Orders Today", len(report_df))
    
    st.subheader("Recent Transactions")
    st.dataframe(report_df)
else:
    st.info("No sales recorded yet.")
