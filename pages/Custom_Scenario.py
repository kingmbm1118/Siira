import streamlit as st
from openai import OpenAI
import base64
from Home import API_KEY

def my_key(key):
    return base64.b64decode(key.encode()).decode()

client = OpenAI(api_key=my_key(API_KEY))

def generate_siirabot_message(prompt, messages):
    full_messages = [{"role": "system", "content": prompt}] + messages
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=full_messages
    )
    return response.choices[0].message.content

def setup_scenario():
    st.title("Custom Role-Play Scenario Setup")
    
    if 'setup_messages' not in st.session_state:
        st.session_state.setup_messages = []
    
    if 'scenario_data' not in st.session_state:
        st.session_state.scenario_data = {}
    
    if 'setup_complete' not in st.session_state:
        st.session_state.setup_complete = False

    setup_prompt = """You are SiiraBot, an assistant tasked with setting up a custom role-play scenario. Ask the user questions to gather the following information, providing examples for each:

    1. The roles involved in the scenario
    2. The main conflict or issue to be addressed
    3. Any specific cultural or environmental factors to consider
    4. The desired learning outcome for the participant
    5. The stopping criteria for the scenario

    Ask one question at a time and wait for the user's response before moving to the next question. Once all necessary information is gathered, summarize the scenario details and ask the user to confirm. Then, ask which role SiraBot should play in the scenario. After the user confirms all details, inform them that they can now start the role-play."""

    for message in st.session_state.setup_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if not st.session_state.setup_messages:
        with st.spinner("SiiraBot is thinking..."):
            siirabot_response = generate_siirabot_message(setup_prompt, [])
        st.session_state.setup_messages.append({"role": "assistant", "content": siirabot_response})
        st.rerun()

    if st.session_state.setup_messages[-1]["role"] == "assistant":
        user_input = st.chat_input("Your response:", key="setup_input")
        if user_input:
            st.session_state.setup_messages.append({"role": "user", "content": user_input})
            with st.spinner("siiraBot is thinking..."):
                siirabot_response = generate_siirabot_message(setup_prompt, st.session_state.setup_messages)
            st.session_state.setup_messages.append({"role": "assistant", "content": siirabot_response})
            
            if "can now start the role-play" in siirabot_response.lower():
                st.session_state.setup_complete = True
                st.session_state.scenario_data = parse_scenario_summary(siirabot_response)
            
            st.rerun()

    if st.session_state.setup_complete:
        st.write("Scenario Details:")
        for key, value in st.session_state.scenario_data.items():
            st.write(f"{key}: {value}")
        
        if st.button("Start Role-Play"):
            st.session_state.role_play_started = True
            st.session_state.role_play_messages = []
            st.session_state.current_iteration = 0
            st.rerun()

def parse_scenario_summary(summary):
    lines = summary.split('\n')
    scenario_data = {}
    current_key = None
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            current_key = key.strip('* ').strip()
            scenario_data[current_key] = value.strip()
        elif current_key and line.strip():
            scenario_data[current_key] += ' ' + line.strip()
    
    # Ensure SiiraBot's role is included in the scenario data
    if 'siiraBot Role' not in scenario_data:
        for line in lines:
            if "siirabot should play" in line.lower():
                scenario_data['siiraBot Role'] = line.split("play")[-1].strip()
                break
    
    return scenario_data

