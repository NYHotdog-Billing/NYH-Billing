import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- पेज की सेटिंग ---
st.set_page_config(page_title="New York's Hotdog", page_icon="🌭", layout="wide")

# --- 1. गूगल शीट से कनेक्शन (असली ब्रह्मास्त्र टोटका) ---
@st.cache_resource
def init_connection():
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets", 
            "https://www.googleapis.com/auth/drive"
        ]
        
        # यह है कोडिंग का सबसे पक्का तरीका! हर लाइन अलग से लॉक है।
        my_private_key = (
            "-----BEGIN PRIVATE KEY-----\n"
            "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDGSHdXOKUK30bH\n"
            "3HYUyaFj4ujl5tjZ2mhGuKzNXC/AHw9wNqaYb+Jbdg4GUnMpBNZM33z0Y9rgO/QP\n"
            "N3JYgBEx+UqfZjln9tGmrNPo062e3ci8Zc44rmqSMLNVIWHIfxFzfgExdKNqa7zz\n"
            "T1lprG+l1vzbnpGXHpupzIB/VvExu3cXK7TERIO0xB19KV+DJqSPNBnGOml6q3wh\n"
            "mNxXYWsRVVFRk5OuErFwdcjHkHENNDqM5ZmqcUlipQZcyY6RCwnu2jJymhKLIPvd\n"
            "NKcd4HX1X6B3V34H8YEgZF7eDqc7QgEr/+L6R2iwpAwYJ0DkZpobJlIp/TKt1O0D\n"
            "3YVe6rB5AgMBAAECggEALsSDX391EBwrO/NAJ7WKGz73O1ioX7P/4eRnn7Vlbt10\n"
            "P1K7IwBOhzdgHi8gFmLeUzCUntl8fs6HMexcPXd+GlKBFBObHrfJr6/abxZyG2b\n"
            "zfH+QsjCyrHxbnwl7e4ordKz0dgmvjBkvAfEeWQKXnWXpO5g/SGjShi52y8kyxt3\n"
            "1xu7/v998eu7FNhdgG8EjfSKyXhNOzyEjMe45p7+4JTrjr9T7MmgWsTgdNZn3Lpo\n"
            "h4Vx6Glx1R84SKnaLHMTE+3GXzZ7xmR6Ev90mHR0eHKaLiNPdw5s/zrbjLZ9kI6a\n"
            "2svyIMEzV4kJZlprUlNZG2L0nlMzcndAkIZZoQ9wPQKBgQDk5vCHNkSjb0K+lf6k\n"
            "mpliXFgZ5mDEtvMD/E5NXwepXiJ0bGjzD2aZm5Ld3EpUJokxLdCgN2UsB85C0Q7Z\n"
            "4HHIq+j8AXEtvUc4QZP1DTOt0DzscK9uNEoAgdy8rgsXSd+f+1VcEALBKfDUtAD+\n"
            "4NYD/eXAKte177lllWsoSdI+5QKBgQDdwZekVijES/x2W0yxCG6SHIRA/j4mkBhQ\n"
            "HLU/US/ee3HCoV/1y/IdrfBQ7cTFK20Qb5s6wtq5k4K+9dS8C9wM24DCwwIIbwAE\n"
            "XOfSDxFReQV2UaEogEpyqN/vAX8s1ud2ni075LPJhtWl+P8zCMqMPWenoiqJwLu7\n"
            "5rdSewQ+BQKBgD0RD2JDLBSd/iRyR7kKNZl0IVznhTF1zWdmzEz/6T9aCb8dnPIb\n"
            "Tbf1NT1TI9FHZppkKqBTpv4UJwbUVy3xHun2UvXIPLWDJZjwhdR+bScVwushNOwl\n"
            "rwhrnMQJepP/9VTs7FzfOJzn34QfcZSNzwrJlZ2q0FmNVtyu/COHbjuxAoGALPgX\n"
            "MkIuni/ykGXPVY8qLQMPZsan/9X0uDo6Hw7tsCZEWX20IforrQ0a0K6G2p0FzvFy\n"
            "/yWIiV16hBMCAug8xXa108kL3n3z+O6GLDjWADmUe/vtvHLXpgzM7IDXM1aZNZq5\n"
            "/Y1RUCrBpJir18OOn4XMQVhHXAvzhhUxU86Se6kCgYBwjpGwnyKWbd2l5V+ClIPq\n"
            "XkcXImoSo6dNuVdFzmo7RJPpbTuZNJ04ZNS7en6Ldc45D98rzci6gmQC8av3ztHh\n"
            "R6LatdVMfWfS+WGemaUWGpSHe97Vmf6A6O0Wd9xmidF70PQKUXPdppLrt4N4pTHl\n"
            "EihXF7HxqsEWO/1qwKs1EA==\n"
            "-----END PRIVATE KEY-----\n"
        )
        
        credentials_dict = {
          "type": "service_account",
          "project_id": "hotdog-billing-492413",
          "private_key_id": "ba0b5204f4a3b792371528594bea6feed35c083a",
          "private_key": my_private_key,
          "client_email": "hotdog-app@hotdog-billing-492413.iam.gserviceaccount.com",
          "client_id": "101024134007123863664",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/hotdog-app%40hotdog-billing-492413.iam.gserviceaccount.com",
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

tab1, tab2 = st.tabs(["🧾 New Bill", "📈 Profit & Loss"])

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
        elif not mobile_number:
            st.warning("कृपया Mobile Number भरें!")
        elif not selected_items:
            st.warning("कृपया कम से कम 1 Item चुनें!")
        elif client is None:
             st.error("गूगल शीट से कनेक्शन नहीं है।")
        else:
            try:
                sheet = client.open(SHEET_NAME).sheet1 
                time_str = datetime.now().strftime("%H:%M:%S")
                date_str = date_of_bill.strftime("%Y-%m-%d")
                items_str = ", ".join(selected_items)
                
                row_data = [date_str, time_str, customer_name, mobile_number, staff, items_str, total_amount, discount, final_amount]
                sheet.append_row(row_data)
                
                st.success(f"✅ बिल ₹{final_amount} ग्राहक '{customer_name}' के लिए सफलतापूर्वक सेव हो गया!")
                st.balloons()
            except Exception as e:
                st.error(f"गूगल शीट में डेटा सेव करने में एरर: {e}")

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
                    
                    total_sales = df.iloc[:, -1].sum() 
                    st.metric(label="Overall Total Sales", value=f"₹ {total_sales:,.2f}")
                else:
                    st.info("अभी शीट में कोई डेटा नहीं है। एक नया बिल काटें!")
            except Exception as e:
                st.error(f"डेटा लोड करने में एरर: {e}. क्या SHEET_NAME सही है?")
