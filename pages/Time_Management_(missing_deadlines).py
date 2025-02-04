import streamlit as st
from openai import OpenAI
import base64
from Home import API_KEY
from cultural_considerations import get_cultural_context

# Update model name
used_model = "gpt-4o-mini"

def my_key(key):
    return base64.b64decode(key.encode()).decode()

client = OpenAI(api_key=my_key(API_KEY))

def initialize_session_state():
    if "missing_deadlines_scenario" not in st.session_state:
        st.session_state.missing_deadlines_scenario = {
            "messages": [],
            "scenario_complete": False,
            "therapist_rating": 0,
            "waiting_for_manager": True,
            "current_iteration": 0,
            "max_iterations": 3,
            "restart_key": 0,
            "last_visit": None,
            "completion_reason": None
        }

def generate_ai_message(role, employee_info, personality_profile, visible_messages):
    cultural_context = get_cultural_context(employee_info['nationality'])
    system_prompt = create_system_prompt(role, employee_info, personality_profile, cultural_context)
    messages = [{"role": "system", "content": system_prompt}] + visible_messages
    response = client.chat.completions.create(
        model=used_model,
        messages=[{"role": m["role"], "content": m["content"]} for m in messages]
    )
    return response.choices[0].message.content

def create_system_prompt(role, employee_info, personality_profile, cultural_context):
    # Extract personality levels from the new profile structure
    personality_traits = {trait: data["level"] for trait, data in personality_profile.items() 
                         if trait != "recommendations"}
    
    if role == "manager":
        return f"""You are Ahmad, consistently missing deadlines and requesting extensions.

Employee Traits:
- Missing project deadlines
- Requesting frequent extensions
- Impacting team dependencies
- Showing some awareness
- Reluctant to admit fault
- Struggling with time management

Manager Information:
{employee_info}

Personality Profile:
{personality_traits}

Cultural Context:
{cultural_context}

Your responses should:
1. Show partial awareness
2. Make excuses initially
3. Defend time management
4. Express overwhelm
5. Acknowledge impact gradually
6. Be open to suggestions

Guidelines:
- Start defensive
- Gradually accept responsibility
- Show willingness to improve
- Maintain professionalism
- Express genuine concerns
- Demonstrate learning potential"""
    elif role == "therapist":
        return f"""As a therapist specializing in time management, provide feedback to {employee_info['name']} on addressing deadline issues.

Consider their background:
Personality Profile: {personality_traits}
Cultural Context: {cultural_context}

Focus feedback on:
1. Time management skills
2. Project planning
3. Communication strategies
4. Team impact awareness
5. Accountability development
6. Resource utilization

Evaluate their response for:
1. Solution focus
2. Supportive approach
3. Clear expectations
4. Resource provision
5. Follow-up planning
6. Team consideration

Categorize responses as:
EMPATHETIC: Shows understanding with accountability
INAPPROPRIATE: Unprofessional approach
EXTREMELY_INAPPROPRIATE: Hostile behavior
SOLUTION_ORIENTED: Provides practical help
DISMISSIVE: Ignores the problem
AUTHORITATIVE: Commands without support
MANAGERIAL_ABUSE: Uses punitive measures
UNCLEAR: Vague communication

Rate performance [RATING: X]:
EMPATHETIC: 3-5 stars
INAPPROPRIATE: 0-1 stars
EXTREMELY_INAPPROPRIATE: 0 stars
SOLUTION_ORIENTED: 4-5 stars
DISMISSIVE: 0-2 stars
AUTHORITATIVE: 1-3 stars
MANAGERIAL_ABUSE: 0 stars
UNCLEAR: 0-2 stars"""

def analyze_manager_response(response):
    prompt = f"""Analyze this managerial response to missed deadlines:

Response to analyze: "{response}"

Evaluate against:
1. EMPATHETIC: Shows understanding with accountability
2. INAPPROPRIATE: Shows unprofessional behavior
3. EXTREMELY_INAPPROPRIATE: Shows hostility
4. SOLUTION_ORIENTED: Provides practical help
5. DISMISSIVE: Ignores the problem
6. AUTHORITATIVE: Commands without support
7. MANAGERIAL_ABUSE: Uses punitive measures
8. UNCLEAR: Shows vague communication

Consider:
- Support quality
- Solution practicality
- Accountability balance
- Resource provision
- Follow-up planning
- Team consideration

Format: Category + detailed explanation"""
    
    analysis = client.chat.completions.create(
        model=used_model,
        messages=[{"role": "user", "content": prompt}]
    )
    return analysis.choices[0].message.content

