import streamlit as st
from openai import OpenAI
import base64
from Home import API_KEY

used_model = "gpt-4o"

def my_key(key):
    return base64.b64decode(key.encode()).decode()

client = OpenAI(api_key=my_key(API_KEY))

def initialize_session_state():
    if "custom_scenario" not in st.session_state:
        st.session_state.custom_scenario = {
            "setup_started": False,
            "setup_complete": False,
            "setup_messages": [],
            "scenario_info": "",
            "role_play_messages": [],
            "scenario_complete": False,
            "therapist_rating": 0,
            "waiting_for_user": True,
            "current_iteration": 0,
            "max_iterations": 10,
            "restart_key": 0,
            "last_visit": None,
            "user_role": "",
            "ai_role": "",
            "stopping_criteria": ""
        }

def generate_ai_message(prompt, messages):
    response = client.chat.completions.create(
        model=used_model,
        messages=[{"role": "system", "content": prompt}] + messages
    )
    return response.choices[0].message.content

def setup_scenario():
    scenario = st.session_state.custom_scenario
    if not scenario["setup_started"]:
        st.title("Custom Scenario Setup")
        st.write("Welcome to the Custom Scenario Creator! Here, you can design your own role-play scenario tailored to your specific learning needs.")
        scenario["setup_started"] = True
        initial_message = """
        Hello! I'm SiiraBot , here to help you create a custom role-play scenario. We'll work together to define the roles, conflict, and learning objectives for your scenario. 

        Let's start with a general idea. What type of scenario would you like to create? For example:
        - A job interview
        - A difficult conversation with a coworker
        - A customer service interaction
        - A performance review meeting
        - A project pitch to management

        Please provide a brief description of the scenario you have in mind.
        """
        scenario["setup_messages"].append({"role": "assistant", "content": initial_message})
        st.rerun()
        return

    if not scenario["setup_complete"]:
        setup_prompt = """
        You are an AI assistant (named SiiraBot) helping to set up a custom role-play scenario. scenario is already set so don't confuse and re do setup or scenario setting again. Your task is to engage with the user in a conversational manner to gather information about the scenario they want to create. Ask questions one at a time, and provide examples or suggestions to help the user develop their scenario. Cover the following aspects:

        1. Roles involved in the scenario (including which role the user will play and which role the AI will play)
        2. Main conflict or challenge
        3. Relevant background information for the roles (e.g., job titles, experience levels, relationships)
        4. Any specific cultural or environmental factors
        5. Desired learning outcome
        6. Stopping criteria for the scenario (be very specific about what constitutes completion)

        After each user response, acknowledge their input and ask the next relevant question. When you have enough information to create a complete scenario, summarize the scenario and ask the user if they want to make any changes. If they're satisfied, end with the phrase 'SCENARIO_READY' followed by a brief summary of the key elements.
        """

        for message in scenario["setup_messages"]:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if scenario["waiting_for_user"]:
            user_input = st.chat_input("Your response:")
            if user_input:
                scenario["setup_messages"].append({"role": "user", "content": user_input})
                scenario["waiting_for_user"] = False
                st.rerun()
        else:
            with st.spinner("SiiraBot is responding..."):
                ai_response = generate_ai_message(setup_prompt, scenario["setup_messages"])
                scenario["setup_messages"].append({"role": "assistant", "content": ai_response})
                
                if "SCENARIO_READY" in ai_response:
                    summary_start = ai_response.index("SCENARIO_READY") + len("SCENARIO_READY")
                    scenario["scenario_info"] = ai_response[summary_start:].strip()
                    
                    # Extract roles and stopping criteria from the scenario info
                    extract_prompt = """Based on the following scenario summary, please extract and provide:
                    1. The role that the user will play
                    2. The role that the AI will play
                    3. The specific stopping criteria for the scenario
                    
                    Respond in the format:
                    User Role: [role]
                    AI Role: [role]
                    Stopping Criteria: [criteria]
                    
                    Scenario summary:
                    """ + scenario["scenario_info"]
                    
                    extract_response = generate_ai_message(extract_prompt, [])
                    
                    for line in extract_response.split('\n'):
                        if line.startswith("User Role:"):
                            scenario["user_role"] = line.split(":")[1].strip()
                        elif line.startswith("AI Role:"):
                            scenario["ai_role"] = line.split(":")[1].strip()
                        elif line.startswith("Stopping Criteria:"):
                            scenario["stopping_criteria"] = line.split(":")[1].strip()
                    
                    scenario["setup_complete"] = True
                    st.success("Scenario setup complete! You can now start the role-play.")
                else:
                    scenario["waiting_for_user"] = True
                
                st.rerun()

