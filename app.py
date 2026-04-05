import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- पेज की सेटिंग ---
st.set_page_config(page_title="New York's Hotdog", page_icon="🌭", layout="wide")

# --- 1. गूगल शीट से कनेक्शन (अभेद्य लाइन-बाय-लाइन लॉक) ---
@st.cache_resource
def init_connection():
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets", 
            "https://www.googleapis.com/auth/drive"
        ]
        
        # यह है मोबाइल के \n एरर को मात देने का सबसे पक्का तरीका
        my_private_key = (
            "-----BEGIN PRIVATE KEY-----\n"
            "MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDJeuWd17ZaG27/\n"
            "PSIqojgr9mBznbkZP9CzHN56A762LaJAZ0jdNJEBRFi16A2ByzkB0psrYNWVfm2/\n"
            "fXhqONwk+57gFJSVCouGs5S8w7Lo0Qg4KEwPaM2bdrao2MAWju86Hte4VA9ozGEd\n"
            "JJzid+jZMsqeJ37j0aBDm+3c4945BCZbd7NET8YmZN1cPSlRHepToIrTf/b9g+Ey\n"
            "UiGtEawLwo+5wFriftBAFIYHoV9cdb8K6vy8bvvWBpwcmxprCTZsab0UdvjHK6oL\n"
            "nawHJ9064phF61H4PZs9z0hX7T1GRLVFnlCwKFwmBzK7dIlfLB8qyNlIUVputN3K\n"
            "vYNevoWtAgMBAAECggEAIxkCE+eGcBb0VIk5QPUGVP4z2iAhJPldaT4/sUCiwcic\n"
            "SZzUcBhepDpcO8ADTldxBFTETB+vxT2Db8azKcni65xblkxvf7EZEiuJXwK2UWFM\n"
            "jb/TVCHdI1ZgRnSPrb5ThSvnR0h5cLeduT5uB/N8gA2dh0R5EcWsJertWjvls8eq\n"
            "ninQJ1TMsxc9yoj3PKadLt2rUdrEDod5lQk6UrHGStdecENprkzo/HDpXZXq+CYL\n"
            "H9Nob0nqG4sL8Ql7iZoUzrGsnLQ0O9aEAPQxZFkrewhhXZP0oA/X3N9F3alYwmm0\n"
            "nnN7IxkxUtH5lAQnMATqSm724fyEwQe8scX68thiQQKBgQDqibWMGdMFa63HMvKl\n"
            "9zyDl9ZAdj0AXpVk2nnLccCZ04e5GkmovO4E6iNY7DB0CiNGwmh4yY6SGHjcEmOM\n"
            "bTGR8B706WTP5B8pHWJ11O2eeeqamPxdkh+HOGVI+LkXCf5WkHLyxX/G2Q0UBfsL\n"
            "ir55STlC8SCNt9qOVr8O2j34YQKBgQDb6sYJURoZYkQq9tq8c00ShZhwP6NR5qoL\n"
            "z0RD5BBeMEEtkVntc934XaWc2w5sBVSD+AqtarwOLJ1hOw64LgoWLbsse7upaEYI\n"
            "/4m4cXjd+tYOEXOb0FEYAfrtfY+ENREDF5ttYECM3n0k0c09SmLD+iGrpOnP5bfu\n"
            "CH2rwyKgzQKBgQDW7ErJkACoPvyIRk/FdsKldEaJ29AavpH4UZy6qgrs68K8BTLq\n"
            "xfb32fd6TTY5n/CjrxM9XLahenuGb/N5g7ahHYHAvP/84fcMHjlT8UOurdomwXrB\n"
            "5F2v9CYcsJAsZKQFf2lWv1VQSyaI6tIayZGyYz9t8Lj8JTbKqQN8ANI5AQKBgQCm\n"
            "qPs/oEjJJ+FFNiJ6Yl7sRHZLys54iPghTwgK81E8MBGU+OxPuVlkmYOipZf+YOO1\n"
            "x0pANf0iOMlkIB99kNZwDGQmx/Zl4fIBa7bxIn1YrHl/29XjJTHvocCKLneO17B2\n"
            "yXMupp0EpK/uMVj6s965alwN+kJ/HTYQnDqw6obZmQKBgQDj8cehbi+g6oFD8Dbj\n"
            "UNS+Oz+CrXxPha7baPYmvA7r1q5sg7J5xslSdAyEHimnVi3j0/0h4tSPYyN91x30\n"
            "d1o+hinqiz1Cqzx1BVSE4XXnJE4vzrbC7o8eOJfeWrJnxgdL1ZaSIZhEzMpG8Ffo\n"
            "1VQOZkZi93FUcJr9RZNpZk3Lbg==\n"
            "-----END PRIVATE KEY-----\n"
        )
        
        credentials_dict = {
          "type": "service_account",
          "project_id": "hotdog-billing-492413",
          "private_key_id": "417ab2c8f943b22966b94bc7d64472a7bd9603d3",
          "private_key": my_private_key,
          "client_email": "hotdog-app-new@hotdog-billing-492413.iam.gserviceaccount.com",
          "client_id": "107807598057562047821",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/hotdog-app-new%40hotdog-billing-492413.iam.gserviceaccount.com",
          "universe_domain": "googleapis.com"
        }
        
        creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"एरर: {e}")
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
    
    st.markdown("---")
    st.subheader("Select Items from Menu")
    
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
    
    st.markdown("---")
    if total_amount > 0:
        st.metric(label="Total Amount", value=f"₹ {total_amount}")
        st.metric(label="Final Amount (After Discount)", value=f"₹ {final_amount}")
    
    if st.button("Complete & Save Transaction", type="primary"):
        if not customer_name:
            st.warning("कृपया Customer Name भरें!")
        elif not selected_items:
            st.warning("कृपया कम से कम 1 Item चुनें!")
        elif client is None:
             st.error("गूगल शीट से कनेक्शन नहीं है।")
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
                
                st.success(f"✅ बिल ₹{final_amount} ग्राहक '{customer_name}' के लिए सफलतापूर्वक सेव हो गया!")
                st.balloons()
                
                try:
                    inv_sheet = client.open(SHEET_NAME).worksheet("Inventory")
                    if len(inv_sheet.get_all_values()) == 0:
                        inv_sheet.append_row(["Date", "Time", "Item Name", "Quantity", "Action", "Reference"])
                    
                    used_materials = {}
                    for item in selected_items:
                        for raw_item, qty in RECIPE_MAP[item].items():
                            used_materials[raw_item] = used_materials.get(raw_item, 0) + qty
                    
                    for raw_item, total_qty in used_materials.items():
                        inv_row = [date_str, time_str, raw_item, total_qty, "Stock Used 🔴 (Auto)", f"Bill: {customer_name}"]
                        inv_sheet.append_row(inv_row)
                        
                except Exception as e:
                    st.warning("बिल कट गया, लेकिन इन्वेंटरी अपडेट नहीं हुई।")
                    
            except Exception as e:
                st.error(f"गूगल शीट में डेटा सेव करने में एरर: {e}")

