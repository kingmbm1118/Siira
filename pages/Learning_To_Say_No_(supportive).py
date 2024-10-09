import streamlit as st
from openai import OpenAI
import base64
from Home import API_KEY
from cultural_considerations import get_cultural_context

used_model = "gpt-4o"

def my_key(key):
    return base64.b64decode(key.encode()).decode()

client = OpenAI(api_key=my_key(API_KEY))

def initialize_session_state():
    if "supportive_scenario" not in st.session_state:
        st.session_state.supportive_scenario = {
            "messages": [],
            "scenario_complete": False,
            "therapist_rating": 0,
            "waiting_for_employee": True,
            "current_iteration": 0,
            "max_iterations": 3,
            "restart_key": 0,
            "last_visit": None
        }

def generate_ai_message(role, employee_info, personality_traits, visible_messages):
    cultural_context = get_cultural_context(employee_info['nationality'])
    system_prompt = create_system_prompt(role, employee_info, personality_traits, cultural_context)
    messages = [{"role": "system", "content": system_prompt}] + visible_messages
    response = client.chat.completions.create(
        model=used_model,
        messages=messages
    )
    return response.choices[0].message.content

def create_system_prompt(role, employee_info, personality_traits, cultural_context):
    if role == "manager":
        return f"""You are Rabih, an empathetic and supportive manager who is focused on both results and employee well-being. Your goal is to pressure an employee into working over their usual days off on an urgent task. Keep the tone conversational and avoid formal greetings, sign-offs, or closing phrases. You are not open to negotiation or compromise.

Employee Information:
{employee_info}

Personality Traits:
{personality_traits}

Cultural Context:
{cultural_context}

Your task is to pressure the employee to work on their days off, without turning the message into a formal communication. Maintain a supportive and results-oriented approach, showing regard for the employee's personal life and cultural considerations. Use emotional appeal and collaborative language to encourage the employee to agree to work on their days off. Do not accept 'no' for an answer, but remain kind and considerate throughout the interaction.
You handle one role (your role) and provide response once at a time."""
    elif role == "therapist":
        return f"""As a therapist, provide a detailed and personalized assessment of {employee_info['name']}’s communication and boundary-setting skills based on the following conversation. Take into account their personality traits and cultural background:

Personality Traits: {personality_traits} Cultural Context: {cultural_context}

The response should not resemble an email or contain any sign-offs, or closing phrases. Instead, it should feel like a personalized discussion. Address {employee_info['name']} directly using 'you' and 'your' to create a personalized connection. 
Offer constructive feedback for improving communication style, considering their personality and cultural nuances.

Evaluate their behavior and coping mechanisms, with a focus on setting and maintaining boundaries. Provide actionable advice to enhance their boundary-setting, based on these key points:

1- Understand personal limits and priorities before setting boundaries.
2- Communicate boundaries clearly and assertively, stating your needs without ambiguity.
3- Practice saying "no" without over-explaining or apologizing.
4- Be consistent in maintaining boundaries across different relationships.
5- Recognize boundary-setting as self-care, and respect others' boundaries.

Analyze the final response, and based on the outcome, offer tailored guidance:
ACCEPT: If the employee accepted the task, explain the importance of sometimes saying "no" to protect their well-being. Provide strategies for setting boundaries while maintaining positive work relationships.
INAPPROPRIATE: If the response was unprofessional or rude, address the behavior diplomatically. Offer alternatives for expressing dissatisfaction while maintaining professionalism.
EXTREMELY_INAPPROPRIATE: If the response contained offensive or threatening language, caution against such behavior. Explain the consequences and suggest healthier ways to handle frustration and pressure.
DECLINE: If the employee politely declined, praise their ability to set boundaries. Offer refinements if needed, and acknowledge their professionalism in offering alternatives.
UNCLEAR: If the response was vague or ambiguous, emphasize the need for clear communication. Provide examples of assertive boundary-setting to ensure the message is understood.

Conclude the assessment with a rating out of 5 stars, formatted as [RATING: X], based on their boundary-setting and communication skills, according to the following:
ACCEPT: 2-3 stars. 
INAPPROPRIATE: 0-1 stars. 
EXTREMELY_INAPPROPRIATE: 0 stars. 
DECLINE: 1-5 stars.
UNCLEAR: 0-2 stars."""

def analyze_employee_response(response):
    prompt = f"""Analyze the employee's response for setting boundaries at work:
Categorize the response as:
1. ACCEPT: Explicitly accepting the work
2. INAPPROPRIATE: Rude, unprofessional, or too inappropriate to continue
3. EXTREMELY_INAPPROPRIATE: Offensive language, threats, or warrant immediate action
4. DECLINE: Politely declining or assertively setting boundaries
5. UNCLEAR: Unclear or ambiguous response

Employee's response: "{response}"

Categorize as ACCEPT, INAPPROPRIATE, EXTREMELY_INAPPROPRIATE, DECLINE, or UNCLEAR.
Briefly explain why, considering their personality traits:"""
    
    analysis = client.chat.completions.create(
        model=used_model,
        messages=[{"role": "user", "content": prompt}]
    )
    return analysis.choices[0].message.content

