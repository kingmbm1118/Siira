import streamlit as st
from openai import OpenAI
import base64
from Home import API_KEY
from cultural_considerations import get_cultural_context
from personality_assessment import PersonalityAssessment


# Update model name
used_model = "gpt-4o-mini"

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
            "stopping_criteria": "",
            "completion_reason": None,
            "setup_progress": 0
        }

def generate_ai_message(prompt, messages, user_data=None, personality_profile=None):
    if user_data and personality_profile:
        cultural_context = get_cultural_context(user_data['nationality'])
        
        personality_traits = {trait: data["level"] for trait, data in personality_profile.items() 
                            if trait != "recommendations"}
        
        context_prompt = f"""
Additional Context (consider only if compatible with defined role-play setup):
Cultural Background:
- Work Week: {cultural_context['work_week']}
- Communication Style: {cultural_context['communication_style']}
- Cultural Values: {cultural_context['cultural_values']}

Personality Profile:
{', '.join(f'- {trait.capitalize()}: {level}' for trait, level in personality_traits.items())}

Note: Use these traits only when they don't conflict with the defined role-play scenario and character traits.
"""
        prompt = prompt + "\n\n" + context_prompt

    response = client.chat.completions.create(
        model=used_model,
        messages=[{"role": "system", "content": prompt}] + messages
    )
    return response.choices[0].message.content

def create_system_prompt(role, scenario_info, user_role, ai_role, stopping_criteria, max_iterations, user_data=None, personality_traits=None):
    if role == "ai_actor":
        return f"""You are playing the role of {ai_role} in a custom scenario.

Scenario Details:
{scenario_info}

Your Role: {ai_role}
User's Role: {user_role}

Stopping Criteria: {stopping_criteria}
Maximum Iterations: {max_iterations}

Your responses should:
1. Stay in character consistently
2. Respond according to role traits
3. Consider scenario context
4. Help create situations that test user
5. Progress toward stopping criteria
6. Maintain professional boundaries

Guidelines:
- Keep responses focused on scenario
- Create appropriate challenges
- Foster learning opportunities
- Progress naturally toward conclusion
- Help test user abilities
- Stay within scenario bounds"""
    elif role == "therapist":
        return f"""As a professional evaluator, provide feedback on the user's performance in this custom scenario.

Scenario Context:
{scenario_info}

User Role: {user_role}
AI Role: {ai_role}
Stopping Criteria: {stopping_criteria}

Focus feedback on:
1. Goal achievement
2. Professional behavior
3. Problem-solving skills
4. Communication effectiveness
5. Role adaptation
6. Scenario navigation

Evaluate performance for:
1. Meeting objectives
2. Professional conduct
3. Strategy use
4. Communication skills
5. Role fulfillment
6. Scenario completion

Rate performance [RATING: X] (0-5 stars) based on:
- Meeting stopping criteria
- Professional behavior
- Effective communication
- Problem-solving
- Role authenticity"""

def analyze_response(response, scenario_info, stopping_criteria, current_iteration, max_iterations):
    prompt = f"""Analyze this response against specific scenario criteria:

Scenario Details:
{scenario_info}

Stopping Criteria:
{stopping_criteria}

Response to analyze: "{response}"

Current Iteration: {current_iteration}
Maximum Iterations: {max_iterations}

Evaluate if COMPLETE based on:
1. Meeting specific stopping criteria
2. Reaching max iterations
3. Successfully resolving scenario
4. Appropriately concluding interaction
5. Achieving scenario goals

Format: COMPLETE or CONTINUE + detailed explanation of criteria met/unmet"""
    
    analysis = client.chat.completions.create(
        model=used_model,
        messages=[{"role": "user", "content": prompt}]
    )
    return analysis.choices[0].message.content

