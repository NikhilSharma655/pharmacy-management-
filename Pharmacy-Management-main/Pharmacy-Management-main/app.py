import sqlite3
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta


def create_tables():
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS medicines
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL, quantity INTEGER,
                 expiry_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, medicine_id INTEGER, quantity INTEGER, 
                 FOREIGN KEY(medicine_id) REFERENCES medicines(id))''')
    conn.commit()
    conn.close()

def insert_medicine(name, price, quantity, expiry_date):
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    c.execute("SELECT id, quantity FROM medicines WHERE name = ?", (name,))
    result = c.fetchone()
    
    if result:
        st.error(f"{name} already exists in the inventory. Please update the quantity instead.")
    else:
        
        c.execute("INSERT INTO medicines (name, price, quantity, expiry_date) VALUES (?, ?, ?, ?)", 
                  (name, price, quantity, expiry_date))
        st.success(f"{name} has been added to the inventory.")
        conn.commit()
    conn.close()

def search_medicine(search_term):
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    c.execute("SELECT * FROM medicines WHERE name LIKE ?", ('%' + search_term + '%',))
    results = c.fetchall()
    conn.close()
    return results

def delete_medicine(medicine_id):
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    c.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
    conn.commit()
    conn.close()

def update_medicine(medicine_id, name, price, quantity, expiry_date):
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    c.execute("UPDATE medicines SET name = ?, price = ?, quantity = ?, expiry_date = ? WHERE id = ?", 
              (name, price, quantity, expiry_date, medicine_id))
    conn.commit()
    conn.close()

def get_inventory():
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    c.execute("SELECT * FROM medicines")
    inventory = c.fetchall()
    conn.close()
    return inventory

def manage_sales(medicine, quantity):
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    c.execute("INSERT INTO sales (medicine_id, quantity) VALUES (?, ?)", (medicine[0], quantity))
    c.execute("UPDATE medicines SET quantity = quantity - ? WHERE id = ?", (quantity, medicine[0]))
    conn.commit()
    conn.close()

def get_out_of_stock():
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    c.execute("SELECT * FROM medicines WHERE quantity = 0")
    out_of_stock = c.fetchall()
    conn.close()
    return out_of_stock

def get_expiring_soon(days_p=30):
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    threshold_date = (datetime.now() + timedelta(days=days_p)).strftime('%Y-%m')
    c.execute("SELECT * FROM medicines WHERE expiry_date <= ?", (threshold_date,))
    expiring_soon = c.fetchall()
    conn.close()
    return expiring_soon

def get_expired():
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    current_date = datetime.now().strftime('%Y-%m')
    c.execute("SELECT * FROM medicines WHERE expiry_date < ?", (current_date,))
    expired = c.fetchall()
    conn.close()
    return expired


def show_home():
    st.image("pharmacyimg.png", use_container_width=True)
    
    st.title("💊 Pharmacy Management System")
    st.markdown(
        """
        Welcome to the **Pharmacy Management System**, your one-stop solution for efficiently managing your pharmacy inventory. 
        
        ### 📌 Features:
        - **Inventory Management**: Add, update, and delete medicines.
        - **Sales Tracking**: Record and track medicine sales.
        - **Stock Alerts**: Get notified about out-of-stock and expired medicines.

        🔹 Use the sidebar to navigate through different sections.
        """
    )

  


def show_manage_inventory():
    
    
    manage_option = option_menu("Manage Inventory", ["Add Medicine", "Update Medicine", "Delete Medicine"], 
                                    icons=['plus', 'pencil', 'trash'], menu_icon="cast", default_index=0, orientation="horizontal")
    
    if manage_option == "Add Medicine":
        st.subheader("Add New Medicine")
        name = st.text_input("Medicine Name")
        price = st.number_input("Price",value=None,min_value=0.0,step=1.0)
        quantity = st.number_input("Quantity",step=1,min_value=1,value=None)
        
       
        expiry_year = st.selectbox("Expiry Year", range(datetime.now().year, datetime.now().year + 10))
        if expiry_year == datetime.now().year:
            expiry_month = st.selectbox("Expiry Month", range(datetime.now().month, 13))
        else:
            expiry_month = st.selectbox("Expiry Month", range(1, 13))
        expiry_date = f"{expiry_year}-{expiry_month:02d}"
        
        
        if st.button("Add Medicine"):
            insert_medicine(name, price, quantity, expiry_date)
            
    
    elif manage_option == "Delete Medicine":
        st.subheader("Delete Medicine")
        inventory = get_inventory()
        medicine_names = [item[1] for item in inventory]
        selected_medicine = st.selectbox("Select Medicine to Delete", options=medicine_names)
        
        if selected_medicine:
            if st.button("Delete Medicine"):
                medicine = next(item for item in inventory if item[1] == selected_medicine)
                delete_medicine(medicine[0])
                st.success(f"{selected_medicine} has been deleted from the inventory.")
    
    elif manage_option == "Update Medicine":
        st.subheader("Update Medicine")
        inventory = get_inventory()
        medicine_names = [item[1] for item in inventory]
        selected_medicine = st.selectbox("Select Medicine to Update", options=medicine_names, key="update_selectbox")
        
        if selected_medicine:
            medicine = next(item for item in inventory if item[1] == selected_medicine)
            
            
            name = st.text_input("Update Medicine Name", value=medicine[1], key="update_name")
            price = st.text_input("Update Price", value=str(medicine[2]), key="update_price")
            quantity = st.text_input("Update Quantity", value=str(medicine[3]), key="update_quantity")
            
            
            expiry_year = st.selectbox("Update Expiry Year", range(datetime.now().year, datetime.now().year + 10), 
                           index=datetime.strptime(medicine[4], '%Y-%m').year - datetime.now().year)
            expiry_month = st.selectbox("Update Expiry Month", range(1, 13), 
                            index=datetime.strptime(medicine[4], '%Y-%m').month - 1)

            expiry_date = f"{expiry_year}-{expiry_month:02d}"
            
            if st.button("Update Medicine"):
                update_medicine(medicine[0], name, price, quantity, expiry_date)
                st.success(f"{name} has been updated in the inventory.")

def show_inventory():
    st.title("Inventory")
    
    
    st.subheader("Search Medicine")
    search_term = st.text_input("Enter medicine name")
    
    if st.button("Search") or search_term:
        if search_term:
            inventory = search_medicine(search_term)
            if inventory:
                st.success(f"Results for '{search_term}':")
            else:
                st.warning(f"No results found for '{search_term}'. ")
        else:
            inventory = get_inventory()
            st.warning("No search term entered. Displaying full inventory.")
    else:
        inventory = get_inventory()
    
    
    
    inventory_df = pd.DataFrame(inventory, columns=["ID", "Name", "Price", "Quantity", "Expiry Date"])
    st.dataframe(inventory_df)
    

    
def alert():
    out_of_stock = get_out_of_stock()
    if out_of_stock:
        with st.expander("Out of Stock", expanded=True):
            st.error("Out of Stock")
            out_of_stock_df = pd.DataFrame(out_of_stock, columns=["ID", "Name", "Price", "Quantity", "Expiry Date"])
            st.dataframe(out_of_stock_df)

    expiring_soon = get_expiring_soon()
    if expiring_soon:
        with st.expander("Expiring Soon", expanded=True):
            st.warning("Some medicines are expiring soon!")
            expiring_soon_df = pd.DataFrame(expiring_soon, columns=["ID", "Name", "Price", "Quantity", "Expiry Date"])
            st.dataframe(expiring_soon_df)

    expired = get_expired()
    if expired:
        with st.expander("Expired Medicines", expanded=True):
            st.error("Some medicines have expired!")
            expired_df = pd.DataFrame(expired, columns=["ID", "Name", "Price", "Quantity", "Expiry Date"])
            st.dataframe(expired_df)

    if not out_of_stock and not expiring_soon and not expired:
        st.success("All medicines are in stock and have a long shelf life.")

        
def show_manage_sales():
    st.title("Manage Sales")
    inventory = get_inventory()

    if not inventory:
        st.warning("No medicines available in inventory.")
        return

    medicine_names = [item[1] for item in inventory]
    medicine = st.selectbox("Select Medicine", options=medicine_names)
    quantity = st.text_input("Quantity Sold")

    if st.button("Record Sale"):
        medicine_data = next((item for item in inventory if item[1] == medicine), None)

        if medicine_data is None:
            st.error("Medicine not found in inventory.")
            return

        medicine_id, _, _, stock_quantity, _ = medicine_data 

        if not quantity.isdigit():
            st.error("Please enter a valid quantity.")
            return

        if int(quantity) > stock_quantity:
            st.error("Insufficient stock to complete the sale.")
        else:
            manage_sales((medicine_id, medicine), int(quantity))
            st.success(f"Sale recorded for {quantity} of {medicine}.")


def main():
    with st.sidebar:
        page = option_menu("Select a page:", ["Home", "Manage Inventory", "View Inventory", "Manage Sales","Alerts"], 
                           icons=['house', 'gear', 'list', 'cart','bell'], menu_icon="cast", default_index=0)
    
    if page == "Home":
        show_home()
    elif page == "Manage Inventory":
        show_manage_inventory()
    elif page == "View Inventory":
        show_inventory()
    elif page == "Manage Sales":
        show_manage_sales()
    elif page == "Alerts":
        alert()

if __name__ == "__main__":
    create_tables()
    main() 