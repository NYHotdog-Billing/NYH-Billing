import streamlit as st
import pandas as pd
from datetime import datetime

# पेज की सेटिंग
st.set_page_config(page_title="New York's Hotdog POS", page_icon="🌭")

st.title("🌭 New York's Hotdog - Ultimate Billing System")

# --- 1. इन्वेंटरी (स्टॉक) का सेटअप ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        "Hotdog Buns": 100,
        "Normal Sausages": 50,
        "Veg Sausages": 30,
        "Cheese Sausages": 20,
        "Chicken Sausages": 40,
        "Fries (kg)": 10.0,
        "Chicken Nuggets (Pcs)": 200,
        "Pizza Pockets (Pcs)": 100,
        "Coke Syrup (Liters)": 5.0,
        "Sauces/Toppings (Units)": 200
    }

if 'sales_history' not in st.session_state:
    st.session_state.sales_history = []

# --- 2. आपका असली मेन्यू और उसकी इन्वेंटरी खपत ---
MENU_DATABASE = {
    # हॉटडॉग्स
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

    # साइड्स और स्नैक्स
    "Small Fries": [59, 20, {"Fries (kg)": 0.1}],
    "Medium Fries": [79, 30, {"Fries (kg)": 0.15}],
    "Large Fries": [119, 45, {"Fries (kg)": 0.2}],
    "Chicken Nuggets (6 Pcs)": [109, 50, {"Chicken Nuggets (Pcs)": 6}],
    "Chicken Nuggets (9 Pcs)": [149, 70, {"Chicken Nuggets (Pcs)": 9}],
    "Chicken Nuggets Bucket (15 Pcs)": [229, 110, {"Chicken Nuggets (Pcs)": 15}],
    "Pizza Pockets (3 Pcs)": [89, 40, {"Pizza Pockets (Pcs)": 3}],
    "Pizza Pockets (5 Pcs)": [139, 65, {"Pizza Pockets (Pcs)": 5}],

    # बेवरेजेस (कोल्ड ड्रिंक्स)
    "Cold Drink (Small)": [20, 10, {"Coke Syrup (Liters)": 0.03}],
    "Cold Drink (Medium)": [40, 15, {"Coke Syrup (Liters)": 0.05}],
    "Cold Drink (Large)": [50, 20, {"Coke Syrup (Liters)": 0.08}], 
    "Party Pack": [70, 30, {"Coke Syrup (Liters)": 0.15}],

    # मील्स (ऐड-ऑन)
    "Small Meal (Add-on)": [69, 30, {"Fries (kg)": 0.1, "Coke Syrup (Liters)": 0.03}],
    "Medium Meal (Add-on)": [99, 45, {"Fries (kg)": 0.15, "Coke Syrup (Liters)": 0.05}],
    "Big Meal (Add-on)": [139, 65, {"Fries (kg)": 0.2, "Coke Syrup (Liters)": 0.08}]
}

# --- सेक्शन 1: नया बिल बनाना ---
st.header("🧾 New Bill")
cust_name = st.text_input("Customer Name", "Guest")
mobile_no = st.text_input("Mobile No.")

# आइटम चुनने का ऑप्शन
selected_items = st.multiselect("Select Items", list(MENU_DATABASE.keys()))
discount = st.number_input("Flat Discount (₹)", min_value=0, value=0)

if st.button("Complete Transaction & Print"):
    if not selected_items:
        st.warning("Please select at least one item!")
    else:
        total_amount = 0
        total_cost = 0
        
        can_make = True
        short_items = []
        
        temp_inventory = st.session_state.inventory.copy()
        
        for item in selected_items:
            sell_price, cost_price, ingredients = MENU_DATABASE[item]
            total_amount += sell_price
            total_cost += cost_price
            
            for ing, qty in ingredients.items():
                if temp_inventory.get(ing, 0) >= qty:
                    temp_inventory[ing] -= qty
                else:
                    can_make = False
                    short_items.append(ing)
                    
        if not can_make:
            st.error(f"Not enough stock! Running low on: {', '.join(set(short_items))}")
        else:
            # बिल और इन्वेंटरी अपडेट करना
            st.session_state.inventory = temp_inventory
            grand_total = total_amount - discount
            
            # सेल रिकॉर्ड करना
            st.session_state.sales_history.append({
                "Time": datetime.now().strftime("%H:%M"),
                "Customer": cust_name,
                "Total Amount": total_amount,
                "Discount": discount,
                "Final Paid": grand_total,
                "Profit": grand_total - total_cost
            })
            
            st.success(f"Bill Generated Successfully! Total Paid: ₹{grand_total}")
            st.info(f"Customer: {cust_name} | Items: {', '.join(selected_items)}")

st.markdown("---")

# --- सेक्शन 2: लाइव इन्वेंटरी (स्टॉक) ट्रैकिंग ---
st.header("📦 Inventory Status")
inv_df = pd.DataFrame(list(st.session_state.inventory.items()), columns=["Item", "Stock Remaining"])
st.dataframe(inv_df, use_container_width=True)

st.markdown("---")

# --- सेक्शन 3: प्रॉफिट और सेल रिपोर्ट ---
st.header("📊 Daily Report (P&L)")
if st.session_state.sales_history:
    report_df = pd.DataFrame(st.session_state.sales_history)
    st.dataframe(report_df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    col1.metric("Total Sales (₹)", f"₹{report_df['Final Paid'].sum()}")
    col2.metric("Estimated Profit (₹)", f"₹{report_df['Profit'].sum()}")
else:
    st.info("No sales recorded yet.")
