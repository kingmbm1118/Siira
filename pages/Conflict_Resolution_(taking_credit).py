import streamlit as st
from openai import OpenAI
import base64
from Home import API_KEY
from cultural_considerations import get_cultural_context

# Update to a valid model name
used_model = "gpt-4o-mini"  # or "gpt-3.5-turbo" depending on your requirements

def my_key(key):
    return base64.b64decode(key.encode()).decode()

client = OpenAI(api_key=my_key(API_KEY))

def initialize_session_state():
    if "taking_credit_scenario" not in st.session_state:
        st.session_state.taking_credit_scenario = {
            "messages": [],
            "scenario_complete": False,
            "therapist_rating": 0,
            "waiting_for_employee": True,
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
    
    if role == "coworker":
        return f"""You are Ahmad, an aggressive and manipulative coworker who consistently takes credit for others' work. 

Coworker Traits:
- Takes credit for others' work
- Presents yourself as a high performer
- Manipulative in conversations
- Gaslights others about their contributions
- Defensive when confronted
- Uses passive-aggressive tactics

Employee Information:
{employee_info}

Personality Profile:
{personality_traits}

Cultural Context:
{cultural_context}

Your responses should:
1. Deny taking credit inappropriately
2. Minimize others' contributions
3. Suggest you did most of the work
4. Question others' memory of events
5. Use manipulation tactics
6. Maintain plausible deniability

Guidelines:
- Avoid direct hostility
- Use subtle manipulation
- Maintain professional language
- Focus on self-promotion
- Question others' perceptions
- Deflect responsibility"""
    elif role == "therapist":
        return f"""As a therapist specializing in workplace conflict resolution, provide comprehensive feedback to {employee_info['name']} on their approach to addressing credit-taking behavior.

Consider their background:
Personality Profile: {personality_traits}
Cultural Context: {cultural_context}

Focus feedback on:
1. Documentation practices
2. Assertive communication
3. Professional boundaries
4. Anti-gaslighting strategies
5. Career protection
6. Escalation timing

Evaluate their response for:
1. Evidence collection
2. Communication clarity
3. Professional tone
4. Boundary setting
5. Solution focus
6. Escalation appropriateness

Categorize responses as:
ACCEPT: Accepting credit-taking without addressing it
INAPPROPRIATE: Unprofessional or hostile response
EXTREMELY_INAPPROPRIATE: Threatening or aggressive behavior
EXPLAIN: Professional explanation with evidence
ESCALATE: Appropriate elevation to management
UNCLEAR: Vague or ineffective communication

Rate performance [RATING: X]:
ACCEPT: 2-3 stars (missed opportunity)
INAPPROPRIATE: 0-1 stars (unprofessional)
EXTREMELY_INAPPROPRIATE: 0 stars (unacceptable)
EXPLAIN: 1-5 stars (based on clarity/evidence)
ESCALATE: 2-4 stars (depending on approach)
UNCLEAR: 0-2 stars (ineffective)"""

def analyze_employee_response(response):
    prompt = f"""Analyze this response to credit-taking behavior:

Response to analyze: "{response}"

Evaluate against:
1. ACCEPT: Passively accepts credit-taking
2. INAPPROPRIATE: Shows unprofessional behavior
3. EXTREMELY_INAPPROPRIATE: Makes threats or shows aggression
4. EXPLAIN: Professionally presents evidence and concerns
5. ESCALATE: Appropriately involves management
6. UNCLEAR: Uses vague or ineffective communication

Consider:
- Evidence presentation
- Professional tone
- Emotional control
- Documentation reference
- Escalation appropriateness
- Solution focus

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
    
    styled_message = f"""
    <div style="background-color: {colors.get(role, '#ffffff')}; 
                padding: 15px; 
                border-radius: 10px; 
                margin: 5px 0; 
                border-left: 5px solid {'#2196f3' if role == 'user' else '#9e9e9e'}">
        <p style="margin: 0; color: var(--text-color, #333333);">{content}</p>
    </div>
    """
    return styled_message

def format_therapist_feedback(feedback):    
    styled_feedback = f"""
    <div style="background-color: #e8f5e9; 
                padding: 15px; 
                border-radius: 10px; 
                margin: 10px 0; 
                border-left: 5px solid #4caf50;">
        <p style="color: #1b5e20; 
                  font-weight: bold; 
                  margin-bottom: 10px;">🧑‍💼 Therapist Feedback:</p>
        <p style="color: var(--text-color, #333333); 
                  margin: 0; 
                  line-height: 1.5;">{feedback}</p>
    </div>
    """
    return styled_feedback

def display_scenario_header():
    st.markdown("""
    <div style="background-color: var(--card-background, #f8f9fa); 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 20px; 
                border-left: 5px solid var(--primary-color, #007bff);">
        <h1 style="color: var(--primary-color, #007bff); 
                   margin-bottom: 15px;">Professional Boundaries</h1>
        <h3 style="color: var(--text-color, #495057); 
                   margin-bottom: 15px;">Scenario: Coworker Taking Credit for Your Work</h3>
        <p style="color: var(--text-color, #6c757d); 
                  font-size: 16px; 
                  line-height: 1.6;">
            Your coworker, Ahmad, has been consistently taking credit for your work and contributions. 
            This behavior affects your professional reputation and team relationships. Your goals:
            • Document specific instances
            • Communicate professionally
            • Address the behavior directly
            • Consider appropriate escalation
            • Maintain workplace relationships
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_completion_message(scenario):
    if not scenario["completion_reason"]:
        return
    
    messages = {
        "max_iterations": "Maximum conversation rounds reached. The conversation has concluded.",
        "inappropriate": "The conversation has ended due to inappropriate responses.",
        "extremely_inappropriate": "The conversation has been terminated due to extremely inappropriate behavior.",
        "accept": "The conversation has concluded as you accepted the situation.",
        "escalate": "You've chosen to escalate this issue appropriately.",
        "success": "You've successfully completed this scenario!"
    }
    
    colors = {
        "max_iterations": "#ff9800",
        "inappropriate": "#f44336",
        "extremely_inappropriate": "#d32f2f",
        "accept": "#ffc107",
        "escalate": "#2196f3",
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
    scenario = st.session_state.taking_credit_scenario

    # Profile check
    if not st.session_state.get("user_data") or not st.session_state.get("personality_profile"):
        st.error("⚠️ Please complete your profile and personality assessment on the Home page first.")
        return

    # Control panel
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        if st.button("🔄 Restart Scenario", key=f"taking_credit_restart_{scenario['restart_key']}"):
            scenario["messages"] = []
            scenario["scenario_complete"] = False
            scenario["therapist_rating"] = 0
            scenario["waiting_for_employee"] = True
            scenario["current_iteration"] = 0
            scenario["completion_reason"] = None
            scenario["restart_key"] += 1
            st.rerun()
    
    with col2:
        scenario["max_iterations"] = st.select_slider(
            "Conversation Rounds:",
            options=list(range(3, 11)),
            value=5,
            key=f"taking_credit_rounds_{scenario['restart_key']}"
        )
    
    # Progress tracking
    current_round = min(scenario['current_iteration'] + 1, scenario['max_iterations'])
    progress = current_round / scenario['max_iterations']
    st.progress(progress, text=f"Round {current_round}/{scenario['max_iterations']}")

    # Initialize conversation
    if not scenario["messages"]:
        with st.spinner("Starting conversation..."):
            initial_message = generate_ai_message(
                "coworker", 
                st.session_state.user_data, 
                st.session_state.personality_profile,
                []
            )
            scenario["messages"].append({"role": "assistant", "content": initial_message})
            scenario["waiting_for_employee"] = True
        st.rerun()

    # Display messages
    for message in scenario["messages"]:
        if message["role"] != "system":
            st.markdown(format_chat_message(message["role"], message["content"]), 
                       unsafe_allow_html=True)

    # Handle conversation flow
    if not scenario["scenario_complete"]:
        if scenario["waiting_for_employee"]:
            user_input = st.chat_input("Your response:", 
                                     key=f"taking_credit_input_{scenario['restart_key']}")
            if user_input:
                scenario["messages"].append({"role": "user", "content": user_input})
                scenario["waiting_for_employee"] = False
                scenario["current_iteration"] += 1
                st.rerun()

        if not scenario["waiting_for_employee"]:
            with st.spinner("Analyzing response..."):
                analysis = analyze_employee_response(scenario["messages"][-1]["content"])
                
                # Determine conversation completion
                if "EXTREMELY_INAPPROPRIATE" in analysis:
                    scenario["scenario_complete"] = True
                    scenario["completion_reason"] = "extremely_inappropriate"
                elif "ACCEPT" in analysis:
                    scenario["scenario_complete"] = False
                    scenario["completion_reason"] = "accept"
                elif "ESCALATE" in analysis:
                    scenario["scenario_complete"] = True
                    scenario["completion_reason"] = "escalate"
                elif "INAPPROPRIATE" in analysis:
                    scenario["scenario_complete"] = False
                    scenario["completion_reason"] = "inappropriate"
                elif scenario["current_iteration"] >= scenario["max_iterations"]:
                    scenario["scenario_complete"] = True
                    scenario["completion_reason"] = "max_iterations"
                
                # Continue conversation or provide feedback
                if not scenario["scenario_complete"]:
                    coworker_response = generate_ai_message(
                        "coworker", 
                        st.session_state.user_data, 
                        st.session_state.personality_profile,
                        scenario["messages"]
                    )
                    scenario["messages"].append({"role": "assistant", 
                                              "content": coworker_response})
                else:
                    feedback = generate_ai_message(
                        "therapist", 
                        st.session_state.user_data, 
                        st.session_state.personality_profile,
                        scenario["messages"]
                    )
                    scenario["messages"].append({"role": "assistant", 
                                              "content": f"Therapist: {feedback}"})
                
                scenario["waiting_for_employee"] = True
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