import streamlit as st
import json
from datetime import datetime, timedelta

def save_to_storage():
    """Save all user data and personality assessment to storage"""
    if "user_data" in st.session_state and "personality_profile" in st.session_state:
        try:
            # Convert data to JSON strings
            user_data_json = json.dumps(st.session_state["user_data"])
            personality_profile_json = json.dumps(st.session_state["personality_profile"])
            expiry = str((datetime.now() + timedelta(days=30)).timestamp())
            
            # Save to query params
            st.query_params["user_data"] = user_data_json
            st.query_params["personality_profile"] = personality_profile_json
            st.query_params["expiry"] = expiry

            # Add JavaScript to save to localStorage
            st.markdown(
                f"""
                <script>
                    localStorage.setItem('siira_user_data', '{user_data_json}');
                    localStorage.setItem('siira_personality_profile', '{personality_profile_json}');
                    localStorage.setItem('siira_expiry', '{expiry}');
                </script>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            print(f"Error saving data: {e}")

def load_from_storage():
    """Load user data and personality assessment from storage"""
    try:
        # Get data from query parameters first
        params = st.query_params
        
        if "user_data" in params and "personality_profile" in params and "expiry" in params:
            expiry = float(params["expiry"])
            if datetime.now().timestamp() < expiry:
                st.session_state["user_data"] = json.loads(params["user_data"])
                st.session_state["personality_profile"] = json.loads(params["personality_profile"])
                st.session_state["form_submitted"] = True
                return True

        # Add JavaScript to check localStorage
        st.markdown(
            """
            <script>
                const userData = localStorage.getItem('siira_user_data');
                const personalityProfile = localStorage.getItem('siira_personality_profile');
                const expiry = localStorage.getItem('siira_expiry');
                
                if (userData && personalityProfile && expiry) {
                    const currentTime = new Date().getTime() / 1000;
                    if (currentTime < parseFloat(expiry)) {
                        // Update query params with localStorage data
                        const url = new URL(window.location.href);
                        url.searchParams.set('user_data', userData);
                        url.searchParams.set('personality_profile', personalityProfile);
                        url.searchParams.set('expiry', expiry);
                        window.history.replaceState({}, '', url);
                        window.location.reload();
                    }
                }
            </script>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        print(f"Error loading data: {e}")
        clear_storage()
    return False

def clear_storage():
    """Clear all saved data"""
    try:
        # Clear query params
        for key in list(st.query_params.keys()):
            del st.query_params[key]

        # Clear localStorage
        st.markdown(
            """
            <script>
                localStorage.removeItem('siira_user_data');
                localStorage.removeItem('siira_personality_profile');
                localStorage.removeItem('siira_expiry');
            </script>
            """,
            unsafe_allow_html=True
        )
        
        if "form_submitted" in st.session_state:
            del st.session_state["form_submitted"]
    except Exception as e:
        print(f"Error clearing data: {e}")