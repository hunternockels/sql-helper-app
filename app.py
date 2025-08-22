import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load up the environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)    


# Configure Streamlit
st.set_page_config(page_title="SQL Practice with Feedback", page_icon="🧠", layout="centered")
st.title("🧠 SQL Practice Helper")
st.write("Time to learn SQL!")

# Session state setup
for key in ["sql_question", "user_answer", "feedback", "history"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "history" else []

# Sidebar settings
st.sidebar.header("⚙️ Settings")
difficulty = st.sidebar.selectbox("Select Difficulty", ["Beginner", "Intermediate", "Advanced"])
if st.sidebar.button("🔄 Reset"):
    st.session_state.sql_question = ""
    st.session_state.user_answer = ""
    st.session_state.feedback = ""
    st.session_state.help_history = []

# Generate new SQL question
if st.button("🎯 New SQL Question"):
    with st.spinner("Generating SQL question..."):
        prompt = f"Give me one {difficulty.lower()} SQL practice question. Just the question, no answer. Make it practical and realistic."
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a SQL tutor who gives practical, technical SQL questions based on difficulty level."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
        )
        st.session_state.sql_question = response.choices[0].message.content.strip()
        st.session_state.user_answer = ""
        st.session_state.feedback = ""

# Display question
if st.session_state.sql_question:
    st.subheader("🧪 Your SQL Question:")
    st.markdown(f"**{st.session_state.sql_question}**")


    # Answer input
    st.session_state.user_answer = st.text_area("✍️ Your SQL Answer:", value=st.session_state.user_answer, height=200)

    # Submit answer
    if st.button("📝 Submit Answer for Feedback"):
        if not st.session_state.user_answer.strip():
            st.warning("Please enter your SQL answer before submitting.")
        else:
            with st.spinner("Evaluating your answer..."):
                feedback_response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a SQL expert providing detailed feedback on students' answers. Be helpful, concise, and constructive."},
                        {"role": "user", "content": f"Here is the SQL question:\n{st.session_state.sql_question}\n\nHere is my answer:\n{st.session_state.user_answer}\n\nPlease give detailed feedback on correctness, logic, formatting, and improvements."}
                    ],
                    temperature=0.5,
                    max_tokens=600,
                )
                st.session_state.feedback = feedback_response.choices[0].message.content.strip()

                # Save to history
                st.session_state.history.append({
                    "question": st.session_state.sql_question,
                    "answer": st.session_state.user_answer,
                    "feedback": st.session_state.feedback,
                    "difficulty": difficulty
                })

# Show feedback
if st.session_state.feedback:
    st.subheader("🔍 GPT Feedback:")
    st.markdown(st.session_state.feedback)

# --- Help Bot Section ---
st.subheader("💬 Have a Question About the Feedback? Ask SQL Sam!")

# Always ensure help_history is a list
if "help_history" not in st.session_state or not isinstance(st.session_state.help_history, list):
    st.session_state.help_history = []

# User input
help_question = st.text_input("Ask SQL Sam about anything to do with your query:")

if st.button("Ask"):
    if help_question.strip():
        # Add to conversation history
        st.session_state.help_history.append({"role": "user", "content": help_question})

        # Send question to OpenAI
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a friendly SQL tutor. Explain things clearly and with examples."},
                    *st.session_state.help_history
                ]
            )
        bot_reply = response.choices[0].message.content

        # Add bot reply to history
        st.session_state.help_history.append({"role": "assistant", "content": bot_reply})

# Display conversation
for chat in st.session_state.help_history:
    if chat["role"] == "user":
        st.markdown(f"**You:** {chat['content']}")
    else:
        st.markdown(f"**SQL Sam:** {chat['content']}")

# Show history
if st.session_state.history:
    st.subheader("📜 Your Practice History")
    for i, entry in enumerate(reversed(st.session_state.history[-5:]),1):
    #Last 5
        with st.expander(f"{entry['difficulty']} Question #{len(st.session_state.history) - i + 1}"):
            st.markdown(f"**🧪 Question:**\nsql\n{entry['question']}\n")
            st.markdown(f"**✍️ Your Answer:**\nsql\n{entry['answer']}\n")
            st.markdown(f"**🔍 Feedback:**\n{entry['feedback']}\n")