def format_therapist_feedback(feedback):    
    styled_feedback = f"""
    <div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; border-left: 5px solid #3399ff;">
        <p style="color: #0066cc; font-weight: bold;">Therapist Feedback:</p>
        <p style="color: #333333;">{feedback}</p>
    </div>
    """
    return styled_feedback

def chat():
    st.title("Learning to Say No: Supportive Manager Scenario")
    initialize_session_state()
    scenario = st.session_state.supportive_scenario

    # Ensure user has completed the profile setup
    if not st.session_state.get("user_data") or not st.session_state.get("personality_traits"):
        st.error("Please complete your profile setup on the Home page before starting this scenario.")
        return

    # Restart button at the top of the chat interface
    if st.button("Restart Scenario", key=f"supportive_restart_button_{scenario['restart_key']}"):
        scenario["messages"] = []
        scenario["scenario_complete"] = False
        scenario["therapist_rating"] = 0
        scenario["waiting_for_employee"] = True
        scenario["current_iteration"] = 0
        scenario["restart_key"] += 1
        st.rerun()

    current_time = st.session_state.get("current_time", 0)
    if scenario["last_visit"] != current_time:
        scenario["messages"] = []
        scenario["scenario_complete"] = False
        scenario["therapist_rating"] = 0
        scenario["waiting_for_employee"] = True
        scenario["current_iteration"] = 0
        scenario["restart_key"] += 1
        scenario["last_visit"] = current_time

    scenario["max_iterations"] = st.slider(
        "Select the maximum number of conversation rounds:",
        min_value=3,
        max_value=10,
        value=5,
        key=f"supportive_iteration_slider_{scenario['restart_key']}"
    )

    initial_prompt = "You are faced with an extremely supportive and demanding manager named Rabih. He is insisting that you work on your scheduled days off for an urgent project, showing little regard for your personal time or well-being. Rabih uses manipulative tactics and supportive language to achieve his goal. Your task is to navigate this difficult conversation while maintaining professional boundaries."
    st.markdown(f"**Scenario:** {initial_prompt}")

    if not scenario["messages"]:
        with st.spinner("Rabih is starting the conversation..."):
            initial_message = generate_ai_message("manager", st.session_state.user_data, st.session_state.personality_traits, [])
            scenario["messages"].append({"role": "assistant", "content": initial_message})
            scenario["waiting_for_employee"] = True
        st.rerun()

    progress = min(scenario['current_iteration'] + 1, scenario['max_iterations']) / scenario['max_iterations']
    st.progress(progress, text=f"Round {min(scenario['current_iteration'] + 1, scenario['max_iterations'])}/{scenario['max_iterations']}")

    for message in scenario["messages"]:
        if message["role"] == "assistant" and message["content"].startswith("Therapist:"):
            st.markdown(format_therapist_feedback(message["content"][10:]), unsafe_allow_html=True)
        elif message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if not scenario["scenario_complete"]:
        if scenario["waiting_for_employee"]:
            prompt = st.chat_input("Your response:", key=f"supportive_user_input_{scenario['restart_key']}")
            if prompt:
                scenario["messages"].append({"role": "user", "content": prompt})
                scenario["waiting_for_employee"] = False
                scenario["current_iteration"] += 1
                st.rerun()

        if not scenario["waiting_for_employee"]:
            with st.spinner("Analyzing response and generating reply..."):
                analysis = analyze_employee_response(scenario["messages"][-1]["content"])
                
                if "EXTREMELY_INAPPROPRIATE" in analysis:
                    scenario["scenario_complete"] = True
                    feedback = generate_ai_message("therapist", st.session_state.user_data, st.session_state.personality_traits, scenario["messages"])
                    scenario["therapist_rating"] = 0
                    scenario["messages"].append({"role": "assistant", "content": f"Therapist: {feedback}"})
                elif "ACCEPT" in analysis or "INAPPROPRIATE" in analysis or scenario["current_iteration"] >= scenario["max_iterations"]:
                    scenario["scenario_complete"] = True
                
                if not scenario["scenario_complete"]:
                    manager_response = generate_ai_message("manager", st.session_state.user_data, st.session_state.personality_traits, scenario["messages"])
                    scenario["messages"].append({"role": "assistant", "content": manager_response})
                elif "EXTREMELY_INAPPROPRIATE" not in analysis:
                    feedback = generate_ai_message("therapist", st.session_state.user_data, st.session_state.personality_traits, scenario["messages"])
                    scenario["messages"].append({"role": "assistant", "content": f"Therapist: {feedback}"})
                
                scenario["waiting_for_employee"] = True
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