def create_system_prompt(role, scenario_info, user_role, ai_role, stopping_criteria, max_iterations):
    if role == "ai_actor":
        return f"""You are an AI actor playing the role of {ai_role} in a custom scenario. Here are the details:

Scenario: {scenario_info}

Your role: {ai_role}
User's role: {user_role}

Your task is to play your role ({ai_role}) in this scenario, keeping in mind the main conflict and learning outcome. Adapt your communication style based on the scenario context. 

Stopping Criteria: {stopping_criteria}
Maximum Iterations: {max_iterations}

Continue the conversation until either the stopping criteria are met or the maximum number of iterations is reached. You handle one role (your role) and provide response once at a time. Do not reference any information outside of what's provided in the scenario summary."""
    elif role == "therapist":
        return f"""As a therapist, provide a detailed and personalized assessment of the user's performance in the following custom scenario:

Scenario: {scenario_info}

User's role: {user_role}
AI's role: {ai_role}

The response should not resemble an email or contain any sign-offs, or closing phrases. Instead, it should feel like a personalized discussion. Address the user directly using 'you' and 'your' to create a personalized connection. 

Evaluate their behavior and communication skills, focusing on how well they addressed the main conflict and achieved the learning outcome. Provide actionable advice for improvement, considering the scenario context.

Conclude the assessment with a rating out of 5 stars, formatted as [RATING: X], based on their performance in the scenario."""

def analyze_response(response, scenario_info, stopping_criteria, current_iteration, max_iterations):
    prompt = f"""Analyze the participant's response in the following custom scenario:

Scenario: {scenario_info}

Stopping Criteria: {stopping_criteria}
Current Iteration: {current_iteration}
Maximum Iterations: {max_iterations}

Participant's response: "{response}"

Determine if the response meets the stopping criteria or if the maximum number of iterations has been reached. If either condition is met, categorize as COMPLETE. Otherwise, categorize as CONTINUE.

Categorize as COMPLETE or CONTINUE. Briefly explain your decision:"""
    
    analysis = client.chat.completions.create(
        model=used_model,
        messages=[{"role": "user", "content": prompt}]
    )
    return analysis.choices[0].message.content

def format_feedback(feedback):    
    styled_feedback = f"""
    <div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; border-left: 5px solid #3399ff;">
        <p style="color: #0066cc; font-weight: bold;">Feedback:</p>
        <p style="color: #333333;">{feedback}</p>
    </div>
    """
    return styled_feedback

