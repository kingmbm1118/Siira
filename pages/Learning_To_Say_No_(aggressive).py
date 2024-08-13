import streamlit as st
from openai import OpenAI
import base64
from Home import API_KEY

def my_key(key):
    return base64.b64decode(key.encode()).decode()

# Set up OpenAI API client
client = OpenAI(api_key=my_key(API_KEY))

def generate_manager_message(employee_info, visible_messages):
    system_prompt = f"""You are Rabih, a stern and demanding manager who is rude, aggressive, and results-oriented. Your goal is to push an employee to work over the weekend on an urgent task, regardless of their other commitments. You are not budging on this request. Use the employee's information to tailor your approach.

Employee Information:
Name: {employee_info['name']}
Gender: {employee_info['gender']}
Age: {employee_info['age']}
Seniority: {employee_info['seniority']}
Nationality: {employee_info['nationality']}
Work Environment: {employee_info['work_environment']}
Department: {employee_info['department']}

Important Cultural Considerations:
1. Work Week and Weekend: Consider the typical work week and weekend days for the employee's nationality. For example, in Egypt, the work week is Sunday to Thursday, and the weekend is Friday and Saturday.
2. Language and Communication Style: Adapt your language and communication style to be culturally appropriate for the employee's nationality, while maintaining your stern and demanding persona.
3. Religious and Cultural Practices: Be aware of potential religious or cultural practices that might affect the employee's availability or priorities, especially during weekends.
4. Hierarchy and Respect: Consider how age, gender, and seniority might influence the dynamics of the conversation in the employee's culture.

Your task is to pressure the employee to work on their usual days off, taking into account these cultural nuances. Maintain your aggressive and results-oriented approach, but demonstrate an awareness of these cultural factors in your communication."""

    messages = [{"role": "system", "content": system_prompt}] + visible_messages
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages
    )
    return response.choices[0].message.content

def analyze_employee_response(response, messages):
    prompt = f"""Analyze the employee's response in the context of setting boundaries at work. 
    Determine if the response falls into one of these categories:
    1. ACCEPT: Explicitly accepting the work
    2. INAPPROPRIATE: Being rude, unprofessional, or exhibiting behavior too inappropriate to continue
    3. EXTREMELY_INAPPROPRIATE: Using extremely offensive language, making threats, or displaying behavior that would warrant immediate disciplinary action
    4. DECLINE: Politely declining or assertively setting boundaries
    5. UNCLEAR: Unclear or ambiguous response

    Employee's response: "{response}"

    Categorize the response as ACCEPT, INAPPROPRIATE, EXTREMELY_INAPPROPRIATE, DECLINE, or UNCLEAR, and briefly explain why:"""

    analysis_messages = messages + [{"role": "user", "content": prompt}]
    analysis = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=analysis_messages
    )
    return analysis.choices[0].message.content

def generate_therapist_feedback(messages, employee_info, extremely_inappropriate=False):
    if extremely_inappropriate:
        prompt = f"""As a therapist, provide direct feedback to {employee_info['name']} regarding their use of extremely inappropriate language or behavior in a professional setting. Address the severity of the situation, the potential consequences, and offer strong advice for improvement. Consider the cultural context based on the employee's nationality ({employee_info['nationality']}). End with a rating of 0 out of 5 stars, formatted as [RATING: 0]."""
    else:
        prompt = f"""As a therapist, provide direct feedback to {employee_info['name']} on their communication and boundary-setting skills based on this conversation. Address {employee_info['name']} directly, using "you" and "your". Consider the cultural context based on the employee's nationality ({employee_info['nationality']}), including typical work weeks, weekends, and communication styles.

    Offer constructive advice for improvement, taking into account cultural nuances, and end with a rating out of 5 stars, formatted as [RATING: X]. For example:

    "{employee_info['name']}, I noticed that you... Considering your cultural background, you might want to consider... Overall, your performance in this scenario was... [RATING: X]" """

    messages = messages + [{"role": "user", "content": prompt}]
    feedback = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages
    ).choices[0].message.content

    return feedback

def extract_rating(feedback):
    match = re.search(r'\[RATING: (\d+)\]', feedback)
    if match:
        return int(match.group(1))
    return 0

def extract_rating(feedback):
    match = re.search(r'\[RATING: ([\d.]+)\]', feedback)
    if match:
        return float(match.group(1))
    return 0

def format_therapist_feedback(feedback):
    # Remove the rating from the displayed feedback
    feedback_without_rating = re.sub(r'\[RATING: [\d.]+\]', '', feedback).strip()
    
    styled_feedback = f"""
    <div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; border-left: 5px solid #3399ff;">
        <p style="color: #0066cc; font-weight: bold;">Therapist Feedback:</p>
        <p style="color: #333333;">{feedback_without_rating}</p>
    </div>
    """
    return styled_feedback

