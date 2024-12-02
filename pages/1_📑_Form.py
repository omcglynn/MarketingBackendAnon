import streamlit as st
import pandas as pd
from connect_snowflake import conn, login, logOut
import itertools

# Initialize the Snowflake session and return the cursor object
def initialize_session():
    conn = st.session_state.conn
    return conn.cursor()

#Self
def getLastIndex(cursor):
    cursor.execute(f"""SELECT index FROM SAMPLE_TABLE x
                   WHERE index > ALL(SELECT index FROM SAMPLE_TABLE y WHERE x.index != y.index)""")
    lI = cursor.fetchone()
    if not lI:
        lI = 0
        return lI
    return lI[0]

# Get the contact information from the user through text inputs
# Each field is keyed by contact_id to manage multiple contacts
def get_contact_info(contact_id):
    contact_info = st.session_state.contactsF.get(contact_id)
    if contact_info: #Checks if there is already contact info for selected ID and if so, propagates it in respective fields
        first_name = st.text_input(f"**First Name :red[*]**", f"{contact_info['first_name']}", key=f'first_name_{contact_id}')
        last_name = st.text_input(f"**Last Name :red[*]**", f"{contact_info['last_name']}", key=f'last_name_{contact_id}')
        email = st.text_input(f"**Email**", f"{contact_info['email']}", key=f'email_{contact_id}')
        phone = st.text_input(f"**Phone Number**", f"{contact_info['phone']}", key=f'phone_{contact_id}')
        address_1 = st.text_input(f"**Address 1 :red[*]**", f"{contact_info['address_1']}", key=f'address_1_{contact_id}')
        address_2 = st.text_input(f"**Address 2**", f"{contact_info['address_2']}", key=f'address_2_{contact_id}')
        city = st.text_input(f"**City :red[*]**", f"{contact_info['city']}", key=f'city_{contact_id}')
        state = st.text_input(f"**State Code (ex. KS) :red[*]**", f"{contact_info['state']}", key=f'state_{contact_id}', max_chars= 2)
        zipcode = st.text_input(f"**Zipcode :red[*]**", f"{contact_info['zipcode']}", key=f'zipcode_{contact_id}')
        zip_plus_four_code = st.text_input(f"**Zipcode Extension**", f"{contact_info['zip_plus_four_code']}", key = f'zip_plus_four_code_{contact_id}')
        info_to_remove = st.text_input(f"**Info To Remove :red[*]**", f"{contact_info['info_to_remove']}", key=f'info_to_remove_{contact_id}')
    else:
        first_name = st.text_input(f"**First Name :red[*]**", key=f'first_name_{contact_id}')
        last_name = st.text_input(f"**Last Name :red[*]**", key=f'last_name_{contact_id}')
        email = st.text_input(f"**Email**", key=f'email_{contact_id}')
        phone = st.text_input(f"**Phone Number**", key=f'phone_{contact_id}')
        address_1 = st.text_input(f"**Address 1 :red[*]**", key=f'address_1_{contact_id}')
        address_2 = st.text_input(f"**Address 2**", key=f'address_2_{contact_id}')
        city = st.text_input(f"**City :red[*]**", key=f'city_{contact_id}')
        state = st.text_input(f"**State Code (ex. KS) :red[*]**", key=f'state_{contact_id}', max_chars= 2)
        zipcode = st.text_input(f"**Zipcode :red[*]**", key=f'zipcode_{contact_id}')
        zip_plus_four_code = st.text_input(f"**Zipcode Extension**", key = f'zip_plus_four_code_{contact_id}')
        info_to_remove = st.text_input(f"**Info To Remove :red[*]**", key=f'info_to_remove_{contact_id}')
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

def dupeChecker(contact):
    cDF = pd.DataFrame.from_dict(contact, orient = 'index')
    cDF = cDF.transpose()
    cDF= cDF.drop(columns=['info_to_remove'])

    abbreviations = {
            "drive": ["dr", "drv", "dve", "dr."],
            "street": ["st", "str", "st.", "strt"],
            "avenue": ["ave", "av", "av.", "avenu"],
            "boulevard": ["blvd", "boul", "bvd", "boulv"],
            "road": ["rd", "rd.", "rode"],
            "lane": ["ln", "ln.", "lne"],
            "terrace": ["ter", "ter.", "terr"],
            "place": ["pl", "pl.", "plc"],
            "court": ["ct", "ct.", "cour"]
        }
    cursor = st.session_state.cursor

    pT = pd.DataFrame(cursor.execute("select first_name, last_name, email, phone, address_1, address_2, city, state, zipcode, zip_plus_four_code from SAMPLE_TABLE"), columns=cDF.columns)
        # Create a reverse lookup dictionary to map values back to their keys
    reverse_abbreviations = {abbr: key for key, abbrs in abbreviations.items() for abbr in abbrs}
    # Split the address into parts
    add1 = cDF['address_1'][0].lower()
    parts = add1.split()
    # Create a list to hold possible variations of each part
    possible_variations = []

    # Iterate over each part of the address
    for part in parts:
        # Add the original part to the variations
        variations = [part]
        # If the part has known abbreviations or misspellings, add those to the variations
        if part in abbreviations:
            variations.extend(abbreviations[part])
        elif part in reverse_abbreviations:
            # Add the original key and all of its abbreviations/misspellings
            key = reverse_abbreviations[part]
            variations.append(key)
            variations.extend(abbreviations[key])
        possible_variations.append(variations)
    
    appCS = (cDF['city'][0].lower(), cDF['state'][0].lower())
    
    # Use itertools.product to create all possible combinations of the variations
    all_combinations = list(itertools.product(*possible_variations))
    i = 0
    for item in all_combinations:
        item = item + (appCS)
        all_combinations[i] = item
        i+=1

    ptList = pT['address_1'] +' '+ pT['city'] +' '+ pT['state']
    
    all_variations = [' '.join(combination) for combination in all_combinations]
    for var in all_variations:
        if var in list(ptList):
            return True
    return False

