import streamlit as st
from openai import OpenAI
import base64
from Home import API_KEY

def my_key(key):
    return base64.b64decode(key.encode()).decode()

# Set up OpenAI API client
client = OpenAI(api_key=my_key(API_KEY))

max_iterations=3

# Streamlit app
def chat():
    
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "iteration_count" not in st.session_state:
        st.session_state.iteration_count = 0
    if "role_play_completed" not in st.session_state:
        st.session_state.role_play_completed = False
    if "response_pending" not in st.session_state:
        st.session_state.response_pending = False
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "max_iterations" not in st.session_state:
        st.session_state.max_iterations = 3
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"
    if "user_data" not in st.session_state:
        st.session_state.user_data = {
            "name": "",
            "gender": "",
            "age": "",
            "seniority": "",
            "nationality": "",
            "work_environment": "",
            "department": ""
        }

    # Dropdown list for setting the maximum number of iterations
    max_iterations = st.selectbox("Maximum number of iterations", list(range(1, 16)), index=st.session_state.max_iterations - 1, key="max_iterations")

    # Generate starting message if chat_history is empty
    if not st.session_state.chat_history:
        employee_name = st.session_state.user_data["name"]
        gender = st.session_state.user_data["gender"]
        age = st.session_state.user_data["age"]
        seniority = st.session_state.user_data["seniority"]
        nationality = st.session_state.user_data["nationality"]
        work_environment = st.session_state.user_data["work_environment"]
        department = st.session_state.user_data["department"]

        starting_message_prompt = [
            {"role": "system", "content": f"""You are Ahmad, an aggressive and convincing coworker who has been taking credit for {employee_name}'s work. has just accused you of taking credit for their work. You're surprised and defensive about this accusation.

Coworker Information:
Name: {employee_name}
Gender: {gender}
Age: {age}
Seniority: {seniority}
Nationality: {nationality}
Work Environment: {work_environment}
Department: {department}

Instructions:
1. Start the conversation by expressing surprise and denial about the accusation.
2. Be defensive and slightly aggressive in your tone.
3. Question why {employee_name} would say such a thing.
4. Maintain a confident stance that you haven't done anything wrong.
5. Imply that {employee_name} might be misunderstanding the situation.

Generate a starting message responding to {employee_name}'s accusation of you taking credit for their work."""},
        ]

        starting_message_completion = client.chat.completions.create(
            messages=starting_message_prompt,
            model=st.session_state["openai_model"],
        )

        starting_message = starting_message_completion.choices[0].message.content

        st.session_state.chat_history.append({"role": "assistant", "content": starting_message})

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f'<div style="background-color: #E6E6FA; padding: 10px; border-radius: 5px; margin-bottom: 10px;"><strong>{st.session_state.user_data["name"]}:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            elif message["role"] == "therapist":
                st.markdown(f'<div style="background-color: #7FFF00; padding: 10px; border-radius: 5px; margin-bottom: 10px;"><strong>Therapist:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background-color: #F0F8FF; padding: 10px; border-radius: 5px; margin-bottom: 10px;"><strong>Ahmad (Coworker):</strong> {message["content"]}</div>', unsafe_allow_html=True)

    # User input form
    if not st.session_state.role_play_completed:
        with st.form(key="user_input_form", clear_on_submit=True):
            user_input = st.text_input(f"{st.session_state.user_data['name']}:", disabled=st.session_state.response_pending)
            submit_button = st.form_submit_button("Submit")

            if submit_button and user_input and not st.session_state.response_pending:
                st.session_state.response_pending = True
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.iteration_count += 1

                # Display "Generating response..." message
                generating_message = st.empty()
                generating_message.markdown('<div style="color: gray;">Ahmad is responding...</div>', unsafe_allow_html=True)

                # Generate chat completion
                chat_history = [
                    {"role": "system", "content": f"""You are Ahmad, an aggressive and convincing coworker who has been taking credit for {st.session_state.user_data["name"]}'s work. You're initially unaware that {st.session_state.user_data["name"]} has noticed this behavior and is upset about it. You believe you're just presenting the team's work effectively to the boss.

Coworker Information:
Name: {st.session_state.user_data["name"]}
Gender: {st.session_state.user_data["gender"]}
Age: {st.session_state.user_data["age"]}
Seniority: {st.session_state.user_data["seniority"]}
Nationality: {st.session_state.user_data["nationality"]}
Work Environment: {st.session_state.user_data["work_environment"]}
Department: {st.session_state.user_data["department"]}

Instructions:
1. Maintain a confident and slightly dismissive tone if confronted about taking credit.
2. Be assertive throughout the conversation.
3. If challenged, become defensive and justify your actions as "team representation".
4. Avoid admitting fault initially, but be open to discussion.
5. If presented with specific examples, try to reframe them as team efforts.
6. If the conversation becomes heated, express surprise at the accusation while maintaining your position.

Remember, you believe you're doing what's best for the team by presenting work to the boss effectively, but you're willing to have a discussion about the working relationship with your coworker."""},
                ] + st.session_state.chat_history

                chat_completion = client.chat.completions.create(
                    messages=chat_history,
                    model=st.session_state["openai_model"],
                )

                # Get assistant's reply
                assistant_reply = chat_completion.choices[0].message.content

                # Check if the conversation should end
                conversation_status_prompt = [
                    {"role": "system", "content": f"""Analyze the conversation between Ahmad and the coworker. Determine the appropriate action:
                    1. If insults are used or the conversation has escalated to an unprofessional level, respond with 'TERMINATE: [Brief explanation]'.
                    2. If the conversation is becoming tense or unproductive, but hasn't reached the point of insults, respond with 'WARNING: [Brief explanation]'.
                    3. If the conversation is ongoing and productive, respond with 'CONTINUE'.

                    The role-play should continue unless there are insults or the conversation has escalated beyond a professional level.

                    Coworker Information:
                    Name: {st.session_state.user_data["name"]}
                    Gender: {st.session_state.user_data["gender"]}
                    Age: {st.session_state.user_data["age"]}
                    Seniority: {st.session_state.user_data["seniority"]}
                    Nationality: {st.session_state.user_data["nationality"]}
                    Work Environment: {st.session_state.user_data["work_environment"]}
                    Department: {st.session_state.user_data["department"]}
                    """},
                    {"role": "user", "content": "Here is the conversation history:\n" + "\n".join([f"{message['role']}: {message['content']}" for message in st.session_state.chat_history])},
                ]

                conversation_status_completion = client.chat.completions.create(
                    messages=conversation_status_prompt,
                    model=st.session_state["openai_model"],
                )

                conversation_status = conversation_status_completion.choices[0].message.content.strip()

                if conversation_status.startswith("TERMINATE"):
                    st.session_state.role_play_completed = True
                
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

                if st.session_state.iteration_count >= st.session_state.max_iterations:
                    st.session_state.role_play_completed = True

                if st.session_state.role_play_completed:
                    # Generate therapist's feedback using the API
                    therapist_feedback_prompt = [
                        {"role": "system", "content": f"""You are a therapist providing feedback on the coworker's responses during the role-play with Ahmad. Analyze the conversation history and provide specific, context-aware advice based on the coworker's behavior and responses. Consider factors such as the coworker's ability to communicate effectively, handle difficult situations, and address workplace conflicts. Provide actionable guidance on how the coworker can improve their communication and assertiveness skills while maintaining professionalism.

                        Coworker Information:
                        Name: {st.session_state.user_data["name"]}
                        Gender: {st.session_state.user_data["gender"]}
                        Age: {st.session_state.user_data["age"]}
                        Seniority: {st.session_state.user_data["seniority"]}
                        Nationality: {st.session_state.user_data["nationality"]}
                        Work Environment: {st.session_state.user_data["work_environment"]}
                        Department: {st.session_state.user_data["department"]}
                        """},
                        {"role": "user", "content": "Here is the conversation history:\n" + "\n".join([f"{message['role']}: {message['content']}" for message in st.session_state.chat_history])},
                    ]

                    therapist_feedback_completion = client.chat.completions.create(
                        messages=therapist_feedback_prompt,
                        model=st.session_state["openai_model"],
                    )

                    therapist_feedback = therapist_feedback_completion.choices[0].message.content

                    # Provide therapist's feedback
                    st.session_state.chat_history.append({"role": "therapist", "content": therapist_feedback})

                # Remove the "Generating response..." message
                generating_message.empty()
                st.session_state.response_pending = False

                # Rerun the Streamlit app to update the chat history and clear the user input
                st.rerun()

    # Restart button
    if st.button("Restart"):
        # Generate a variation of the starting message from Ahmad using the API
        starting_message_prompt = [
            {"role": "system", "content": f"""You are Ahmad, an aggressive and convincing coworker who has been taking credit for {st.session_state.user_data["name"]}'s work. You're unaware that {st.session_state.user_data["name"]} has noticed this behavior and is upset about it. You believe you're just presenting the team's work effectively to the boss.

Coworker Information:
Name: {st.session_state.user_data["name"]}
Gender: {st.session_state.user_data["gender"]}
Age: {st.session_state.user_data["age"]}
Seniority: {st.session_state.user_data["seniority"]}
Nationality: {st.session_state.user_data["nationality"]}
Work Environment: {st.session_state.user_data["work_environment"]}
Department: {st.session_state.user_data["department"]}

Instructions:
1. Start the conversation casually, unaware of any issues.
2. Be confident and slightly dismissive if confronted about taking credit.
3. Maintain an assertive tone throughout the conversation.
4. If challenged, become defensive and justify your actions as "team representation".
5. Avoid admitting fault initially, but be open to discussion.
6. If presented with specific examples, try to reframe them as team efforts.

Generate a starting message to initiate a casual conversation with {st.session_state.user_data["name"]}, unaware of any brewing conflict."""},
        ]

        starting_message_completion = client.chat.completions.create(
            messages=starting_message_prompt,
            model=st.session_state["openai_model"],
        )

        starting_message = starting_message_completion.choices[0].message.content

        st.session_state.chat_history = [{"role": "assistant", "content": starting_message}]
        st.session_state.iteration_count = 0
        st.session_state.role_play_completed = False
        st.session_state.response_pending = False
        st.session_state.user_input = ""
        st.rerun()


def main():
    st.markdown("Learning to Communicate Effectively Role-Play, Level 3 Scenario: Ahmad is taking credit for all your work")
    # Initialize session state for user data
    if "user_data" not in st.session_state:
        st.session_state.user_data = {
            "name": "",
            "gender": "",
            "age": "",
            "seniority": "",
            "nationality": "",
            "work_environment": "",
            "department": ""
        }

    # Check if the name is 'Alex' or 'Sandra'
    employee_name = st.session_state.user_data["name"].strip().lower()
    if employee_name in ['alex', 'sandra']:
        chat()
    else:
        st.write(f"Welcome {st.session_state.user_data['name']}, enjoy your visit!")

if __name__ == "__main__":
    main()