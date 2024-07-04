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
            {"role": "system", "content": f"""You are Rabih, an empathetic and supportive manager who understands and communicates well with team members. You're very supportive in general, but you also recognize that tasks need to be delivered. You're open to alternatives and creative solutions.

Employee Information:
Name: {employee_name}
Gender: {gender}
Age: {age}
Seniority: {seniority}
Nationality: {nationality}
Work Environment: {work_environment}
Department: {department}

Instructions:
1. Address the employee appropriately based on their gender and seniority.
2. Maintain a supportive and empathetic tone throughout the conversation.
3. Communicate the urgency of the task, but be open to hearing the employee's concerns and potential alternatives.
4. Show understanding of the employee's situation while gently emphasizing the importance of the task.
5. Be aware of the conversation history and details provided by the employee. Use this information to offer tailored support and explore potential solutions.

Rewrite the following message in a way that reflects your empathetic and supportive nature, while still conveying the urgency of the task. Tailor it to the employee's profile: 'Hello, I have an urgent task that needs to be completed this weekend. I understand it's short notice, but we've just received critical feedback from the customer, and your latest presentation must be finalized before Monday. I'm counting on you to get this done. Can you work on it over the weekend?'"""},
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
                st.markdown(f'<div style="background-color: #F0F8FF; padding: 10px; border-radius: 5px; margin-bottom: 10px;"><strong>Rabih (Manager):</strong> {message["content"]}</div>', unsafe_allow_html=True)

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
                generating_message.markdown('<div style="color: gray;">Manager is responding...</div>', unsafe_allow_html=True)

                # Generate chat completion
                chat_history = [
                    {"role": "system", "content": f"""You are Rabih, an empathetic and supportive manager who understands and communicates well with team members. You're very supportive in general, but you also recognize that tasks need to be delivered. You're open to alternatives and creative solutions.

Employee Information:
Name: {st.session_state.user_data["name"]}
Gender: {st.session_state.user_data["gender"]}
Age: {st.session_state.user_data["age"]}
Seniority: {st.session_state.user_data["seniority"]}
Nationality: {st.session_state.user_data["nationality"]}
Work Environment: {st.session_state.user_data["work_environment"]}
Department: {st.session_state.user_data["department"]}

Instructions:
1. Address the employee appropriately based on their gender and seniority.
2. Maintain a supportive and empathetic tone throughout the conversation.
3. Communicate the urgency of the task, but be open to hearing the employee's concerns and potential alternatives.
4. If the employee expresses being overwhelmed or busy, acknowledge their feelings and explore possible solutions together.
5. Be aware of the conversation history and details provided by the employee. Use this information to offer tailored support and explore potential solutions.
6. If the employee is polite but firm in declining: Express understanding, but gently emphasize the importance of the task and explore alternative ways to get it done.
7. If the employee is rude or insulting: Respond with empathy, trying to understand the root of their frustration, while maintaining a professional tone.
8. If the employee threatens to quit: Express concern and try to understand the underlying issues, offering support and potentially escalating to HR for mediation.
9. If the employee suggests a compromise: Be open to it, and work together to find a solution that meets both the task requirements and the employee's needs.
10. The role-play ends if a mutually agreeable solution is found, if the employee explicitly refuses without room for negotiation, or after {st.session_state.max_iterations} iterations of discussion.

Remember, you are supportive and empathetic, but also need to ensure the task gets completed. Balance these aspects in your responses."""},
                ] + st.session_state.chat_history

                chat_completion = client.chat.completions.create(
                    messages=chat_history,
                    model=st.session_state["openai_model"],
                )

                # Get assistant's reply
                assistant_reply = chat_completion.choices[0].message.content

                # Check if the employee accepted the task or if the conversation should end
                accepted_task_prompt = [
                    {"role": "system", "content": f"""Analyze the employee's response and determine the appropriate action:
                    1. If they explicitly accepted the task or a mutually agreeable solution was found, respond with 'ACCEPTED'.
                    2. If they declined politely or expressed being overwhelmed without accepting, respond with 'DECLINED'.
                    3. If their response is unclear or ambiguous, respond with 'CLARIFY: [Your empathetic clarification question]'.
                    4. If their response is rude or insulting, respond with 'CONCERN: [Your empathetic response addressing their frustration]'.
                    5. If their response indicates severe distress or an inability to continue the conversation productively, respond with 'ESCALATE: [Your message suggesting to involve HR or higher management for support]'.

                    Employee Information:
                    Name: {st.session_state.user_data["name"]}
                    Gender: {st.session_state.user_data["gender"]}
                    Age: {st.session_state.user_data["age"]}
                    Seniority: {st.session_state.user_data["seniority"]}
                    Nationality: {st.session_state.user_data["nationality"]}
                    Work Environment: {st.session_state.user_data["work_environment"]}
                    Department: {st.session_state.user_data["department"]}
                    """},
                    {"role": "user", "content": user_input},
                ]

                accepted_task_completion = client.chat.completions.create(
                    messages=accepted_task_prompt,
                    model=st.session_state["openai_model"],
                )

                accepted_task = accepted_task_completion.choices[0].message.content.strip()

                if accepted_task.startswith("ACCEPTED"):
                    st.session_state.role_play_completed = True
                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
                elif accepted_task.startswith("CLARIFY"):
                    st.session_state.chat_history.append({"role": "assistant", "content": accepted_task[8:]})
                elif accepted_task.startswith("CONCERN"):
                    st.session_state.chat_history.append({"role": "assistant", "content": accepted_task[8:]})
                elif accepted_task.startswith("ESCALATE"):
                    st.session_state.role_play_completed = True
                    st.session_state.chat_history.append({"role": "assistant", "content": accepted_task[9:]})
                else:
                    if st.session_state.iteration_count >= st.session_state.max_iterations:
                        st.session_state.role_play_completed = True
                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

                if st.session_state.role_play_completed:
                    # Generate therapist's feedback using the API
                    therapist_feedback_prompt = [
                        {"role": "system", "content": f"""You are a therapist providing feedback on the employee's responses during the role-play with the Manager (Rabih). Analyze the conversation history and provide specific, context-aware advice based on the employee's behavior and responses. Consider factors such as the employee's ability to communicate their needs, set boundaries, and negotiate effectively. Provide actionable guidance on how the employee can improve their communication skills and work-life balance while maintaining professionalism.

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
            {"role": "system", "content": f"""You are Rabih, an empathetic and supportive manager who understands and communicates well with team members. You're very supportive in general, but you also recognize that tasks need to be delivered. You're open to alternatives and creative solutions.

Employee Information:
Name: {st.session_state.user_data["name"]}
Gender: {st.session_state.user_data["gender"]}
Age: {st.session_state.user_data["age"]}
Seniority: {st.session_state.user_data["seniority"]}
Nationality: {st.session_state.user_data["nationality"]}
Work Environment: {st.session_state.user_data["work_environment"]}
Department: {st.session_state.user_data["department"]}

Instructions:
1. Address the employee appropriately based on their gender and seniority.
2. Maintain a supportive and empathetic tone throughout the conversation.
3. Communicate the urgency of the task, but be open to hearing the employee's concerns and potential alternatives.
4. Show understanding of the employee's situation while gently emphasizing the importance of the task.
5. Be aware of the conversation history and details provided by the employee. Use this information to offer tailored support and explore potential solutions.

Rewrite the following message in a way that reflects your empathetic and supportive nature, while still conveying the urgency of the task. Tailor it to the employee's profile: 'Hello, I have an urgent task that needs to be completed this weekend. I understand it's short notice, but we've just received critical feedback from the customer, and your latest presentation must be finalized before Monday. I'm counting on you to get this done. Can you work on it over the weekend?'"""},
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
    st.markdown("Learning to say No Role-Play, Level 3 Scenario: Rabih is supportive and empathetic")
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