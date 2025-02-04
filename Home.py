import streamlit as st
import re
from personality_assessment import PersonalityAssessment
from cultural_considerations import get_cultural_context
from storage_manager import save_to_storage, load_from_storage, clear_storage  # Update import

# Set page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="Chat with Professional",
    page_icon="siira.jpg",
    layout="wide"
)


# Enhanced CSS for better theme compatibility
st.markdown("""
    <style>
    /* Theme-aware colors */
    :root {
        --primary-color: #06B6D4;
        --secondary-color: #0EA5E9;
        --background-color: #ECFEFF;
        --text-color: #1F2937;
        --card-background: rgba(255, 255, 255, 0.9);
        --card-border: #06B6D4;
    }

    /* Dark theme overrides */
    [data-theme="dark"] {
        --text-color: #F3F4F6;
        --card-background: rgba(17, 25, 40, 0.9);
        --card-border: #0EA5E9;
    }
    
    /* General styles */
    .stApp {
        background: linear-gradient(to bottom, var(--background-color), white);
    }

    [data-theme="dark"] .stApp {
        background: linear-gradient(to bottom, #0F172A, #1E293B);
    }
    
    /* Typography */
    .main-title {
        color: var(--primary-color) !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 2.5rem;
        text-align: center;
        text-shadow: 0 0 10px rgba(6, 182, 212, 0.2);
        margin-bottom: 1rem;
    }

    [data-theme="dark"] .main-title {
        color: #38BDF8 !important;
    }

    .subtitle {
        color: var(--secondary-color) !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 1.5rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Form elements */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color)) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
        border-radius: 8px !important;
    }
    
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border-color: var(--card-border) !important;
        background-color: var(--card-background) !important;
        color: var(--text-color) !important;
    }

    /* Cards styling */
    .trait-card {
        background-color: var(--card-background);
        border: 1px solid var(--card-border);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    [data-theme="dark"] .trait-card {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    .recommendation-card {
        background-color: var(--card-background);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--primary-color);
    }

    /* Headers and text */
    .card-header {
        color: var(--primary-color);
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    [data-theme="dark"] .card-header {
        color: #38BDF8;
    }

    .card-text {
        color: var(--text-color);
        line-height: 1.6;
    }

    /* Success/Error messages */
    .success-message {
        background-color: rgba(6, 182, 212, 0.1);
        border-left: 4px solid var(--primary-color);
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }

    .error-message {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #EF4444;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }

    /* Center image */
    .center-image {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Display centered image
st.markdown('<div class="center-image">', unsafe_allow_html=True)
st.image("siira.jpg", width=200)
st.markdown('</div>', unsafe_allow_html=True)

# Main title and subtitle
st.markdown('<h1 class="main-title">Chat with Professional</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="subtitle">Connect, Learn, and Network</h3>', unsafe_allow_html=True)

# Initialize session state and try to load from cookies
if not load_from_storage():
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

# Initialize personality assessment
personality_questions = PersonalityAssessment.get_questions()

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
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="card-header">Personal Information</p>', unsafe_allow_html=True)
        user_data = {
            "name": st.text_input("Name", value=st.session_state["user_data"]["name"]),
            "gender": st.selectbox("Gender", ["Male", "Female"], index=0),
            "age": st.number_input("Age", min_value=18, max_value=100, value=int(st.session_state["user_data"]["age"]) if st.session_state["user_data"]["age"] else 18),
            "seniority": st.selectbox("Level of Seniority", seniority_levels, index=seniority_levels.index(st.session_state["user_data"]["seniority"]) if st.session_state["user_data"]["seniority"] in seniority_levels else 0),
            "nationality": st.selectbox("Nationality", countries, index=countries.index(st.session_state["user_data"]["nationality"]) if st.session_state["user_data"]["nationality"] in countries else 0),
            "work_environment": st.radio("Work Environment", ["Individual Contributor", "Team Member", "Team Lead", "Remote Worker", "Hybrid"], index=0),
            "department": st.selectbox("Department", ["Sales", "Marketing", "Engineering", "Product", "Design", "Finance", "Human Resources", "Customer Support", "Operations"], index=0)
        }

    with col2:
        st.markdown('<p class="card-header">Personality Assessment</p>', unsafe_allow_html=True)
        st.write("Please answer these questions to help us understand your personality and work style preferences.")
        
        # Initialize dictionary to store responses for each trait
        responses = {trait: [] for trait in personality_questions.keys()}
        
        # Create tabs for different trait categories
        tabs = st.tabs(["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Emotional Stability"])
        
        for trait, tab in zip(personality_questions.keys(), tabs):
            with tab:
                for i, question in enumerate(personality_questions[trait]):
                    # Get the saved value from session state if it exists
                    saved_value = 3  # Default value
                    if "personality_profile" in st.session_state and trait in st.session_state["personality_profile"]:
                        saved_value = st.session_state["personality_profile"][trait].get("responses", [])[i] if i < len(st.session_state["personality_profile"][trait].get("responses", [])) else 3
                    
                    response = st.slider(
                        f"{question}",
                        min_value=1,
                        max_value=5,
                        value=saved_value,
                        help="1 = Strongly Disagree, 5 = Strongly Agree"
                    )
                    responses[trait].append(response)
    
    submitted = st.form_submit_button("Submit")
    if submitted:
        errors = validate_input(user_data)
        if errors:
            for error in errors.values():
                st.markdown(f'<div class="error-message">{error}</div>', unsafe_allow_html=True)
        else:
            st.session_state["user_data"] = user_data
            
            # Assess personality with enhanced system
            personality_profile = PersonalityAssessment.assess_personality(responses)
            st.session_state["personality_profile"] = personality_profile
            
            # Save to cookies
            save_to_storage()
            
            st.markdown(f'<div class="success-message">Welcome {user_data["name"]}! Your profile and personality assessment have been saved.</div>', unsafe_allow_html=True)
            st.session_state["form_submitted"] = True

# Display results
if "form_submitted" in st.session_state and st.session_state["form_submitted"]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<p class="card-header">Your Personality Profile</p>', unsafe_allow_html=True)
        
        for trait, data in st.session_state["personality_profile"].items():
            if trait != "recommendations":
                st.markdown(f"""
                    <div class="trait-card">
                        <div class="card-header">{trait.capitalize()}</div>
                        <div class="card-text">
                            <strong>Level:</strong> {data['level']}<br>
                            {data['description']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # Display cultural information
        if st.session_state["user_data"]["nationality"]:
            st.markdown('<p class="card-header">Cultural Context</p>', unsafe_allow_html=True)
            cultural_info = get_cultural_context(st.session_state["user_data"]["nationality"])
            
            st.markdown(f"""
                <div class="trait-card">
                    <div class="card-text">
                        <strong>Work Week:</strong> {cultural_info['work_week']}<br>
                        <strong>Communication Style:</strong> {cultural_info['communication_style']}<br>
                        <strong>Special Occasions:</strong> {', '.join(cultural_info['special_occasions'])}<br>
                        <strong>Cultural Values:</strong> {cultural_info['cultural_values']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Display work style recommendations
        st.markdown('<p class="card-header">Work Style Recommendations</p>', unsafe_allow_html=True)
        recommendations = st.session_state["personality_profile"]["recommendations"]
        
        for category, items in recommendations.items():
            st.markdown(f"""
                <div class="recommendation-card">
                    <div class="card-header">{category.replace('_', ' ').title()}</div>
                    <div class="card-text">
                        <ul>
                            {''.join(f'<li>{item}</li>' for item in items)}
                        </ul>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Restart button
if "form_submitted" in st.session_state and st.session_state["form_submitted"]:
    if st.button("Restart"):
        clear_storage()  # Clear the cookies
        for key in st.session_state["user_data"]:
            st.session_state["user_data"][key] = ""
        st.session_state["personality_traits"] = {}
        st.session_state["form_submitted"] = False
        st.rerun()

API_KEY = "c2stcHJvai01QkM2cGtyU01zVVZHNUpvUjRCQTI0RlhVOGwyc0xqNWM0eTBJbHJ5Tnl0aTUyRVRua0Nhd0M1MkwtT0hxZm9YQjYxdjNvSXJxZFQzQmxia0ZKTXdBa3p3a0dUMWxGamNhUTFUenFVc3E1bmlhZUVINVVqcnhOcWwtYVhBcThWdy15SW9UVVo2S0UtVW1EREVOSm5oUmgtR2FTa0E="