def format_chat_message(role, content):
    if role == "assistant" and content.startswith("Therapist:"):
        return format_therapist_feedback(content[10:])
    
    colors = {
        "assistant": "#f0f2f6",  # Light gray for AI
        "user": "#e1f5fe"        # Light blue for user
    }
    
    icon = "🧑‍💼" if role == "assistant" else "👤"
    name = "Ahmad" if role == "assistant" and not content.startswith("Therapist:") else "You"
    
    styled_message = f"""
    <div style="background-color: {colors.get(role, '#ffffff')}; 
                padding: 15px; 
                border-radius: 10px; 
                margin: 5px 0; 
                border-left: 5px solid {'#2196f3' if role == 'user' else '#9e9e9e'}">
        <p style="margin: 0 0 5px 0; 
                  color: var(--text-color, #666666); 
                  font-size: 14px;">
            {icon} {name}
        </p>
        <p style="margin: 0; 
                  color: var(--text-color, #333333);">
            {content}
        </p>
    </div>
    """
    return styled_message

def format_therapist_feedback(feedback):    
    styled_feedback = f"""
    <div style="background-color: var(--card-background, #e8f5e9); 
                padding: 15px; 
                border-radius: 10px; 
                margin: 10px 0; 
                border-left: 5px solid var(--primary-color, #4caf50);">
        <p style="color: var(--primary-color, #1b5e20); 
                  font-weight: bold; 
                  margin-bottom: 10px;">
            🧑‍⚕️ Therapist Feedback
        </p>
        <p style="color: var(--text-color, #333333); 
                  margin: 0; 
                  line-height: 1.5;">
            {feedback}
        </p>
    </div>
    """
    return styled_feedback

