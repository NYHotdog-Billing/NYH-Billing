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
        
        credentials_dict = {
          "type": "service_account",
          "project_id": "hotdog-billing-492413",
          "private_key_id": "417ab2c8f943b22966b94bc7d64472a7bd9603d3",
          "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDJeuWd17ZaG27/\nPSIqojgr9mBznbkZP9CzHN56A762LaJAZ0jdNJEBRFi16A2ByzkB0psrYNWVfm2/\nfXhqONwk+57gFJSVCouGs5S8w7Lo0Qg4KEwPaM2bdrao2MAWju86Hte4VA9ozGEd\nJJzid+jZMsqeJ37j0aBDm+3c4945BCZbd7NET8YmZN1cPSlRHepToIrTf/b9g+Ey\nUiGtEawLwo+5wFriftBAFIYHoV9cdb8K6vy8bvvWBpwcmxprCTZsab0UdvjHK6oL\nnawHJ9064phF61H4PZs9z0hX7T1GRLVFnlCwKFwmBzK7dIlfLB8qyNlIUVputN3K\nvYNevoWtAgMBAAECggEAIxkCE+eGcBb0VIk5QPUGVP4z2iAhJPldaT4/sUCiwcic\nSZzUcBhepDpcO8ADTldxBFTETB+vxT2Db8azKcni65xblkxvf7EZEiuJXwK2UWFM\njb/TVCHdI1ZgRnSPrb5ThSvnR0h5cLeduT5uB/N8gA2dh0R5EcWsJertWjvls8eq\nninQJ1TMsxc9yoj3PKadLt2rUdrEDod5lQk6UrHGStdecENprkzo/HDpXZXq+CYL\nH9Nob0nqG4sL8Ql7iZoUzrGsnLQ0O9aEAPQxZFkrewhhXZP0oA/X3N9F3alYwmm0\nnnN7IxkxUtH5lAQnMATqSm724fyEwQe8scX68thiQQKBgQDqibWMGdMFa63HMvKl\n9zyDl9ZAdj0AXpVk2nnLccCZ04e5GkmovO4E6iNY7DB0CiNGwmh4yY6SGHjcEmOM\nbTGR8B706WTP5B8pHWJ11O2eeeqamPxdkh+HOGVI+LkXCf5WkHLyxX/G2Q0UBfsL\nir55STlC8SCNt9qOVr8O2j34YQKBgQDb6sYJURoZYkQq9tq8c00ShZhwP6NR5qoL\nz0RD5BBeMEEtkVntc934XaWc2w5sBVSD+AqtarwOLJ1hOw64LgoWLbsse7upaEYI\n/4m4cXjd+tYOEXOb0FEYAfrtfY+ENREDF5ttYECM3n0k0c09SmLD+iGrpOnP5bfu\nCH2rwyKgzQKBgQDW7ErJkACoPvyIRk/FdsKldEaJ29AavpH4UZy6qgrs68K8BTLq\nxfb32fd6TTY5n/CjrxM9XLahenuGb/N5g7ahHYHAvP/84fcMHjlT8UOurdomwXrB\n5F2v9CYcsJAsZKQFf2lWv1VQSyaI6tIayZGyYz9t8Lj8JTbKqQN8ANI5AQKBgQCm\nqPs/oEjJJ+FFNiJ6Yl7sRHZLys54iPghTwgK81E8MBGU+OxPuVlkmYOipZf+YOO1\nx0pANf0iOMlkIB99kNZwDGQmx/Zl4fIBa7bxIn1YrHl/29XjJTHvocCKLneO17B2\nyXMupp0EpK/uMVj6s965alwN+kJ/HTYQnDqw6obZmQKBgQDj8cehbi+g6oFD8Dbj\nUNS+Oz+CrXxPha7baPYmvA7r1q5sg7J5xslSdAyEHimnVi3j0/0h4tSPYyN91x30\nd1o+hinqiz1Cqzx1BVSE4XXnJE4vzrbC7o8eOJfeWrJnxgdL1ZaSIZhEzMpG8Ffo\n1VQOZkZi93FUcJr9RZNpZk3Lbg==\n-----END PRIVATE KEY-----\n",
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

# --- तीन टैब्स बना दिए गए हैं ---
tab1, tab2, tab3 = st.tabs(["🧾 New Bill", "📈 Profit & Loss", "📦 Inventory"])

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

    menu = {
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
        "French Fries (Small)": 59,
        "French Fries (Medium)": 79,
        "French Fries (Large)": 119,
        "Chicken Nuggets (6 Pcs)": 109,
        "Chicken Nuggets (9 Pcs)": 149,
        "Chicken Nuggets (15 Pcs bucket)": 229,
        "Pizza Pockets (3 Pcs snack)": 89,
        "Pizza Pockets (5 Pcs party)": 139,
        "Cold Drink (Small)": 20,
        "Cold Drink (Medium - Option 1)": 40,
        "Cold Drink (Medium - Option 2)": 50,
        "Party Pack Beverage": 70,
        "(1) Small Meal Add-on": 69,
        "(2) Medium Meal Add-on": 99,
        "(3) Big Meal Add-on": 139
    }
    
    selected_items = st.multiselect("Pick Items", list(menu.keys()))
    discount = st.number_input("Discount (₹)", min_value=0, value=0, step=1)
    
    total_amount = sum([menu[item] for item in selected_items])
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
                # अगर शीट खाली है तो हेडिंग डालें
                if len(sheet.get_all_values()) == 0:
                    sheet.append_row(["Date", "Time", "Customer Name", "Mobile", "Staff", "Items", "Total Amount", "Discount", "Final Amount"])
                
                time_str = datetime.now().strftime("%H:%M:%S")
                date_str = date_of_bill.strftime("%Y-%m-%d")
                items_str = ", ".join(selected_items)
                
                row_data = [date_str, time_str, customer_name, mobile_number, staff, items_str, total_amount, discount, final_amount]
                sheet.append_row(row_data)
                
                st.success(f"✅ बिल ₹{final_amount} ग्राहक '{customer_name}' के लिए सफलतापूर्वक सेव हो गया!")
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
                    st.dataframe(df, use_container_width=True)
                    total_sales = df["Final Amount"].sum() if "Final Amount" in df.columns else df.iloc[:, -1].sum()
                    st.metric(label="Overall Total Sales", value=f"₹ {total_sales:,.2f}")
                else:
                    st.info("अभी शीट में कोई डेटा नहीं है। एक नया बिल काटें!")
            except Exception as e:
                st.error(f"डेटा लोड करने में एरर: {e}")

# --- TAB 3: Inventory (नया टैब) ---
with tab3:
    st.header("📦 Inventory Management")
    st.write("यहाँ आप अपने कैफे के कच्चे माल (Raw Materials) का स्टॉक अपडेट कर सकते हैं।")
    
    inv_col1, inv_col2 = st.columns(2)
    with inv_col1:
        inv_item = st.text_input("Item Name (जैसे: Buns, Sausages, Coke)")
    with inv_col2:
        inv_qty = st.number_input("Quantity (मात्रा)", min_value=1, value=1)
        
    inv_action = st.selectbox("Action", ["Stock Added 🟢 (स्टॉक आया)", "Stock Used 🔴 (स्टॉक खत्म/इस्तेमाल हुआ)"])
    
    if st.button("Update Inventory", type="primary"):
        if not inv_item:
            st.warning("कृपया Item Name भरें!")
        elif client is None:
            st.error("गूगल शीट से कनेक्शन नहीं है।")
        else:
            try:
                # Inventory टैब ढूँढना
                inv_sheet = client.open(SHEET_NAME).worksheet("Inventory")
                
                # अगर पन्ना खाली है तो पहली बार में हेडिंग बना देगा
                if len(inv_sheet.get_all_values()) == 0:
                    inv_sheet.append_row(["Date", "Time", "Item Name", "Quantity", "Action"])
                
                date_str = datetime.now().strftime("%Y-%m-%d")
                time_str = datetime.now().strftime("%H:%M:%S")
                
                row_data = [date_str, time_str, inv_item, inv_qty, inv_action]
                inv_sheet.append_row(row_data)
                
                st.success(f"✅ {inv_item} का स्टॉक सफलतापूर्वक अपडेट हो गया!")
            except Exception as e:
                st.error(f"एरर: क्या आपने अपनी गूगल शीट में 'Inventory' नाम का नया पन्ना (Tab) बनाया है? (Error details: {e})")
                
    st.markdown("---")
    if st.button("Load/Refresh Inventory Data"):
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
                    st.info("अभी इन्वेंटरी में कोई डेटा नहीं है।")
            except Exception as e:
                st.error("एरर: कृपया सुनिश्चित करें कि गूगल शीट में 'Inventory' नाम का पन्ना मौजूद है।")
