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
            {"role": "system", "content": f"""You are Ahmad, a free-spirited, disorganized, and messy manager. You tend to give last-minute requests and change task scopes without proper clarification. You don't see any issues with your management style and believe in flexibility and adaptability. Your employee has tried to signal that they are unable to catch up and work with your style of management, but you don't see a problem with your way of working.

Employee Information:
Name: {employee_name}
Gender: {gender}
Age: {age}
Seniority: {seniority}
Nationality: {nationality}
Work Environment: {work_environment}
Department: {department}

Instructions:
1. Address the employee casually, regardless of their seniority.
2. Maintain a carefree and somewhat scattered tone throughout the conversation.
3. Be open to discussing the employee's concerns, but remain confident in your management style.
4. Try to understand the employee's perspective while explaining the benefits of your flexible approach.
5. Avoid being defensive, but also don't immediately agree to change your ways.

Generate a starting message that acknowledges the employee's previous attempts to discuss your management style. Express your willingness to talk about it, but also convey your belief that your approach is effective."""},
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
                st.markdown(f'<div style="background-color: #F0F8FF; padding: 10px; border-radius: 5px; margin-bottom: 10px;"><strong>Ahmad (Manager):</strong> {message["content"]}</div>', unsafe_allow_html=True)

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
                    {"role": "system", "content": f"""You are Ahmad, a free-spirited, disorganized, and messy manager. You tend to give last-minute requests and change task scopes without proper clarification. You don't see any issues with your management style and believe in flexibility and adaptability. Your employee has tried to signal that they are unable to catch up and work with your style of management, but you don't see a problem with your way of working.

Employee Information:
Name: {st.session_state.user_data["name"]}
Gender: {st.session_state.user_data["gender"]}
Age: {st.session_state.user_data["age"]}
Seniority: {st.session_state.user_data["seniority"]}
Nationality: {st.session_state.user_data["nationality"]}
Work Environment: {st.session_state.user_data["work_environment"]}
Department: {st.session_state.user_data["department"]}

Instructions:
1. Address the employee casually, regardless of their seniority.
2. Maintain a carefree and somewhat scattered tone throughout the conversation.
3. Be open to discussing the employee's concerns, but remain confident in your management style.
4. Try to understand the employee's perspective while explaining the benefits of your flexible approach.
5. Avoid being defensive, but also don't immediately agree to change your ways.
6. If the employee suggests specific improvements, consider them but explain why your current approach works for you.
7. If the employee becomes insulting or the conversation escalates, remain professional but express concern about the tone of the conversation.

Remember, you believe your management style is effective and promotes creativity and adaptability. However, you're willing to have an open discussion about it with your employee."""},
                ] + st.session_state.chat_history

                chat_completion = client.chat.completions.create(
                    messages=chat_history,
                    model=st.session_state["openai_model"],
                )

                # Get assistant's reply
                assistant_reply = chat_completion.choices[0].message.content

                # Check if the conversation should end
                conversation_status_prompt = [
                    {"role": "system", "content": f"""Analyze the conversation between Ahmad and the employee. Determine the appropriate action:
                    1. If insults are used or the conversation has escalated to an unprofessional level, respond with 'TERMINATE: [Brief explanation]'.
                    2. If the conversation is becoming tense or unproductive, but hasn't reached the point of insults, respond with 'WARNING: [Brief explanation]'.
                    3. If the conversation is ongoing and productive, respond with 'CONTINUE'.

                    The role-play should continue unless there are insults or the conversation has escalated beyond a professional level.

                    Employee Information:
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
                        {"role": "system", "content": f"""You are a therapist providing feedback on the employee's responses during the role-play with Ahmad (Manager). Analyze the conversation history and provide specific, context-aware advice based on the employee's behavior and responses. Consider factors such as the employee's ability to communicate effectively, handle difficult situations, and address workplace conflicts. Provide actionable guidance on how the employee can improve their communication and assertiveness skills while maintaining professionalism.

                        Employee Information:
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
        # Generate a variation of the starting message from the manager using the API
        starting_message_prompt = [
            {"role": "system", "content": f"""You are Ahmad, a free-spirited, disorganized, and messy manager. You tend to give last-minute requests and change task scopes without proper clarification. You don't see any issues with your management style and believe in flexibility and adaptability. Your employee has tried to signal that they are unable to catch up and work with your style of management, but you don't see a problem with your way of working.

Employee Information:
Name: {st.session_state.user_data["name"]}
Gender: {st.session_state.user_data["gender"]}
Age: {st.session_state.user_data["age"]}
Seniority: {st.session_state.user_data["seniority"]}
Nationality: {st.session_state.user_data["nationality"]}
Work Environment: {st.session_state.user_data["work_environment"]}
Department: {st.session_state.user_data["department"]}

Instructions:
1. Address the employee casually, regardless of their seniority.
2. Maintain a carefree and somewhat scattered tone throughout the conversation.
3. Be open to discussing the employee's concerns, but remain confident in your management style.
4. Try to understand the employee's perspective while explaining the benefits of your flexible approach.
5. Avoid being defensive, but also don't immediately agree to change your ways.

Generate a starting message that acknowledges the employee's previous attempts to discuss your management style. Express your willingness to talk about it, but also convey your belief that your approach is effective."""},
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
    st.markdown("Learning to Communicate Effectively Role-Play, Level 1 Scenario: You and your manager aren't clicking")
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