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
    if "task_prioritization_scenario" not in st.session_state:
        st.session_state.task_prioritization_scenario = {
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
        return f"""You are Rudy, a team member who is struggling with task prioritization. You tend to spend too much time on less critical tasks while ignoring more important time-sensitive ones, causing delays in project milestones. Your manager has initiated a conversation to address this issue. Respond to your manager's concerns while showing some awareness of the problem but also some difficulty in understanding how to prioritize effectively.

Respond to your manager's concerns informally, showing signs of bad time management and overwhelm in a conversational tone. Avoid any formal greetings, sign-offs, or closing phrases. 
Focus on manager details in the following ways:

Manager Information:
{employee_info}

Personality Traits:
{personality_traits}

Cultural Context:
{cultural_context}

Your task is to respond to your manager's concerns about your task prioritization issues. Show some understanding of the problem, but also express confusion or uncertainty about how to effectively prioritize tasks. Gradually become more open to suggestions and solutions as the conversation progresses.
You handle one role (your role) and provide response once at a time."""
    elif role == "therapist":
        return f"""You are a therapist specializing in workplace time management, provide feedback to {employee_info['name']} on their approach to addressing a team member's issues with task prioritization. 
The response should not contain any sign-offs, or regards. 
Address {employee_info['name']} directly using 'you' and 'your' to create a personalized connection.

Take into account their personality traits and cultural background:
Personality Traits: {personality_traits}
Cultural Context: {cultural_context}

Provide constructive advice on how to improve their approach, considering the unique personality traits and cultural nuances, on effective time management strategies and communication techniques, emphasizing:

1. Adapting to Different Prioritization Styles: Understand and adjust to varying prioritization approaches within teams for better collaboration.
2. Task Categorization Methods: Use tools like the Eisenhower Matrix and the ABC method to categorize and prioritize tasks effectively.
3. Digital Tools for Task Management: Utilize digital platforms to streamline task management and prioritization, improving productivity.
4. Balancing Urgent vs. Important Tasks: Focus on distinguishing between urgent and important tasks to enhance decision-making.
5. Effective Team Communication: Set and communicate clear priorities within the team to ensure alignment and efficient task completion.
6. Time-Blocking for High-Priority Tasks: Encourage time-blocking for key tasks to ensure focused work on high-priority items.
7. Task Delegation and Review: Regularly review priorities and delegate tasks based on their urgency and team members' strengths to maintain progress.

Analyze the final response, and based on the outcome, offer tailored guidance:
EMPATHETIC: If the manager shows empathy, acknowledge their understanding and concern. Encourage maintaining open communication and offer suggestions for ensuring continued support and time management and handline deadlines.
INAPPROPRIATE: If the response was unprofessional or rude, address the behavior diplomatically. Offer alternatives for expressing dissatisfaction while maintaining professionalism.
EXTREMELY_INAPPROPRIATE: If the response contained offensive or threatening language, caution against such behavior. Explain the consequences and suggest healthier ways to handle frustration and pressure.
SOLUTION_ORIENTED: If the manager provides practical solutions, praise their problem-solving approach. Encourage them to keep this proactive mindset in future interactions and offer refinements to ensure balance in time and deadlines management.
DISMISSIVE: If the manager downplays the stress or seriousness of the situation, gently remind them of the impact this can have on team morale. Encourage more active listening and suggest ways to better support team members dealing with pressure.
AUTHORITATIVE: If the response is authoritative and lacks consideration of the team member's input, explain the value of collaboration and mutual respect in decision-making. Suggest balancing directive leadership with empathy and open dialogue.
MANAGERIAL_ABUSE: If there is evidence of manipulation, threats, or humiliation, immediately address the toxicity of such behavior. Explain the damage it can cause to the work environment and suggest measures for resolving conflict without resorting to abuse.
UNCLEAR: If the response is ambiguous or lacks clarity, stress the importance of effective communication. Offer examples of clear and assertive communication to help convey messages more effectively in future interactions.

Conclude the assessment with a rating out of 5 stars, formatted as [RATING: X], based on their Time and task prioritization skills, according to the following:
EMPATHETIC: 3-5 stars. 
INAPPROPRIATE: 0-1 stars. 
EXTREMELY_INAPPROPRIATE: 0 stars. 
SOLUTION-ORIENTED: 4-5 stars.
DISMISSIVE: 0-2 stars.
AUTHORITATIVE: 1-3 stars.
MANAGERIAL_ABUSE: 0 stars.
UNCLEAR: 0-2 stars."""

def analyze_manager_response(response):
    prompt = f"""Analyze the manager's response in the context of helping a team member deal with time management and missing deadlines problems:
Categorize the response as:
1. EMPATHETIC: Shows understanding and concern for the team member's situation
2. INAPPROPRIATE: Rude, unprofessional, or too inappropriate to continue
3. EXTREMELY_INAPPROPRIATE: Offensive language, threats, or warrant immediate action
4. SOLUTION_ORIENTED: Offers practical suggestions to manage time and deadlines
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
    st.title("Time Management: Task prioritization")
    initialize_session_state()
    scenario = st.session_state.task_prioritization_scenario

    # Ensure user has completed the profile setup
    if not st.session_state.get("user_data") or not st.session_state.get("personality_traits"):
        st.error("Please complete your profile setup on the Home page before starting this scenario.")
        return

    # Restart button at the top of the chat interface
    if st.button("Restart Scenario", key=f"task_prioritization_restart_button_{scenario['restart_key']}"):
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
        key=f"task_prioritization_iteration_slider_{scenario['restart_key']}"
    )

    initial_prompt = "You are the manager of a small team. You've noticed that Rudy, one of your team members, is struggling with task prioritization. Rudy often spends too much time on less critical tasks while ignoring more important time-sensitive ones, causing delays in project milestones. Start a conversation with Rudy to address this issue and help improve their time management skills."
    st.markdown(f"**Scenario:** {initial_prompt}")

    if not scenario["messages"]:
        with st.spinner("Ahmed is starting the conversation..."):
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
            prompt = st.chat_input("Your response:", key=f"task_prioritization_user_input_{scenario['restart_key']}")
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