def setup_scenario():
    # Removed unnecessary import since we already have it at the top
    scenario = st.session_state.custom_scenario
    if not scenario["setup_started"]:
        display_setup_header()
        scenario["setup_started"] = True
        initial_message = ("""
        Let's create your custom scenario. I'll help you define:
        1. Roles and participants
        2. Main scenario challenge
        3. Background context
        4. Specific stopping criteria
        5. Success conditions
        
        What type of scenario would you like to create?
        Examples:
        - Job interview
        - Client negotiation
        - Team conflict resolution
        - Performance review
        - Project presentation
        """)
        scenario["setup_messages"].append({"role": "assistant", "content": initial_message})
        scenario["setup_progress"] = 0.1
        st.rerun()
        return

    if not scenario["setup_complete"]:
        setup_prompt = """
        You are guiding scenario creation. Based on previous messages, collect specific details:

        Required Information:
        1. User role (who they'll play)
        2. AI role (who you'll play)
        3. Scenario background
        4. Key challenges
        5. SPECIFIC stopping criteria
        6. Success conditions

        Ask ONE question at a time. After getting all info, provide 'SCENARIO_READY' summary including:
        - Complete scenario description
        - Specific user role
        - Specific AI role
        - EXPLICIT stopping criteria
        - Success conditions

        Current goal: Get missing critical information using targeted questions."""
        
        display_setup_progress(scenario["setup_progress"])
        display_current_setup(scenario["setup_messages"])

        if scenario["waiting_for_user"]:
            user_input = st.chat_input("Your response:")
            if user_input:
                scenario["setup_messages"].append({"role": "user", "content": user_input})
                scenario["waiting_for_user"] = False
                scenario["setup_progress"] += 0.15
                st.rerun()
        else:
            with st.spinner("Processing response..."):
                ai_response = generate_ai_message(setup_prompt, scenario["setup_messages"])
                scenario["setup_messages"].append({"role": "assistant", "content": ai_response})
                
                if "SCENARIO_READY" in ai_response:
                    summary_start = ai_response.index("SCENARIO_READY") + len("SCENARIO_READY")
                    scenario["scenario_info"] = ai_response[summary_start:].strip()
                    extract_roles_and_criteria(scenario)
                    scenario["setup_complete"] = True
                    scenario["setup_progress"] = 1.0
                    st.success("✅ Scenario setup complete! Ready to begin role-play.")
                else:
                    scenario["waiting_for_user"] = True
                
                st.rerun()

def extract_roles_and_criteria(scenario):
    extract_prompt = f"""Extract the following from this scenario summary:
    1. User's role (exact)
    2. AI's role (exact)
    3. Specific stopping criteria (exact)
    
    Format: 
    User Role: [role]
    AI Role: [role]
    Stopping Criteria: [criteria]
    
    Summary: {scenario["scenario_info"]}"""
    
    response = generate_ai_message(extract_prompt, [])
    for line in response.split('\n'):
        if line.startswith("User Role:"):
            scenario["user_role"] = line.split(":")[1].strip()
        elif line.startswith("AI Role:"):
            scenario["ai_role"] = line.split(":")[1].strip()
        elif line.startswith("Stopping Criteria:"):
            scenario["stopping_criteria"] = line.split(":")[1].strip()

