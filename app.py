import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json

# --- पेज की सेटिंग ---
st.set_page_config(page_title="New York's Hotdog", page_icon="🌭", layout="wide")

# --- 1. गूगल शीट से कनेक्शन (सीधा फाइल से - सबसे सुरक्षित तरीका) ---
@st.cache_resource
def init_connection():
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets", 
            "https://www.googleapis.com/auth/drive"
        ]
        
        # आपकी अपलोड की हुई फाइल का पूरा नाम
        key_file = "hotdog-billing-492413-417ab2c8f943.txt"
        
        # फाइल को पढ़ना
        with open(key_file) as f:
            credentials_dict = json.load(f)
            
        creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"कनेक्शन एरर: {e}")
        return None

client = init_connection()

SHEET_NAME = "NYH_Billing" 

st.title("🌭 New York's Hotdog - Billing System")

RAW_MATERIALS = [
    "Hotdog Bun", "Classic Sausage", "Cheese Sausage", "Veg Sausage", 
    "Paneer/Egg Patty", "Bacon/Pepperoni", "French Fries Portion", 
    "Chicken Nuggets (Pcs)", "Pizza Pockets (Pcs)", "Cold Drink Cup", "Packaging Box"
]

RECIPE_MAP = {
    "New York's Hotdog (Classic)": {"Hotdog Bun": 1, "Classic Sausage": 1, "Packaging Box": 1},
    "Cheese Hotdog (Cheese Sausage)": {"Hotdog Bun": 1, "Cheese Sausage": 1, "Packaging Box": 1},
    "Breakfast Hotdog (Paneer & Egg)": {"Hotdog Bun": 1, "Paneer/Egg Patty": 1, "Packaging Box": 1},
    "Chicago's Hotdog (Jalapeno/Onion)": {"Hotdog Bun": 1, "Classic Sausage": 1, "Packaging Box": 1},
    "Bdq Hotdog (Smoky Sauce)": {"Hotdog Bun": 1, "Classic Sausage": 1, "Packaging Box": 1},
    "Veg Indian Hotdog (Veg Sausage)": {"Hotdog Bun": 1, "Veg Sausage": 1, "Packaging Box": 1},
    "Chili Hotdog (Chili Sauces)": {"Hotdog Bun": 1, "Classic Sausage": 1, "Packaging Box": 1},
    "Coney Onion Hotdog (Smoky Sauces)": {"Hotdog Bun": 1, "Classic Sausage": 1, "Packaging Box": 1},
    "Mexican Street Hotdog (Chicken Bacon)": {"Hotdog Bun": 1, "Bacon/Pepperoni": 1, "Packaging Box": 1},
    "Loaded Hotdog (Veggies/Pepperoni)": {"Hotdog Bun": 1, "Bacon/Pepperoni": 1, "Packaging Box": 1},
    "French Fries (Small)": {"French Fries Portion": 1},
    "French Fries (Medium)": {"French Fries Portion": 2},
    "French Fries (Large)": {"French Fries Portion": 3},
    "Chicken Nuggets (6 Pcs)": {"Chicken Nuggets (Pcs)": 6},
    "Chicken Nuggets (9 Pcs)": {"Chicken Nuggets (Pcs)": 9},
    "Chicken Nuggets (15 Pcs bucket)": {"Chicken Nuggets (Pcs)": 15},
    "Pizza Pockets (3 Pcs snack)": {"Pizza Pockets (Pcs)": 3},
    "Pizza Pockets (5 Pcs party)": {"Pizza Pockets (Pcs)": 5},
    "Cold Drink (Small)": {"Cold Drink Cup": 1},
    "Cold Drink (Medium - Option 1)": {"Cold Drink Cup": 1},
    "Cold Drink (Medium - Option 2)": {"Cold Drink Cup": 1},
    "Party Pack Beverage": {"Cold Drink Cup": 4},
    "(1) Small Meal Add-on": {"French Fries Portion": 1, "Cold Drink Cup": 1},
    "(2) Medium Meal Add-on": {"French Fries Portion": 2, "Cold Drink Cup": 1},
    "(3) Big Meal Add-on": {"French Fries Portion": 3, "Cold Drink Cup": 1}
}

tab1, tab2, tab3 = st.tabs(["🧾 New Bill", "📈 Profit & Loss", "📦 Inventory"])