# Add or update the contact information in the contacts dictionary
def add_or_update_contact(contacts, contact_id, contact_info):
    contacts[contact_id] = contact_info

def main():
    st.title("Marketing Do Not Email Form :)")

    conn()

    # Initialize contacts dictionary in session state if not already present
    if 'contactsF' not in st.session_state:
        st.session_state.contactsF = {}

    # Initialize Snowflake cursor in session state if not already present
    if 'conn' not in st.session_state:
        st.error("**Please log in.**")
    if 'cursor' not in st.session_state:
        login()
    if 'cursor' in st.session_state:
        logOut()
    

    if 'contact_id' not in st.session_state:
        st.session_state.contact_id = 1
    if st.session_state.logged:

        if st.button('Reset Contacts', type = "primary"):
            st.session_state.contactsF = {}
            st.session_state.current_contact = 1
            st.session_state.contact_id = 1
            st.rerun()

        
        # Get list of contact IDs
        contact_ids = list(st.session_state.contactsF.keys())
        # Populate selectbox with contact IDs
        selected_contact_id = st.selectbox("Select Contact", options=["Contact 1"] + [f"Contact {i+1}" for i in contact_ids], index = st.session_state.contact_id-1)


        # Determine the selected contact ID
        if selected_contact_id == "Contact 1":
            st.session_state.contact_id = 1
        else:
            st.session_state.contact_id = int(selected_contact_id.split()[1])

        # Get the contact information from the user
        contact_info = get_contact_info(st.session_state.contact_id)
        
        # Add or update the contact information when the button is pressed
        if st.button('Add/Update Contact in List'):
            eFields = False
            
            for info in contact_info.items():
                key, val = info
                if key != 'email' and key != 'address_2' and key != 'phone' and key != 'zip_plus_four_code' and val == '':
                    eFields = True
            if eFields:
                st.error('Please fill in all required (:red[*]) fields')
            else:
                add_or_update_contact(st.session_state.contactsF, st.session_state.contact_id, contact_info)
                st.rerun()

        # Save the contact information to the Snowflake table
        col1, col2 = st.columns(2, gap='small')
        with col1:
            if st.button('Save This Contact to Table', type="primary"):
                contact_info = st.session_state.contactsF.get(st.session_state.contact_id)
                dupeQ = dupeChecker(contact_info)
                if dupeQ:
                    st.write(f"""**Duplicate entry for Contact {st.session_state.contact_id} already found in table**""")
                else:
                    query = f"""
                        INSERT INTO SAMPLE_TABLE (first_name, last_name, email, phone, address_1, address_2, city, state, zipcode, zip_plus_four_code, info_to_remove, date_of_discovery, user, dumped, index)
                        VALUES ('{contact_info['first_name']}', '{contact_info['last_name']}', '{contact_info['email']}', '{contact_info['phone']}', 
                        '{contact_info['address_1']}', '{contact_info['address_2']}', '{contact_info['city']}', '{contact_info['state']}', 
                        '{contact_info['zipcode']}','{contact_info['zip_plus_four_code']}', '{contact_info['info_to_remove']}', GETDATE(), '{st.session_state.user}', 'n', {getLastIndex(st.session_state.cursor) + 1})
                    """
                    st.session_state.cursor.execute(query)
                    st.write(f"Contact {st.session_state.contact_id} saved to table at index {getLastIndex(st.session_state.cursor)}")

        with col2:
            if st.button('Save All Contacts to Table', type = 'primary'):
                i = 1
                for contact_info in st.session_state.contactsF.values():
                    dupeQ = dupeChecker(contact_info)
                    if dupeQ:
                        st.write(f"""**Duplicate entry for Contact {i} already found in table**""")
                    else:
                        query = f"""
                            INSERT INTO SAMPLE_TABLE (first_name, last_name, email, phone, address_1, address_2, city, state, zipcode, zip_plus_four_code, info_to_remove, date_of_discovery, user, dumped, index)
                            VALUES ('{contact_info['first_name']}', '{contact_info['last_name']}', '{contact_info['email']}', '{contact_info['phone']}', 
                            '{contact_info['address_1']}', '{contact_info['address_2']}', '{contact_info['city']}', '{contact_info['state']}', 
                            '{contact_info['zipcode']}','{contact_info['zip_plus_four_code']}', '{contact_info['info_to_remove']}', GETDATE(), '{st.session_state.user}', 'n', {getLastIndex(st.session_state.cursor) + 1})
                        """
                        st.session_state.cursor.execute(query)
                        st.write(f"**Contact {i} saved to table at index {getLastIndex(st.session_state.cursor)}**")
                    i+=1

        st.write(pd.DataFrame(st.session_state.contactsF).transpose())


main()
    