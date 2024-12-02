import streamlit as st
import pandas as pd
from connect_snowflake import conn, login, logOut
from math import ceil
import time

# Initialize the Snowflake session and return the cursor object
def initialize_session():
    conn = st.session_state.conn
    return conn.cursor()

def getLastIndex(cursor):
    cursor.execute(f"""SELECT index FROM SAMPLE_TABLE x
                   WHERE index > ALL(SELECT index FROM SAMPLE_TABLE y WHERE x.index != y.index)""")
    lI = cursor.fetchone()
    if not lI:
        lI = -1
        return lI
    return lI[0]

#Grabs contact entry from the dump table with the given index
def retrieve_from_ind(cursor, ind):
    if(ind > 0 and ind <= getLastIndex(cursor)): 
        cursor.execute(f"""select * from SAMPLE_TABLE where index = {ind}""")
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(result, columns=columns)
        return {
            'first_name': df['FIRST_NAME'][0],
            'last_name': df["LAST_NAME"][0],
            'email': df['EMAIL'][0],
            'phone': df['PHONE'][0],
            'address_1': df['ADDRESS_1'][0],
            'address_2': df['ADDRESS_2'][0],
            'city': df['CITY'][0],
            'state': df['STATE'][0],
            'zipcode': df['ZIPCODE'][0],
            'zip_plus_four_code': df['ZIP_PLUS_FOUR_CODE'][0],
            'info_to_remove': df['INFO_TO_REMOVE'][0]
        }
    else:
        return

def database_edit(cursor, contact, ind):
    query = f'''UPDATE SAMPLE_TABLE
                SET FIRST_NAME = '{contact['first_name']}', LAST_NAME = '{contact['last_name']}', EMAIL = '{contact['email']}', PHONE ='{contact['phone']}', 
                ADDRESS_1 = '{contact['address_1']}', ADDRESS_2 ='{contact['address_2']}', CITY = '{contact['city']}', STATE = '{contact['state']}', 
                ZIPCODE = '{contact['zipcode']}',ZIP_PLUS_FOUR_CODE ='{contact['zip_plus_four_code']}', INFO_TO_REMOVE = '{contact['info_to_remove']}', DATE_OF_DISCOVERY = GETDATE(), USER = '{st.session_state.user}',
                DUMPED = FALSE, DUMPED_DT = NULL
                WHERE INDEX = {ind}'''

    cursor.execute(query)
    
    
    

# Get the contact information from the user through text inputs
# Each field is keyed by contact_id to manage multiple contacts
def edit_contact_info(contact_info, contact_id):
    if contact_info:
        first_name = st.text_input(f"**First Name :red[*]**", f"{contact_info['first_name']}", key=f'first_name_{contact_id}')
        last_name = st.text_input(f"**Last Name :red[*]**", f"{contact_info['last_name']}", key=f'last_name_{contact_id}')
        phone = st.text_input(f"**Phone Number**", f"{contact_info['phone']}", key=f'phone_{contact_id}')
        email = st.text_input(f"**Email**", f"{contact_info['email']}", key=f'email_{contact_id}')
        address_1 = st.text_input(f"**Address 1 :red[*]**", f"{contact_info['address_1']}", key=f'address_1_{contact_id}')
        address_2 = st.text_input(f"**Address 2**", f"{contact_info['address_2']}", key=f'address_2_{contact_id}')
        city = st.text_input(f"**City :red[*]**", f"{contact_info['city']}", key=f'city_{contact_id}')
        state = st.text_input(f"**State Code (ex. KS) :red[*]**", f"{contact_info['state']}", key=f'state_{contact_id}', max_chars=2)
        zipcode = st.text_input(f"**Zipcode :red[*]**", f"{contact_info['zipcode']}", key=f'zipcode_{contact_id}')
        zip_plus_four_code = st.text_input(f"**Zipcode Extension**", f"{contact_info['zip_plus_four_code']}", key = f'zip_plus_four_code_{contact_id}')
        info_to_remove = st.text_input(f"**Info To Remove :red[*]**", f"{contact_info['info_to_remove']}", key=f'info_to_remove_{contact_id}')
    else:
        return
    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'phone': phone,
        'address_1': address_1,
        'address_2': address_2,
        'city': city,
        'state': state,
        'zipcode': zipcode,
        'zip_plus_four_code': zip_plus_four_code,
        'info_to_remove': info_to_remove
    }

def executeSQL(cursor, statement):
    cursor.execute(statement)
    result = list(cursor)
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(result, columns = columns)

