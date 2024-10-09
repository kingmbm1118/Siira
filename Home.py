import streamlit as st
import re
from personality_assessment import assess_personality
from cultural_considerations import get_cultural_context

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

if "personality_traits" not in st.session_state:
    st.session_state["personality_traits"] = {}

def validate_input(user_data):
    errors = {}
    
    # Validate name
    if not re.match(r"^[A-Za-z ]+$", user_data["name"]):
        errors["name"] = "Name should only contain letters and spaces"
    
    # Validate age
    if not isinstance(user_data["age"], int) or user_data["age"] < 18 or user_data["age"] > 100:
        errors["age"] = "Age should be a number between 18 and 100"
    
    return errors

# Get list of countries from cultural_considerations.py
def get_countries():
    default_context = get_cultural_context("")
    countries = []
    test_countries = [
        "United States", "Japan", "United Arab Emirates", "Saudi Arabia", "Egypt",
        "Jordan", "Lebanon", "Morocco", "Algeria", "Kuwait", "Qatar", "Oman",
        "Tunisia", "Bahrain", "Iraq", "Syria"
    ]
    for country in test_countries:
        if get_cultural_context(country) != default_context:
            countries.append(country)
    return sorted(countries)

countries = get_countries()

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
    
    # Add personality assessment questions
    st.subheader("Personality Assessment")
    st.write("Please answer the following questions to help us personalize your experience.")
    openness = st.slider("I am open to new experiences and ideas.", 1, 5, 3)
    conscientiousness = st.slider("I am organized and detail-oriented.", 1, 5, 3)
    extraversion = st.slider("I enjoy social interactions and being around people.", 1, 5, 3)
    agreeableness = st.slider("I am cooperative and compassionate towards others.", 1, 5, 3)
    neuroticism = st.slider("I often experience stress and anxiety.", 1, 5, 3)
    
    submitted = st.form_submit_button("Submit")
    if submitted:
        errors = validate_input(user_data)
        if errors:
            for error in errors.values():
                st.error(error)
        else:
            st.session_state["user_data"] = user_data
            
            # Assess personality
            personality_scores = {
                "openness": openness,
                "conscientiousness": conscientiousness,
                "extraversion": extraversion,
                "agreeableness": agreeableness,
                "neuroticism": neuroticism
            }
            st.session_state["personality_traits"] = assess_personality(personality_scores)
            
            st.success(f"Welcome {user_data['name']}! Your profile and personality assessment have been saved.")
            st.session_state["form_submitted"] = True

# Display personality traits if available
if "personality_traits" in st.session_state and st.session_state["personality_traits"]:
    st.subheader("Your Personality Profile")
    for trait, level in st.session_state["personality_traits"].items():
        st.write(f"{trait.capitalize()}: {level}")

# Display cultural information
if st.session_state["user_data"]["nationality"]:
    st.subheader("Cultural Context")
    cultural_info = get_cultural_context(st.session_state["user_data"]["nationality"])
    
    st.write(f"Work Week: {cultural_info['work_week']}")
    st.write(f"Communication Style: {cultural_info['communication_style']}")
    st.write(f"Special Occasions: {', '.join(cultural_info['special_occasions'])}")
    st.write(f"Cultural Values: {cultural_info['cultural_values']}")

# Restart button
if "form_submitted" in st.session_state and st.session_state["form_submitted"]:
    if st.button("Restart"):
        for key in st.session_state["user_data"]:
            st.session_state["user_data"][key] = ""
        st.session_state["personality_traits"] = {}
        st.session_state["form_submitted"] = False
        st.rerun()

API_KEY = "c2stX0l0Qk5GS2ZudmdxRVdhQUNGaXdPMXZicGRfRjNMYi1hX1JjbTNkbEJ5VDNCbGJrRkpUam9LOUZFMi1XYWpOX3BndGZjUTJLVGYydk1QS1B4dmRQdU1LX2tXMEE="