def chat():
    initialize_session_state()
    scenario = st.session_state.custom_scenario

    # Restart button at the top of the chat interface
    if st.button("Restart Scenario", key=f"custom_restart_button_{scenario['restart_key']}"):
        scenario["setup_started"] = False
        scenario["setup_complete"] = False
        scenario["setup_messages"] = []
        scenario["scenario_info"] = ""
        scenario["role_play_messages"] = []
        scenario["scenario_complete"] = False
        scenario["therapist_rating"] = 0
        scenario["waiting_for_user"] = True
        scenario["current_iteration"] = 0
        scenario["restart_key"] += 1
        scenario["user_role"] = ""
        scenario["ai_role"] = ""
        scenario["stopping_criteria"] = ""
        st.rerun()

    setup_scenario()

    if not scenario["setup_complete"]:
        return

    current_time = st.session_state.get("current_time", 0)
    if scenario["last_visit"] != current_time:
        scenario["role_play_messages"] = []
        scenario["scenario_complete"] = False
        scenario["therapist_rating"] = 0
        scenario["waiting_for_user"] = True
        scenario["current_iteration"] = 0
        scenario["restart_key"] += 1
        scenario["last_visit"] = current_time

    st.subheader("Scenario Details")
    st.write(f"**Scenario:** {scenario['scenario_info']}")
    st.write(f"**Your Role:** {scenario['user_role']}")
    st.write(f"**AI's Role:** {scenario['ai_role']}")
    st.write(f"**Stopping Criteria:** {scenario['stopping_criteria']}")

    # Add the slider for adjusting max_iterations
    scenario["max_iterations"] = st.slider(
        "Select the maximum number of conversation rounds:",
        min_value=3,
        max_value=10,
        value=5,
        key=f"custom_iteration_slider_{scenario['restart_key']}"
    )

    if not scenario["role_play_messages"]:
        with st.spinner("SiiraBot is responding..."):
            initial_message = generate_ai_message(
                create_system_prompt("ai_actor", scenario['scenario_info'], scenario['user_role'], scenario['ai_role'], scenario['stopping_criteria'], scenario['max_iterations']),
                []
            )
            scenario["role_play_messages"].append({"role": "assistant", "content": initial_message})
            scenario["waiting_for_user"] = True
        st.rerun()

    progress = min(scenario['current_iteration'] + 1, scenario['max_iterations']) / scenario['max_iterations']
    st.progress(progress, text=f"Round {min(scenario['current_iteration'] + 1, scenario['max_iterations'])}/{scenario['max_iterations']}")

    for message in scenario["role_play_messages"]:
        if message["role"] == "assistant" and message["content"].startswith("Feedback:"):
            st.markdown(format_feedback(message["content"][9:]), unsafe_allow_html=True)
        elif message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if not scenario["scenario_complete"]:
        if scenario["waiting_for_user"]:
            prompt = st.chat_input("Your response:", key=f"custom_user_input_{scenario['restart_key']}")
            if prompt:
                scenario["role_play_messages"].append({"role": "user", "content": prompt})
                scenario["waiting_for_user"] = False
                scenario["current_iteration"] += 1
                st.rerun()

        if not scenario["waiting_for_user"]:
            with st.spinner("SiiraBot is responding..."):
                analysis = analyze_response(
                    scenario["role_play_messages"][-1]["content"],
                    scenario['scenario_info'],
                    scenario['stopping_criteria'],
                    scenario['current_iteration'],
                    scenario['max_iterations']
                )
                
                if "COMPLETE" in analysis:
                    scenario["scenario_complete"] = True
                
                if not scenario["scenario_complete"]:
                    ai_response = generate_ai_message(
                        create_system_prompt("ai_actor", scenario['scenario_info'], scenario['user_role'], scenario['ai_role'], scenario['stopping_criteria'], scenario['max_iterations']),
                        scenario["role_play_messages"]
                    )
                    scenario["role_play_messages"].append({"role": "assistant", "content": ai_response})
                else:
                    feedback = generate_ai_message(
                        create_system_prompt("therapist", scenario['scenario_info'], scenario['user_role'], scenario['ai_role'], scenario['stopping_criteria'], scenario['max_iterations']),
                        scenario["role_play_messages"]
                    )
                    scenario["role_play_messages"].append({"role": "assistant", "content": f"Feedback: {feedback}"})
                
                scenario["waiting_for_user"] = True
                st.rerun()

def main():
    # Check if the name is 'Alex' or 'Sandra'
    employee_name = st.session_state.user_data["name"].strip().lower()
    if employee_name in ['alex', 'sandra']:
        chat()
    else:
        st.write(f"Welcome {st.session_state.user_data['name']}, enjoy your visit!")

if __name__ == "__main__":
    main()