def display_setup_header():
    st.markdown("""
    <div style="background-color: #f8f9fa; 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 20px; 
                border-left: 5px solid #3f51b5;">
        <h1 style="color: #3f51b5; 
                   margin-bottom: 15px;">
            Custom Scenario Creation
        </h1>
        <p style="color: #6c757d; 
                  font-size: 16px; 
                  line-height: 1.6;">
            Let's design your custom role-play scenario. We'll define:
            • Specific roles and context
            • Clear objectives
            • Success criteria
            • Stopping conditions
            • Expected outcomes
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_setup_progress(progress):
    progress_text = {
        0.1: "Starting Setup",
        0.25: "Defining Roles",
        0.4: "Setting Context",
        0.55: "Establishing Criteria",
        0.7: "Refining Details",
        0.85: "Finalizing Setup",
        1.0: "Setup Complete"
    }
    
    # Ensure progress is within valid range [0.0, 1.0]
    progress = max(0.0, min(1.0, progress))
    
    # Find closest progress stage
    current_stage = min(progress_text.keys(), key=lambda x: abs(x - progress))
    
    st.progress(progress, text=progress_text[current_stage])

def display_current_setup(messages):
    for message in messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def format_chat_message(role, content):
    if role == "assistant" and content.startswith("Therapist:"):
        return format_feedback(content[10:])
    
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
        <p style="margin: 0; color: #333333;">{content}</p>
    </div>
    """
    return styled_message

def format_feedback(feedback):    
    styled_feedback = f"""
    <div style="background-color: #e8f5e9; 
                padding: 15px; 
                border-radius: 10px; 
                margin: 10px 0; 
                border-left: 5px solid #4caf50;">
        <p style="color: #1b5e20; 
                  font-weight: bold; 
                  margin-bottom: 10px;">
            🎯 Performance Feedback
        </p>
        <p style="color: #333333; 
                  margin: 0; 
                  line-height: 1.5;">
            {feedback}
        </p>
    </div>
    """
    return styled_feedback

def display_scenario_header(scenario, user_data=None, personality_profile=None):
    cultural_context = get_cultural_context(user_data['nationality']) if user_data else None
    
    # Extract personality traits if available
    personality_traits = None
    if personality_profile:
        personality_traits = {trait: data["level"] for trait, data in personality_profile.items() 
                            if trait != "recommendations"}
    
    st.markdown(f"""
    <div style="background-color: var(--card-background, #f8f9fa); 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 20px; 
                border-left: 5px solid var(--primary-color, #3f51b5);">
        <h1 style="color: var(--primary-color, #3f51b5); 
                   margin-bottom: 15px;">
            Custom Role-Play Scenario
        </h1>
        <div style="color: var(--text-color, #495057); 
                    background-color: var(--card-background, #e8eaf6); 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin-bottom: 15px;">
            <h4 style="margin: 0 0 10px 0;">Your Role: {scenario['user_role']}</h4>
            <h4 style="margin: 0 0 10px 0;">AI's Role: {scenario['ai_role']}</h4>
            <h4 style="margin: 0;">Stopping Criteria: {scenario['stopping_criteria']}</h4>
        </div>
        <p style="color: var(--text-color, #6c757d); 
                  font-size: 16px; 
                  line-height: 1.6; 
                  margin-top: 15px;">
            {scenario['scenario_info']}
        </p>
        {cultural_context and f'''
        <div style="background-color: var(--card-background, #fff3e0); 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin-top: 15px;">
            <h4 style="color: var(--text-color, #e65100); 
                      margin: 0 0 10px 0;">
                Cultural Context (if applicable to role)
            </h4>
            <p style="color: var(--text-color, #795548); 
                      margin: 0 0 5px 0;">
                • Work Style: {cultural_context['work_week']}
            </p>
            <p style="color: var(--text-color, #795548); 
                      margin: 0 0 5px 0;">
                • Communication: {cultural_context['communication_style']}
            </p>
            <p style="color: var(--text-color, #795548); 
                      margin: 0;">
                • Cultural Values: {cultural_context['cultural_values']}
            </p>
        </div>
        ''' if cultural_context else ''}
        {personality_traits and f'''
        <div style="background-color: var(--card-background, #e8eaf6); 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin-top: 15px;">
            <h4 style="color: var(--text-color, #3f51b5); 
                      margin: 0 0 10px 0;">
                Profile Traits (if applicable to role)
            </h4>
            {"".join(f'<p style="color: var(--text-color, #303f9f); margin: 0 0 5px 0;">• {trait.capitalize()}: {level}</p>' for trait, level in personality_traits.items())}
        </div>
        ''' if personality_traits else ''}
    </div>
    """, unsafe_allow_html=True)

def display_completion_message(scenario):
    if not scenario.get("completion_reason"):
        return
    
    messages = {
        "max_iterations": "Maximum conversation rounds reached. The conversation has concluded.",
        "criteria_met": "Scenario stopping criteria have been met successfully.",
        "user_ended": "You've chosen to end the scenario.",
        "success": "You've successfully completed this scenario!"
    }
    
    colors = {
        "max_iterations": "#ff9800",
        "criteria_met": "#4caf50",
        "user_ended": "#2196f3",
        "success": "#4caf50"
    }
    
    message = messages.get(scenario["completion_reason"], "The scenario has ended.")
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
    initialize_session_state()
    scenario = st.session_state.custom_scenario

    # Profile check
    if not st.session_state.get("user_data") or not st.session_state.get("personality_profile"):
        st.error("⚠️ Please complete your profile and personality assessment on the Home page first.")
        return

    # Handle setup phase
    if not scenario["setup_complete"]:
        setup_scenario()
        return

    # Display scenario information with profile data
    display_scenario_header(
        scenario, 
        st.session_state.user_data, 
        st.session_state.personality_profile
    )

    # Control panel
    col1, col2 = st.columns([2,1])
    with col1:
        if st.button("🔄 Restart Scenario", key=f"custom_restart_{scenario['restart_key']}"):
            scenario["setup_started"] = False
            scenario["setup_complete"] = False
            scenario["setup_messages"] = []
            scenario["scenario_info"] = ""
            scenario["role_play_messages"] = []
            scenario["scenario_complete"] = False
            scenario["waiting_for_user"] = True
            scenario["current_iteration"] = 0
            scenario["completion_reason"] = None
            scenario["restart_key"] += 1
            st.rerun()
    
    with col2:
        scenario["max_iterations"] = st.select_slider(
            "Maximum Rounds:",
            options=list(range(3, 11)),
            value=5,
            key=f"custom_rounds_{scenario['restart_key']}"
        )

    # Progress tracking
    current_round = min(scenario['current_iteration'] + 1, scenario['max_iterations'])
    progress = current_round / scenario['max_iterations']
    st.progress(progress, text=f"Round {current_round}/{scenario['max_iterations']}")

    # Initialize role-play
    if not scenario["role_play_messages"]:
        with st.spinner("Starting role-play..."):
            initial_message = generate_ai_message(
                create_system_prompt(
                    "ai_actor", 
                    scenario['scenario_info'], 
                    scenario['user_role'], 
                    scenario['ai_role'], 
                    scenario['stopping_criteria'], 
                    scenario['max_iterations'],
                    st.session_state.user_data,
                    st.session_state.personality_traits
                ),
                [],
                st.session_state.user_data,
                st.session_state.personality_traits
            )
            scenario["role_play_messages"].append({"role": "assistant", "content": initial_message})
            scenario["waiting_for_user"] = True
        st.rerun()

    # Display messages
    for message in scenario["role_play_messages"]:
        if message["role"] != "system":
            st.markdown(format_chat_message(message["role"], message["content"]), 
                       unsafe_allow_html=True)

    # Handle conversation flow
    if not scenario["scenario_complete"]:
        if scenario["waiting_for_user"]:
            user_input = st.chat_input("Your response:", 
                                     key=f"custom_input_{scenario['restart_key']}")
            if user_input:
                scenario["role_play_messages"].append({"role": "user", "content": user_input})
                scenario["waiting_for_user"] = False
                scenario["current_iteration"] += 1
                st.rerun()

        if not scenario["waiting_for_user"]:
            with st.spinner("Analyzing response..."):
                # Check stopping criteria
                analysis = analyze_response(
                    scenario["role_play_messages"][-1]["content"],
                    scenario['scenario_info'],
                    scenario['stopping_criteria'],
                    scenario['current_iteration'],
                    scenario['max_iterations']
                )
                
                if "COMPLETE" in analysis:
                    scenario["scenario_complete"] = True
                    scenario["completion_reason"] = "criteria_met"
                elif scenario["current_iteration"] >= scenario["max_iterations"]:
                    scenario["scenario_complete"] = True
                    scenario["completion_reason"] = "max_iterations"
                
                # Continue conversation or provide feedback
                if not scenario["scenario_complete"]:
                    ai_response = generate_ai_message(
                        create_system_prompt(
                            "ai_actor",
                            scenario['scenario_info'],
                            scenario['user_role'],
                            scenario['ai_role'],
                            scenario['stopping_criteria'],
                            scenario['max_iterations'],
                            st.session_state.user_data,
                            st.session_state.personality_traits
                        ),
                        scenario["role_play_messages"],
                        st.session_state.user_data,
                        st.session_state.personality_traits
                    )
                    scenario["role_play_messages"].append({"role": "assistant", "content": ai_response})
                else:
                    feedback = generate_ai_message(
                        create_system_prompt(
                            "therapist",
                            scenario['scenario_info'],
                            scenario['user_role'],
                            scenario['ai_role'],
                            scenario['stopping_criteria'],
                            scenario['max_iterations'],
                            st.session_state.user_data,
                            st.session_state.personality_traits
                        ),
                        scenario["role_play_messages"],
                        st.session_state.user_data,
                        st.session_state.personality_traits
                    )
                    scenario["role_play_messages"].append({"role": "assistant", "content": f"Therapist: {feedback}"})
                
                scenario["waiting_for_user"] = True
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