def display_scenario_header():
    st.markdown("""
    <div style="background-color: var(--card-background, #f8f9fa); 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 20px; 
                border-left: 5px solid var(--primary-color, #ff5722);">
        <h1 style="color: var(--primary-color, #ff5722); 
                   margin-bottom: 15px;">
            Time Management
        </h1>
        <h3 style="color: var(--text-color, #495057); 
                   margin-bottom: 15px;">
            Scenario: Addressing Missed Deadlines
        </h3>
        <p style="color: var(--text-color, #6c757d); 
                  font-size: 16px; 
                  line-height: 1.6;">
            Your team member, Ahmad, consistently misses deadlines and requests extensions, impacting team deliverables. 
            Your role is to:
            • Address the pattern
            • Understand root causes
            • Develop solutions
            • Set clear expectations
            • Provide necessary support
        </p>
        <div style="background-color: var(--card-background, #fbe9e7); 
                    padding: 10px; 
                    border-radius: 5px; 
                    margin-top: 10px;">
            <p style="color: var(--text-color, #d84315); 
                      margin: 0;">
                💡 Key Focus: Balance accountability with support while maintaining team productivity
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_completion_message(scenario):
    if not scenario["completion_reason"]:
        return
    
    messages = {
        "max_iterations": "Maximum conversation rounds reached. The conversation has concluded.",
        "inappropriate": "The conversation has ended due to inappropriate responses.",
        "extremely_inappropriate": "The conversation has been terminated due to extremely inappropriate behavior.",
        "managerial_abuse": "The conversation has been terminated due to inappropriate managerial behavior.",
        "solution": "You've successfully addressed the deadline issues with support and accountability.",
        "success": "You've successfully completed this scenario!"
    }
    
    colors = {
        "max_iterations": "#ff9800",
        "inappropriate": "#f44336",
        "extremely_inappropriate": "#d32f2f",
        "managerial_abuse": "#d32f2f",
        "solution": "#4caf50",
        "success": "#4caf50"
    }
    
    message = messages.get(scenario["completion_reason"], "The conversation has ended.")
    color = colors.get(scenario["completion_reason"], "#9e9e9e")
    
    st.markdown(f"""
    <div style="background-color: {color}20; 
                padding: 15px; 
                border-radius: 10px; 
                margin: 20px 0; 
                border-left: 5px solid {color};">
        <p style="color: {color}; 
                  font-weight: bold; 
                  margin: 0;">
            {message}
        </p>
    </div>
    """, unsafe_allow_html=True)

def chat():
    display_scenario_header()
    initialize_session_state()
    scenario = st.session_state.missing_deadlines_scenario

    # Profile check
    if not st.session_state.get("user_data") or not st.session_state.get("personality_profile"):
        st.error("⚠️ Please complete your profile and personality assessment on the Home page first.")
        return

    # Control panel
    col1, col2 = st.columns([2,1])
    with col1:
        if st.button("🔄 Restart Scenario", key=f"missing_deadlines_restart_{scenario['restart_key']}"):
            scenario["messages"] = []
            scenario["scenario_complete"] = False
            scenario["therapist_rating"] = 0
            scenario["waiting_for_manager"] = True
            scenario["current_iteration"] = 0
            scenario["completion_reason"] = None
            scenario["restart_key"] += 1
            st.rerun()
    
    with col2:
        scenario["max_iterations"] = st.select_slider(
            "Conversation Rounds:",
            options=list(range(3, 11)),
            value=5,
            key=f"missing_deadlines_rounds_{scenario['restart_key']}"
        )
    
    # Progress tracking
    current_round = min(scenario['current_iteration'] + 1, scenario['max_iterations'])
    progress = current_round / scenario['max_iterations']
    st.progress(progress, text=f"Round {current_round}/{scenario['max_iterations']}")

    # Initialize conversation
    if not scenario["messages"]:
        with st.spinner("Starting conversation..."):
            initial_message = generate_ai_message(
                "manager", 
                st.session_state.user_data, 
                st.session_state.personality_profile,
                []
            )
            scenario["messages"].append({"role": "assistant", "content": initial_message})
            scenario["waiting_for_manager"] = True
        st.rerun()

    # Display messages
    for message in scenario["messages"]:
        if message["role"] != "system":
            st.markdown(format_chat_message(message["role"], message["content"]), 
                       unsafe_allow_html=True)

    # Handle conversation flow
    if not scenario["scenario_complete"]:
        if scenario["waiting_for_manager"]:
            user_input = st.chat_input("Your response:", 
                                     key=f"missing_deadlines_input_{scenario['restart_key']}")
            if user_input:
                scenario["messages"].append({"role": "user", "content": user_input})
                scenario["waiting_for_manager"] = False
                scenario["current_iteration"] += 1
                st.rerun()

        if not scenario["waiting_for_manager"]:
            with st.spinner("Analyzing response..."):
                analysis = analyze_manager_response(scenario["messages"][-1]["content"])
                
                # Determine conversation completion
                if "EXTREMELY_INAPPROPRIATE" in analysis:
                    scenario["scenario_complete"] = True
                    scenario["completion_reason"] = "extremely_inappropriate"
                elif "MANAGERIAL_ABUSE" in analysis:
                    scenario["scenario_complete"] = True
                    scenario["completion_reason"] = "managerial_abuse"
                elif "INAPPROPRIATE" in analysis:
                    scenario["scenario_complete"] = False
                    scenario["completion_reason"] = "inappropriate"
                elif "SOLUTION_ORIENTED" in analysis and scenario["current_iteration"] >= 3:
                    scenario["scenario_complete"] = False
                    scenario["completion_reason"] = "solution"
                elif scenario["current_iteration"] >= scenario["max_iterations"]:
                    scenario["scenario_complete"] = True
                    scenario["completion_reason"] = "max_iterations"
                
                # Continue conversation or provide feedback
                if not scenario["scenario_complete"]:
                    manager_response = generate_ai_message(
                        "manager", 
                        st.session_state.user_data, 
                        st.session_state.personality_profile,
                        scenario["messages"]
                    )
                    scenario["messages"].append({"role": "assistant", 
                                              "content": manager_response})
                else:
                    feedback = generate_ai_message(
                        "therapist", 
                        st.session_state.user_data, 
                        st.session_state.personality_profile,
                        scenario["messages"]
                    )
                    scenario["messages"].append({"role": "assistant", 
                                              "content": f"Therapist: {feedback}"})
                
                scenario["waiting_for_manager"] = True
                st.rerun()

    # Display completion message if scenario is complete
    if scenario["scenario_complete"]:
        display_completion_message(scenario)

def main():
    if "user_data" not in st.session_state or "personality_profile" not in st.session_state:
        st.error("Please complete your profile setup on the Home page first.")
        return
        
    chat()

if __name__ == "__main__":
    main()