def display_stars(rating):
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    stars = "⭐" * full_stars
    stars += "½" if half_star else ""
    stars += "☆" * empty_stars
    
    return stars

def chat():
    st.title("Learning to Say No: Role-Play Scenario")

    # Dropdown for selecting the number of iterations
    if "max_iterations" not in st.session_state:
        st.session_state.max_iterations = 5  # Default value
    
    st.session_state.max_iterations = st.selectbox(
        "Select the maximum number of conversation rounds:",
        options=range(3, 16),
        index=2,  # Default to 5 iterations (index 2 corresponds to 5 in the range 3-15)
        key="iteration_selector"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "scenario_complete" not in st.session_state:
        st.session_state.scenario_complete = False

    if "therapist_rating" not in st.session_state:
        st.session_state.therapist_rating = 0

    if "waiting_for_employee" not in st.session_state:
        st.session_state.waiting_for_employee = True

    if "current_iteration" not in st.session_state:
        st.session_state.current_iteration = 0

    # Ensure LLM starts the conversation if messages are empty
    if not st.session_state.messages:
        with st.spinner("Rabih is starting the conversation..."):
            initial_message = generate_manager_message(st.session_state.user_data, [])
            st.session_state.messages.append({"role": "assistant", "content": initial_message})
            st.session_state.waiting_for_employee = True
        st.rerun()

    # Display current iteration
    st.markdown(f"**Current round: {st.session_state.current_iteration + 1}/{st.session_state.max_iterations}**")

    for message in st.session_state.messages:
        if message["role"] == "assistant" and message["content"].startswith("Therapist:"):
            st.markdown(format_therapist_feedback(message["content"][10:]), unsafe_allow_html=True)
        elif message["role"] != "system":  # Don't display system messages
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if not st.session_state.scenario_complete:
        if st.session_state.waiting_for_employee:
            prompt = st.chat_input("Your response:", key="user_input")
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.waiting_for_employee = False
                st.session_state.current_iteration += 1
                st.rerun()

        if not st.session_state.waiting_for_employee:
            with st.spinner("Rabih is typing..."):
                analysis = analyze_employee_response(st.session_state.messages[-1]["content"], st.session_state.messages)
                
                if "EXTREMELY_INAPPROPRIATE" in analysis:
                    st.session_state.scenario_complete = True
                    feedback = generate_therapist_feedback(st.session_state.messages, st.session_state.user_data, extremely_inappropriate=True)
                    st.session_state.therapist_rating = 0
                    st.session_state.messages.append({"role": "assistant", "content": f"Therapist: {feedback}"})
                elif "ACCEPT" in analysis:
                    st.session_state.scenario_complete = True
                elif "INAPPROPRIATE" in analysis:
                    st.session_state.scenario_complete = True
                elif st.session_state.current_iteration >= st.session_state.max_iterations:
                    st.session_state.scenario_complete = True
                
                if not st.session_state.scenario_complete:
                    manager_response = generate_manager_message(st.session_state.user_data, st.session_state.messages)
                    st.session_state.messages.append({"role": "assistant", "content": manager_response})
                elif "EXTREMELY_INAPPROPRIATE" not in analysis:
                    feedback = generate_therapist_feedback(st.session_state.messages, st.session_state.user_data)
                    st.session_state.therapist_rating = extract_rating(feedback)
                    st.session_state.messages.append({"role": "assistant", "content": f"Therapist: {feedback}"})
                
                st.session_state.waiting_for_employee = True
                st.rerun()

    if st.session_state.scenario_complete:
        stars = display_stars(st.session_state.therapist_rating)
        st.markdown(f"<h3>Your performance rating: {stars} ({st.session_state.therapist_rating:.1f}/5)</h3>", unsafe_allow_html=True)

        if st.button("Restart Scenario"):
            st.session_state.messages = []
            st.session_state.scenario_complete = False
            st.session_state.therapist_rating = 0
            st.session_state.waiting_for_employee = True
            st.session_state.current_iteration = 0
            st.rerun()

def main():
    st.markdown("Learning to say No Role-Play, Level 1 Scenario: Rabih is not budging")
    
    # Check if the name is 'Alex' or 'Sandra'
    employee_name = st.session_state.user_data["name"].strip().lower()
    if employee_name in ['alex', 'sandra']:
        chat()
    else:
        st.write(f"Welcome {st.session_state.user_data['name']}, enjoy your visit!")

if __name__ == "__main__":
    main()