with tab1:
    st.header("🧾 Create New Bill")
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Name")
        mobile_number = st.text_input("Mobile Number (10 Digits)")
    with col2:
        staff = st.selectbox("Staff/Cashier", ["Manager", "Staff 1", "Staff 2"])
        date_of_bill = st.date_input("Date", datetime.now())
    
    selected_items = st.multiselect("Pick Items", list(RECIPE_MAP.keys()))
    discount = st.number_input("Discount (₹)", min_value=0, value=0, step=1)
    
    price_list = {
        "New York's Hotdog (Classic)": 99, "Cheese Hotdog (Cheese Sausage)": 109,
        "Breakfast Hotdog (Paneer & Egg)": 109, "Chicago's Hotdog (Jalapeno/Onion)": 119,
        "Bdq Hotdog (Smoky Sauce)": 129, "Veg Indian Hotdog (Veg Sausage)": 129,
        "Chili Hotdog (Chili Sauces)": 129, "Coney Onion Hotdog (Smoky Sauces)": 139,
        "Mexican Street Hotdog (Chicken Bacon)": 149, "Loaded Hotdog (Veggies/Pepperoni)": 159,
        "French Fries (Small)": 59, "French Fries (Medium)": 79, "French Fries (Large)": 119,
        "Chicken Nuggets (6 Pcs)": 109, "Chicken Nuggets (9 Pcs)": 149, "Chicken Nuggets (15 Pcs bucket)": 229,
        "Pizza Pockets (3 Pcs snack)": 89, "Pizza Pockets (5 Pcs party)": 139,
        "Cold Drink (Small)": 20, "Cold Drink (Medium - Option 1)": 40, "Cold Drink (Medium - Option 2)": 50,
        "Party Pack Beverage": 70, "(1) Small Meal Add-on": 69, "(2) Medium Meal Add-on": 99, "(3) Big Meal Add-on": 139
    }
    
    total_amount = sum([price_list[item] for item in selected_items])
    final_amount = total_amount - discount
    
    if total_amount > 0:
        st.metric(label="Total Amount", value=f"₹ {total_amount}")
        st.metric(label="Final Amount", value=f"₹ {final_amount}")
    
    if st.button("Complete & Save Transaction", type="primary"):
        if not customer_name:
            st.warning("Customer Name भरें!")
        elif not selected_items:
            st.warning("Items चुनें!")
        elif client is None:
             st.error("Sheet Connection Error!")
        else:
            try:
                sheet = client.open(SHEET_NAME).sheet1 
                if len(sheet.get_all_values()) == 0:
                    sheet.append_row(["Date", "Time", "Customer Name", "Mobile", "Staff", "Items", "Total Amount", "Discount", "Final Amount"])
                
                time_str = datetime.now().strftime("%H:%M:%S")
                date_str = date_of_bill.strftime("%Y-%m-%d")
                items_str = ", ".join(selected_items)
                
                row_data = [date_str, time_str, customer_name, mobile_number, staff, items_str, total_amount, discount, final_amount]
                sheet.append_row(row_data)
                
                st.success("✅ बिल सेव हो गया!")
                st.balloons()
                
                # Inventory Auto-Deduct
                try:
                    inv_sheet = client.open(SHEET_NAME).worksheet("Inventory")
                    if len(inv_sheet.get_all_values()) == 0:
                        inv_sheet.append_row(["Date", "Time", "Item Name", "Quantity", "Action", "Reference"])
                    
                    used_materials = {}
                    for item in selected_items:
                        for raw_item, qty in RECIPE_MAP[item].items():
                            used_materials[raw_item] = used_materials.get(raw_item, 0) + qty
                    
                    for raw_item, total_qty in used_materials.items():
                        inv_sheet.append_row([date_str, time_str, raw_item, total_qty, "Stock Used 🔴 (Auto)", f"Bill: {customer_name}"])
                except:
                    st.warning("Inventory update failed.")
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.header("📈 Sales Dashboard")
    if st.button("Load Data"):
        try:
            sheet = client.open(SHEET_NAME).sheet1
            df = pd.DataFrame(sheet.get_all_records())
            st.dataframe(df, use_container_width=True)
            total = df["Final Amount"].sum()
            st.metric("Total Sales", f"₹ {total:,.2f}")
        except Exception as e:
            st.error(f"Error: {e}")

with tab3:
    st.header("📦 Inventory Management")
    inv_item = st.selectbox("Select Item", RAW_MATERIALS)
    inv_qty = st.number_input("Quantity", min_value=1, value=1)
    inv_action = st.selectbox("Action", ["Stock Added 🟢", "Stock Removed 🔴"])
    
    if st.button("Update Manually"):
        try:
            inv_sheet = client.open(SHEET_NAME).worksheet("Inventory")
            inv_sheet.append_row([datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), inv_item, inv_qty, inv_action, "Manual"])
            st.success("Updated!")
        except Exception as e:
            st.error(f"Error: {e}")
