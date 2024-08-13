import streamlit as st
import re
import pycountry

# Set page configuration
st.set_page_config(
    page_title="Chat with Professional",
    page_icon="siira.jpg",
    layout="wide"
)

# Display the image
st.image("siira.jpg", width=200)

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
    errors = {}
    
    # Validate name
    if not re.match(r"^[A-Za-z ]+$", user_data["name"]):
        errors["name"] = "Name should only contain letters and spaces"
    
    # Validate age
    if not isinstance(user_data["age"], int) or user_data["age"] < 18 or user_data["age"] > 100:
        errors["age"] = "Age should be a number between 18 and 100"
    
    return errors

# Get list of countries
countries = sorted([country.name for country in pycountry.countries])

# Define updated seniority levels
seniority_levels = [
    "Entry-Level/Junior",
    "Mid-Level",
    "Senior-Level",
    "Lead/Principal",
    "Managerial",
    "Director",
    "Vice President (VP)",
    "C-Level Executive"
]

# Form for input
with st.form("user_info_form"):
    user_data = {
        "name": st.text_input("Name", value=st.session_state["user_data"]["name"]),
        "gender": st.selectbox("Gender", ["Male", "Female"], index=0),
        "age": st.number_input("Age", min_value=18, max_value=100, value=int(st.session_state["user_data"]["age"]) if st.session_state["user_data"]["age"] else 18),
        "seniority": st.selectbox("Level of Seniority", seniority_levels, index=seniority_levels.index(st.session_state["user_data"]["seniority"]) if st.session_state["user_data"]["seniority"] in seniority_levels else 0),
        "nationality": st.selectbox("Nationality", countries, index=countries.index(st.session_state["user_data"]["nationality"]) if st.session_state["user_data"]["nationality"] in countries else 0),
        "work_environment": st.radio("Work Environment", ["Individual Contributor", "Team Member", "Team Lead", "Remote Worker", "Hybrid"], index=0),
        "department": st.selectbox("Department", ["Sales", "Marketing", "Engineering", "Product", "Design", "Finance", "Human Resources", "Customer Support", "Operations"], index=0)
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
        for key in st.session_state["user_data"]:
            st.session_state["user_data"][key] = ""
        st.session_state["form_submitted"] = False
        st.rerun()

API_KEY = "c2stcHJvai0wbnV3UmZveTZUdnBwUUpmUFc0dlQzQmxia0ZKUHl4OXB4cTFtTE9DRVJBZk5idkg="
