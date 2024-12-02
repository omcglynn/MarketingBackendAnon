import streamlit as st
from connect_snowflake import conn, login, logOut

def main():
    conn()
    if 'cursor' not in st.session_state:
        login()
    if 'cursor' in st.session_state:
        logOut()
    st.title("Marketing DNM Landing")
    st.write(f"""Welcome to your do not mail submission form! The information below contains general usage information for this app. 
             **To get started, just input your Company email into the box on the sidebar and hit submit! This will automatically sign you in if you have correct access.**""")
    st.write("-")
    
    st.subheader('\n📑 Form')
    st.write("This will most likely be your most used portion of this app. This page allows you to streamline your submission request into for multiple or even just one customer.")

    with st.expander(f"""**Usage**""", icon = "🤔"):
        st.markdown(f"""    	-• Enter your user's information in the provided text fields, ensuring to fill all of those with a :red[*] next to their name""")
        st.markdown(f"""    	-• Click the "Add/Update Contact in List" button. (Does not save to table quite yet)""")
        st.markdown(f"""    	-• If you only need to add just that user, click "Save Contact to Table" """)
        st.markdown(f"""    	-• Otherwise, scroll back up to the top and select the next contact index that has appeared.""")
        st.markdown(f"""    	-• Repeat previous steps""")
        st.markdown(f"""    	-• You are able to go back and edit previously created list entries before they're sent to the table by just going to them, changing the inputs, and clicking the add or update button again.""")
        st.markdown(f"""    	-• To submit all of your inputted customers, click the "Save All Contacts to Table" """)
        st.markdown(f"""-• And you're done! If something wont submit ensure you have all fields appropriately filled in and with the information requested.""")
        #st.markdown(f"""    	-• It is okay if the name, phone number,""")


    st.subheader('\n✏️ Edit')
    st.write("This section is responsible for editing any mistakes that have already been submitted to the database server.")
    with st.expander(f"""**Usage**""", icon = "🥴"):
        st.markdown(f"""\n    	-• First, select the index of the contact you would like to update""")
        st.markdown(f"""    	-- -• Can be found using the table propegated at the top of the page """)
        st.markdown(f"""    	-- -• If you cant find the user you're looking for, try either searching the list or hitting the "Toggle Dumped" button and check again.""")
        st.markdown(f"""    	-• Then edit whatever info needs to be changed. Required fields are still required and some still have constraints (State Code specifically)""")
        st.markdown(f"""    	-• Whenever you feel like youre done just hit the submit changes button at the bottom and your updates will be sent to the table!""")
        st.markdown(f"""        -• If your edit happened to be on a customer already marked as "Dumped", their dumped status will be reset to false and thus will fall on the other side of the view table.""")
        st.markdown(f"""    	-• If you plan on using the delete function, make sure you are deleting the correct index. This is not reversible.""")

    st.subheader('\n👨🏻‍💻 Other')
    st.write("Just for general information about usage or possible issues.")
    with st.expander(f"""**Gen. Notes**""", icon = "💢"):
        st.markdown(f"""-• Please try to ensure that there are no extra characters such as accidental spaces or otherwise, this may cause the customer to not be found by the backend.""")
        st.markdown(f"""-• Do not worry how address 1 street names are written, for example, Street, st, st., etc... will all return the same thing.""")
        st.markdown(f"""-• The most important part of your entry is the address. The DNM info can be changed with everything else being incorrect.""")


main()

