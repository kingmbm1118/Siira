import streamlit as st
import re

# Set page configuration
st.set_page_config(
    page_title="Chat with Professional",
    page_icon="siira.jpg",  # Replace with your page icon image path
    layout="wide"  # Adjust layout as per your design
)

# Display the image
st.image("siira.jpg", width=200)  # Replace with your image path and desired width

# Main title
st.title("Chat with Professional")

# Subtitle
st.markdown("### Connect, Learn, and Network")

# Initialize session state for user data if not already done
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {
        "name": "",
        "gender": "",
        "age": "",
        "seniority": "",
        "nationality": "",
        "work_environment": "",
        "department": ""
    }

def validate_input(user_data):
    # Validation patterns
    patterns = {
        "name": r"^[A-Za-z ]+$",  # Allows only letters and spaces
        "nationality": r"^[A-Za-z ]+$",  # Same as name
        "age": r"^\d{1,3}$"  # Allows up to three digits
    }
    errors = {}
    # Validate each field
    for key, pattern in patterns.items():
        if not re.match(pattern, user_data[key]):
            errors[key] = f"Invalid input for {key}"
    return errors

# Form for input
with st.form("user_info_form"):
    user_data = {
        "name": st.text_input("Name", value=st.session_state["user_data"]["name"]),
        "gender": st.selectbox("Gender", ["Male", "Female"], index=0),
        "age": st.text_input("Age", value=st.session_state["user_data"]["age"]),
        "seniority": st.selectbox("Level of Seniority", ["Junior", "Mid-level", "Senior", "Director" , "Manager" , "Senior Manager"], index=0),
        "nationality": st.text_input("Nationality", value=st.session_state["user_data"]["nationality"]),
        "work_environment": st.radio("Do you work alone or in a team?", ["Alone", "In a team"]),
        "department": st.text_input("Department", value=st.session_state["user_data"]["department"])
    }
    submitted = st.form_submit_button("Submit")
    if submitted:
        errors = validate_input(user_data)
        if errors:
            for error in errors.values():
                st.error(error)
        else:
            st.session_state["user_data"] = user_data
            st.success(f"Welcome {user_data['name']}! You are now connected.")
            st.session_state["form_submitted"] = True

# Restart button
if "form_submitted" in st.session_state and st.session_state["form_submitted"]:
    if st.button("Restart"):
        # Clear the session state
        for key in st.session_state["user_data"]:
            st.session_state["user_data"][key] = ""
        st.session_state["form_submitted"] = False
        st.rerun()




API_KEY = "c2stcHJvai0wbnV3UmZveTZUdnBwUUpmUFc0dlQzQmxia0ZKUHl4OXB4cTFtTE9DRVJBZk5idkg=" 