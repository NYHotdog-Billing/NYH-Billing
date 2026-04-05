import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- पेज की सेटिंग ---
st.set_page_config(page_title="New York's Hotdog", page_icon="🌭", layout="wide")

# --- 1. गूगल शीट से कनेक्शन ---
@st.cache_resource
def init_connection():
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets", 
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"प्रमाणीकरण (Authentication) एरर: {e}. कृपया Secrets चेक करें।")
        return None

client = init_connection()

# ध्यान दें: "NYH_Billing" की जगह अपनी गूगल शीट का असली नाम लिखें
SHEET_NAME = "NYH_Billing" 

st.title("🌭 New York's Hotdog - Billing System")

# --- टैब्स बनाना ---
tab1, tab2 = st.tabs(["🧾 New Bill", "📈 Profit & Loss"])

# --- TAB 1: New Bill ---
with tab1:
    st.header("🧾 Create New Bill")
    
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Name")
        mobile_number = st.text_input("Mobile Number (10 Digits)")
    with col2:
        staff = st.selectbox("Staff/Cashier", ["Manager", "Staff 1", "Staff 2"])
        date_of_bill = st.date_input("Date", datetime.now())
    
    st.markdown("---")
    st.subheader("Select Items from Menu")

    # --- आपका असली मेन्यू (मेन्यू कार्ड फोटो के अनुसार) ---
    menu = {
        # --- HOTDOGS --- (image_15.png)
        "New York's Hotdog (Classic)": 99,
        "Cheese Hotdog (Cheese Sausage)": 109,
        "Breakfast Hotdog (Paneer & Egg)": 109,
        "Chicago's Hotdog (Jalapeno/Onion)": 119,
        "Bdq Hotdog (Smoky Sauce)": 129,
        "Veg Indian Hotdog (Veg Sausage)": 129,
        "Chili Hotdog (Chili Sauces)": 129,
        "Coney Onion Hotdog (Smoky Sauces)": 139,
        "Mexican Street Hotdog (Chicken Bacon)": 149,
        "Loaded Hotdog (Veggies/Pepperoni)": 159,
        # --- SIDES & NUGGETS --- (image_16.png)
        "French Fries (Small)": 59,
        "French Fries (Medium)": 79,
        "French Fries (Large)": 119,
        "Chicken Nuggets (6 Pcs)": 109,
        "Chicken Nuggets (9 Pcs)": 149,
        "Chicken Nuggets (15 Pcs bucket)": 229,
        "Pizza Pockets (3 Pcs snack)": 89,
        "Pizza Pockets (5 Pcs party)": 139,
        # --- BEVERAGES & MEALS --- (image_16.png)
        "Cold Drink (Small)": 20,
        "Cold Drink (Medium - Option 1)": 40,
        "Cold Drink (Medium - Option 2)": 50,
        "Party Pack Beverage": 70,
        "(1) Small Meal Add-on": 69,
        "(2) Medium Meal Add-on": 99,
        "(3) Big Meal Add-on": 139
    }
    
    # मेन्यू को कैटेगरी के अनुसार दिखाने के लिए multiselect
    selected_items = st.multiselect("Pick Items", list(menu.keys()))
    
    discount = st.number_input("Discount (₹)", min_value=0, value=0, step=1)
    
    # कैलकुलेशन
    total_amount = sum([menu[item] for item in selected_items])
    final_amount = total_amount - discount
    
    st.markdown("---")
    if total_amount > 0:
        st.metric(label="Total Amount", value=f"₹ {total_amount}")
        st.metric(label="Final Amount (After Discount)", value=f"₹ {final_amount}")
    
    if st.button("Complete & Save Transaction", type="primary"):
        if not customer_name:
            st.warning("कृपया Customer Name भरें!")
        elif not mobile_number:
            st.warning("कृपया Mobile Number भरें!")
        elif not selected_items:
            st.warning("कृपया कम से कम 1 Item चुनें!")
        elif client is None:
             st.error("गूगल शीट से कनेक्शन नहीं है। कृपया Secrets चेक करें।")
        else:
            try:
                # शीट खोलें
                sheet = client.open(SHEET_NAME).sheet1 
                
                # समय और तारीख
                time_str = datetime.now().strftime("%H:%M:%S")
                date_str = date_of_bill.strftime("%Y-%m-%d")
                
                # आइटम को एक लाइन में जोड़ना
                items_str = ", ".join(selected_items)
                
                # डेटा को शीट में भेजना (नया क्रम: Mobile Number के साथ)
                # क्रम: तारीख, समय, ग्राहक का नाम, मोबाइल नंबर, स्टाफ, आइटम्स, टोटल, डिस्काउंट, फाइनल
                row_data = [date_str, time_str, customer_name, mobile_number, staff, items_str, total_amount, discount, final_amount]
                sheet.append_row(row_data)
                
                st.success(f"✅ बिल ₹{final_amount} ग्राहक '{customer_name}' के लिए सफलतापूर्वक सेव हो गया!")
                # फॉर्म साफ़ करने के लिए (Streamlit automatic refresh)
                st.balloons()
            except Exception as e:
                st.error(f"गूगल शीट में डेटा सेव करने में एरर: {e}")

# --- TAB 2: Profit & Loss ---
with tab2:
    st.header("📈 Profit & Loss / Sales Dashboard")
    st.write("यहाँ आप अपने कैफे की पूरी सेल का डेटा देख सकते हैं।")
    
    if st.button("Load/Refresh Sales Data"):
        if client is None:
             st.error("गूगल शीट से कनेक्शन नहीं है।")
        else:
            try:
                sheet = client.open(SHEET_NAME).sheet1
                data = sheet.get_all_records()
                
                if data:
                    df = pd.DataFrame(data)
                    # डेटा दिखाना
                    st.dataframe(df, use_container_width=True)
                    
                    # 'Final Amount' (आखरी कॉलम) का टोटल निकालना
                    # ध्यान दें: अगर आपकी शीट में हेडर अलग है तो इसे बदलें, वरना यह आखरी कॉलम का टोटल करेगा।
                    total_sales = df.iloc[:, -1].sum() 
                    st.metric(label="Overall Total Sales", value=f"₹ {total_sales:,.2f}")
                else:
                    st.info("अभी शीट में कोई डेटा नहीं है। एक नया बिल काटें!")
            except Exception as e:
                st.error(f"डेटा लोड करने में एरर: {e}. क्या SHEET_NAME सही है?")