def listQ(cursor, dump):
    if not dump:
        query = f"""SELECT * FROM SAMPLE_TABLE
            WHERE DUMPED = FALSE 
            ORDER BY INDEX ASC"""
    if dump:
        query = f"""SELECT * FROM SAMPLE_TABLE
            WHERE DUMPED = TRUE 
            ORDER BY INDEX ASC"""
    return executeSQL(cursor, query)


# Add or update the contact information in the contacts dictionary
def add_or_update_contact(contacts, contact_id, contact_info):
    contacts[contact_id] = contact_info

def main():
    conn()
    st.title("Edit Data Dump Entires :)")
       
    # Initialize contacts dictionary in session state if not already present
    if 'contacts' not in st.session_state:
        st.session_state.contacts = {}

    # Initialize objects in session state if not already present
    if 'conn' not in st.session_state:
        err = st.error("**Please log in.**")
    if 'cursor' not in st.session_state:
        login()
    if 'cursor' in st.session_state:
        logOut()
    if 'delCheck' not in st.session_state:
        st.session_state.delCheck = False

    if st.session_state.logged:
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Reset Contacts', type = "primary"):
                st.session_state.contacts = {}
                st.session_state.current_contact = 1
                st.rerun()
        
        if 'dump' not in st.session_state:
            st.session_state.dump = False
            
        #allows you to toggle between viewing dumped and non dumped users
        with col2:
            toggle = st.button('Toggle Dumped')
            if toggle and not st.session_state.dump:
                st.session_state.dump = True
                st.rerun()
            elif toggle and st.session_state.dump:
                st.session_state.dump = False
                st.write("False")
                st.rerun()
        
        time.sleep(.05) #When a user entry is edited it ceases to exist for a split second, thus triggering the error, this solves that problem. 
        df = pd.DataFrame(listQ(st.session_state.cursor, st.session_state.dump))
        if len(df) == 0:
            st.error("There is no data in this side of the table, try making a new entry or toggling dumped.")
        else: #Creates a dataframe with paging holding either the dumped or non dumped values
            page_size = 5
            page_number = st.number_input(
                label="Page Number",
                min_value=1,
                max_value=ceil(len(df)/page_size),
                step=1,
            )
            current_start = (page_number-1)*page_size
            current_end = page_number*page_size
            st.write(df[current_start:current_end])

            selected_contact_id = st.number_input("Select index of contact you would like to edit", min_value=1, max_value=getLastIndex(st.session_state.cursor), value= 1, step=1)
            sel = False

            contact_info = retrieve_from_ind(st.session_state.cursor, selected_contact_id)
            edited_info = contact_info
            col3, col4 = st.columns(2)
            with col3:
                if st.button('Select Contact'):
                    add_or_update_contact(st.session_state.contacts, selected_contact_id, contact_info)
                    st.session_state.selected_contact_id = selected_contact_id
            with col4:
                if st.button("Remove Contact From Table", type= 'primary'):
                    st.session_state.delCheck = True
                    
                    
                            
            if st.session_state.delCheck == True:
                with col4:
                    st.error(f"Are you sure you would like to delete contact at index {selected_contact_id}?") #Create the delete confirmation
                    col5, col6 = st.columns(2)
                    with col5:
                            if st.button("Yes"):
                                st.session_state.cursor.execute(f'DELETE FROM SAMPLE_TABLE where index = {selected_contact_id}')
                                update_query = f"""
                                                UPDATE SAMPLE_TABLE
                                                SET index = index - 1
                                                WHERE index > {selected_contact_id}
                                                """
                                st.session_state.cursor.execute(update_query)
                                st.write("done")
                                st.session_state.delCheck = False
                                st.rerun()
                    with col6:
                        if st.button("No"):
                            st.session_state.delCheck = False
                            st.rerun()
            



            if 'selected_contact_id' in st.session_state:
                edited_info = edit_contact_info(contact_info, st.session_state.selected_contact_id)
            if not 'selected_contact_id' in st.session_state:
                st.write("**Please select a contact to edit from the dropdown**")
            else:
                add_or_update_contact(st.session_state.contacts, st.session_state.selected_contact_id, edited_info)
           
            # Save the contact information to the Snowflake table
            if st.button('Save Updated Contact to Table', type="primary") and edited_info:
                eFields = False
                for info in edited_info.items():
                    key, val = info
                    if key != 'email' and key != 'address_2' and key != 'phone' and key != 'zip_plus_four_code' and val == '':
                        eFields = True
                if eFields:
                    st.error('Please fill in all required (:red[*]) fields')
                else:
                    database_edit(st.session_state.cursor, st.session_state.contacts[st.session_state.selected_contact_id], selected_contact_id)
                    st.write(f"""Contact at index {st.session_state.selected_contact_id} successfully edited""")
                    st.rerun()
        

main()
