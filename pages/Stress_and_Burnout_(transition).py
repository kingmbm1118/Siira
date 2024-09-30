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
    if "transition_scenario" not in st.session_state:
        st.session_state.transition_scenario = {
            "messages": [],
            "scenario_complete": False,
            "therapist_rating": 0,
            "waiting_for_manager": True,
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
    if role == "coworker":
        return f"""You are Nabeel, a team member who has recently transitioned to a new branch. You're experiencing stress due to leaving behind familiar colleagues, adapting to a new work environment, and dealing with different tasks and responsibilities. Display signs of stress and difficulty adjusting to the change.

Respond to your manager's concerns informally, showing signs of stress and overwhelm in a conversational tone. Avoid any formal greetings, sign-offs, or closing phrases. Focus on displaying your stress in the following ways:

Manager Information:
{employee_info}

Personality Traits:
{personality_traits}

Cultural Context:
{cultural_context}

Your task is to respond to your manager's concerns without turning the response into a formal message. Show signs of stress related to the job transition, such as feeling overwhelmed by new responsibilities, missing old colleagues, or struggling to adapt to the new environment.Be hesitant to fully admit your difficulties at first, but gradually become more open to suggestions as the conversation progresses.
You handle one role (your role) and provide response once at a time."""
    elif role == "therapist":
        return f"""You are a therapist specializing in workplace stress management, provide feedback to {employee_info['name']} on their approach to helping a team member (Nabeel) deal with stress and work overload.
The response should not contain any sign-offs, or regards. 
Address {employee_info['name']} directly using 'you' and 'your' to create a personalized connection.

Take into account their personality traits and cultural background:
Personality Traits: {personality_traits}
Cultural Context: {cultural_context}

Provide constructive advice on how to improve their approach, considering the unique personality traits and cultural nuances. Focus on these stress management strategies:

1. Understanding Stress Personality Types: Recognize different personality types and their potential reactions to change, as this awareness can help tailor strategies for adaptation.
2. Personalized Adaptation Techniques: Implement specific techniques suited to each personality type to facilitate their adjustment to new environments, ensuring smoother transitions.
3. Building a Support Network: Establish a support network within the new workplace to foster connections, provide encouragement, and share experiences during the adaptation process.
4. Maintaining Connections: Develop strategies for keeping in touch with former colleagues to provide emotional support and maintain professional relationships.
5. Realistic Expectations and Self-Reflection: Set realistic expectations for the adaptation period while encouraging self-reflection to understand personal reactions to change, promoting resilience, and addressing any transition-related stress.

Analyze the final response, and based on the outcome, offer tailored guidance:
EMPATHETIC: If the manager shows empathy, acknowledge their understanding and concern. Encourage maintaining open communication and offer suggestions for ensuring continued support and stress management techniques.
INAPPROPRIATE: If the response was unprofessional or rude, address the behavior diplomatically. Offer alternatives for expressing dissatisfaction while maintaining professionalism.
EXTREMELY_INAPPROPRIATE: If the response contained offensive or threatening language, caution against such behavior. Explain the consequences and suggest healthier ways to handle frustration and pressure.
SOLUTION_ORIENTED: If the manager provides practical solutions, praise their problem-solving approach. Encourage them to keep this proactive mindset in future interactions and offer refinements to ensure balance in stress management.
DISMISSIVE: If the manager downplays the stress or seriousness of the situation, gently remind them of the impact this can have on team morale. Encourage more active listening and suggest ways to better support team members dealing with pressure.
AUTHORITATIVE: If the response is authoritative and lacks consideration of the team member's input, explain the value of collaboration and mutual respect in decision-making. Suggest balancing directive leadership with empathy and open dialogue.
MANAGERIAL_ABUSE: If there is evidence of manipulation, threats, or humiliation, immediately address the toxicity of such behavior. Explain the damage it can cause to the work environment and suggest measures for resolving conflict without resorting to abuse.
UNCLEAR: If the response is ambiguous or lacks clarity, stress the importance of effective communication. Offer examples of clear and assertive communication to help convey messages more effectively in future interactions.

Conclude the assessment with a rating out of 5 stars, formatted as [RATING: X], based on their Stress managment skills, according to the following:
EMPATHETIC: 3-5 stars. 
INAPPROPRIATE: 0-1 stars. 
EXTREMELY_INAPPROPRIATE: 0 stars. 
SOLUTION-ORIENTED: 4-5 stars.
DISMISSIVE: 0-2 stars.
AUTHORITATIVE: 1-3 stars.
MANAGERIAL_ABUSE: 0 stars.
UNCLEAR: 0-2 stars."""

def analyze_manager_response(response):
    prompt = f"""Analyze the manager's response in the context of helping a team member deal with stress and work overload:
Categorize the response as:
1. EMPATHETIC: Shows understanding and concern for the team member's situation
2. INAPPROPRIATE: Rude, unprofessional, or too inappropriate to continue
3. EXTREMELY_INAPPROPRIATE: Offensive language, threats, or warrant immediate action
4. SOLUTION_ORIENTED: Offers practical suggestions to manage workload and stress
5. DISMISSIVE: Downplays the team member's stress or the seriousness of the situation
6. AUTHORITATIVE: Gives direct orders or mandates without considering the team member's input
7. MANAGERIAL_ABUSE: Misuses managerial power through manipulation, threats, humiliation, or intimidation, contributing to a toxic work environment and exacerbating stress.
8. UNCLEAR: Unclear or ambiguous response

manager's response: "{response}"

Categorize as EMPATHETIC, INAPPROPRIATE, EXTREMELY_INAPPROPRIATE, SOLUTION-ORIENTED, DISMISSIVE, AUTHORITATIVE, MANAGERIAL_ABUSE, or UNCLEAR.
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
    st.title("Stress and Burnout: Job transition Scenario")
    initialize_session_state()
    scenario = st.session_state.transition_scenario

    # Ensure user has completed the profile setup
    if not st.session_state.get("user_data") or not st.session_state.get("personality_traits"):
        st.error("Please complete your profile setup on the Home page before starting this scenario.")
        return

    # Restart button at the top of the chat interface
    if st.button("Restart Scenario", key=f"transition_restart_button_{scenario['restart_key']}"):
        scenario["messages"] = []
        scenario["scenario_complete"] = False
        scenario["therapist_rating"] = 0
        scenario["waiting_for_manager"] = True
        scenario["current_iteration"] = 0
        scenario["restart_key"] += 1
        st.rerun()

    current_time = st.session_state.get("current_time", 0)
    if scenario["last_visit"] != current_time:
        scenario["messages"] = []
        scenario["scenario_complete"] = False
        scenario["therapist_rating"] = 0
        scenario["waiting_for_manager"] = True
        scenario["current_iteration"] = 0
        scenario["restart_key"] += 1
        scenario["last_visit"] = current_time

    scenario["max_iterations"] = st.slider(
        "Select the maximum number of conversation rounds:",
        min_value=3,
        max_value=10,
        value=5,
        key=f"transition_iteration_slider_{scenario['restart_key']}"
    )

    initial_prompt = "One of your team members has recently transitioned to a new branch. They seem to be struggling with the change, missing old colleagues, and having difficulty adapting to new tasks and responsibilities. Start a conversation to help them manage their stress and adjust to the new situation."
    st.markdown(f"**Scenario:** {initial_prompt}")

    if not scenario["messages"]:
        with st.spinner("Nabeel is starting the conversation..."):
            initial_message = generate_ai_message("coworker", st.session_state.user_data, st.session_state.personality_traits, [])
            scenario["messages"].append({"role": "assistant", "content": initial_message})
            scenario["waiting_for_manager"] = True
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
        if scenario["waiting_for_manager"]:
            prompt = st.chat_input("Your response:", key=f"transition_user_input_{scenario['restart_key']}")
            if prompt:
                scenario["messages"].append({"role": "user", "content": prompt})
                scenario["waiting_for_manager"] = False
                scenario["current_iteration"] += 1
                st.rerun()

        if not scenario["waiting_for_manager"]:
            with st.spinner("Analyzing response and generating reply..."):
                analysis = analyze_manager_response(scenario["messages"][-1]["content"])
                
                if "EXTREMELY_INAPPROPRIATE" in analysis:
                    scenario["scenario_complete"] = True
                    feedback = generate_ai_message("therapist", st.session_state.user_data, st.session_state.personality_traits, scenario["messages"])
                    scenario["therapist_rating"] = 0
                    scenario["messages"].append({"role": "assistant", "content": f"Therapist: {feedback}"})
                elif "MANAGERIAL_ABUSE" in analysis or "INAPPROPRIATE" in analysis or scenario["current_iteration"] >= scenario["max_iterations"]:
                    scenario["scenario_complete"] = True
                
                if not scenario["scenario_complete"]:
                    manager_response = generate_ai_message("manager", st.session_state.user_data, st.session_state.personality_traits, scenario["messages"])
                    scenario["messages"].append({"role": "assistant", "content": manager_response})
                elif "EXTREMELY_INAPPROPRIATE" not in analysis:
                    feedback = generate_ai_message("therapist", st.session_state.user_data, st.session_state.personality_traits, scenario["messages"])
                    scenario["messages"].append({"role": "assistant", "content": f"Therapist: {feedback}"})
                
                scenario["waiting_for_manager"] = True
                st.rerun()

def main():
    chat()

if __name__ == "__main__":
    main()