import snowflake.connector
import streamlit as st



def login():
    if 'logged' not in st.session_state:
        st.session_state.logged = False

    logHead = st.sidebar.header("Login/Landing")
    email = st.sidebar.text_input("**Please input your Company email.**")
    sub = st.sidebar.button("Submit", type='primary')
    
    if sub and email:
        # Connect to Snowflake
        st.session_state.conn, st.session_state.cursor = get_snowflake_connection(email)
        st.session_state.logged = True 

    elif st.session_state.logged == False:
        st.sidebar.error("Please input an email into the above field.")
    if st.session_state.logged == True:
        st.sidebar.success("Successfully connected!")
        
        st.rerun()

def logOut():
    logOut = st.sidebar.button("Log Out", type="primary")
    if logOut:
        st.session_state.clear()
        st.rerun()

def conn():
    if 'logged' not in st.session_state:
        st.session_state.logged = False
    if st.session_state.logged == True:
        st.sidebar.success("Connection Active!")

#establishes and gets snowflake connection. MAKE SURE YOU CHANGE THE ROLE, WAREHOUSE, AND DATABASE BEFORE SENDING TO PROD
def get_snowflake_connection(email):
    if 'user' not in st.session_state:
        st.session_state.user = email
    # Define your Snowflake connection parameters
    account = 'sample-account.azure'
    user = email
    role = 'SAMPLE_ROLE'
    authenticator = 'externalbrowser'
    warehouse = 'SAMPLE_WAREHOUSE'
    database = 'SAMPLE_DB'
    schema = 'SAMPLE_SCHEMA'

    # Create the Snowflake connection
    conn = snowflake.connector.connect(
        user=user,
        account=account,
        role = role,
        authenticator=authenticator,
        warehouse = warehouse,
        database = database,
        schema = schema,
        client_session_keep_alive = False,
    )
    
    return conn, conn.cursor()
    