def role_play():
    st.title("Custom Role-Play Scenario")
    
    if 'role_play_messages' not in st.session_state:
        st.session_state.role_play_messages = []

    if 'max_iterations' not in st.session_state:
        st.session_state.max_iterations = 5  # Default value

    # Dropdown for selecting the number of iterations
    st.session_state.max_iterations = st.selectbox(
        "Select the maximum number of conversation rounds:",
        options=range(3, 16),
        index=st.session_state.max_iterations - 3,
        key="iteration_selector"
    )

    if not st.session_state.role_play_messages:
        # Initialize the role-play with the scenario details
        scenario_prompt = f"""You are siiraBot conducting a role-play scenario with the following details:
        Roles: {st.session_state.scenario_data.get('Roles', '')}
        Main Conflict: {st.session_state.scenario_data.get('Main Conflict', '')}
        Cultural/Environmental Factors: {st.session_state.scenario_data.get('Cultural/Environmental Factors', '')}
        Learning Outcome: {st.session_state.scenario_data.get('Learning Outcome', '')}
        Stopping Criteria: {st.session_state.scenario_data.get('Stopping Criteria', '')}
        siiraBot Role: {st.session_state.scenario_data.get('siiraBot Role', '')}

        You will play the role of {st.session_state.scenario_data.get('siiraBot Role', '')}. Begin the role-play by setting the scene and starting the interaction."""

        with st.spinner("siiraBot is starting the role-play..."):
            siirabot_response = generate_siirabot_message(scenario_prompt, [])
        st.session_state.role_play_messages.append({"role": "assistant", "content": siirabot_response})
        st.rerun()

    # Clear previous messages
    st.empty()

    for message in st.session_state.role_play_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    st.write(f"Current iteration: {st.session_state.current_iteration + 1} / {st.session_state.max_iterations}")

    if st.session_state.role_play_messages[-1]["role"] == "assistant":
        user_input = st.chat_input("Your response:", key="role_play_input")
        if user_input:
            st.session_state.role_play_messages.append({"role": "user", "content": user_input})
            st.session_state.current_iteration += 1
            
            # Check for stopping criteria
            if st.session_state.current_iteration >= st.session_state.max_iterations:
                st.success("Role-play complete!")
                provide_feedback()
            else:
                with st.spinner("siiraBot is responding..."):
                    siirabot_response = generate_siirabot_message(f"Continue the role-play based on the user's input. Remember, you are playing the role of {st.session_state.scenario_data.get('siiraBot Role', '')}.", st.session_state.role_play_messages)
                st.session_state.role_play_messages.append({"role": "assistant", "content": siirabot_response})
                st.rerun()

def provide_feedback():
    feedback_prompt = f"""You are siiraBot providing feedback on a role-play scenario. The scenario details are:
    Roles: {st.session_state.scenario_data.get('Roles', '')}
    Main Conflict: {st.session_state.scenario_data.get('Main Conflict', '')}
    Learning Outcome: {st.session_state.scenario_data.get('Learning Outcome', '')}

    Review the conversation and provide constructive feedback on how well the participant handled the scenario. Consider their communication skills, problem-solving approach, and how well they achieved the learning outcome.

    Provide a rating out of 5 stars, formatted as [RATING: X], at the end of your feedback."""

    with st.spinner("siiraBot is generating feedback..."):
        feedback = generate_siirabot_message(feedback_prompt, st.session_state.role_play_messages)
    
    st.subheader("siiraBot's Feedback")
    feedback_without_rating = feedback.split('[RATING:')[0].strip()
    st.write(feedback_without_rating)

    rating = extract_rating(feedback)
    stars = display_stars(rating)
    st.markdown(f"<h3>Your performance rating: {stars} ({rating:.1f}/5)</h3>", unsafe_allow_html=True)

    if st.button("Start New Scenario"):
        reset_session_state()
        st.rerun()

def extract_rating(feedback):
    try:
        return float(feedback.split('[RATING:')[1].split(']')[0].strip())
    except:
        return 0

def display_stars(rating):
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    return "⭐" * full_stars + ("½" if half_star else "") + "☆" * empty_stars

def reset_session_state():
    keys_to_keep = ['user_data']
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]

def main():
    if 'user_data' not in st.session_state:
        st.error("Please complete your profile on the Home page first.")
        return

    if st.sidebar.button("Restart Scenario"):
        reset_session_state()
        st.rerun()

    employee_name = st.session_state.user_data.get("name", "").strip().lower()
    
    if employee_name in ['alex', 'sandra']:
        if 'role_play_started' not in st.session_state or not st.session_state.role_play_started:
            setup_scenario()
        else:
            role_play()
    else:
        st.write(f"Welcome {st.session_state.user_data.get('name', '')}, enjoy your visit!")

if __name__ == "__main__":
    main()