with tab2:
    st.header("📈 Profit & Loss / Sales Dashboard")
    
    if st.button("Load/Refresh Sales Data"):
        if client is None:
             st.error("गूगल शीट से कनेक्शन नहीं है।")
        else:
            try:
                sheet = client.open(SHEET_NAME).sheet1
                data = sheet.get_all_records()
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    total_sales = df["Final Amount"].sum() if "Final Amount" in df.columns else df.iloc[:, -1].sum()
                    st.metric(label="Overall Total Sales", value=f"₹ {total_sales:,.2f}")
                else:
                    st.info("अभी कोई डेटा नहीं है।")
            except Exception as e:
                st.error(f"एरर: {e}")

with tab3:
    st.header("📦 Inventory Management")
    
    inv_col1, inv_col2 = st.columns(2)
    with inv_col1:
        inv_item = st.selectbox("Select Item (कच्चा माल)", RAW_MATERIALS)
    with inv_col2:
        inv_qty = st.number_input("Quantity (मात्रा)", min_value=1, value=1)
        
    inv_action = st.selectbox("Action", ["Stock Added 🟢", "Stock Removed 🔴"])
    
    if st.button("Update Inventory Manually", type="primary"):
        if client is None:
            st.error("गूगल शीट से कनेक्शन नहीं है।")
        else:
            try:
                inv_sheet = client.open(SHEET_NAME).worksheet("Inventory")
                if len(inv_sheet.get_all_values()) == 0:
                    inv_sheet.append_row(["Date", "Time", "Item Name", "Quantity", "Action", "Reference"])
                
                date_str = datetime.now().strftime("%Y-%m-%d")
                time_str = datetime.now().strftime("%H:%M:%S")
                row_data = [date_str, time_str, inv_item, inv_qty, inv_action, "Manual Entry"]
                inv_sheet.append_row(row_data)
                
                st.success(f"✅ अपडेट हो गया!")
            except Exception as e:
                st.error(f"एरर: {e}")
                
    st.markdown("---")
    if st.button("Load/Refresh Inventory"):
        if client is None:
             st.error("गूगल शीट से कनेक्शन नहीं है।")
        else:
            try:
                inv_sheet = client.open(SHEET_NAME).worksheet("Inventory")
                data = inv_sheet.get_all_records()
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("इन्वेंटरी खाली है।")
            except Exception as e:
                st.error("एरर: इन्वेंटरी लोड नहीं हुई।")
