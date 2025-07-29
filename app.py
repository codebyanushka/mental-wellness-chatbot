import streamlit as st
from textblob import TextBlob
import pandas as pd
import os
import matplotlib.pyplot as plt
import base64
from datetime import datetime

# Setup
st.set_page_config(page_title="Mental Wellness Journal", page_icon="🧠")
st.title("Mental Wellness Journal Chatbot")

# Ask for user name
username = st.text_input("Enter your name (for a personal journal):").strip().lower()

if not username:
    st.warning("Please enter your name to continue.")
    st.stop()

# Create personalized file name
file_name = f"{username}_journal_entries.csv"

st.write("Hey there! Just checking in - how are you really feeling today? Whatever it is, you can share it here. I'm all ears and here for you.")

# Custom emotion override
def detect_emotion_keywords(text):
    low_mood_keywords = ['crying', 'devastated', 'worthless', 'hopeless', 'broken', 'exhausted', 'numb', 'alone', 'helpless']
    high_mood_keywords = ['happy', 'joyful', 'excited', 'awesome', 'fantastic', 'blessed', 'grateful', 'amazing']

    text_lower = text.lower()
    for word in low_mood_keywords:
        if word in text_lower:
            return -0.6  # force low sentiment

    for word in high_mood_keywords:
        if word in text_lower:
            return 0.6  # force positive sentiment

    return None  # no override

# Text input
user_input = st.text_area("Write what's on your mind...", height=200)

if st.button("Analyze Mood"):
    if user_input.strip() == "":
        st.warning("Please write something before analyzing.")
    else:
        override_sentiment = detect_emotion_keywords(user_input)
        sentiment = override_sentiment if override_sentiment is not None else TextBlob(user_input).sentiment.polarity

        if sentiment > 0.3:
            st.success("😊 You're radiating good vibes today, keep riding the waves!")
        elif sentiment < -0.1:
            st.error("😔 It seems like you're feeling low today, that's completely okay. YOU GOT ME.")
        else:
            st.info("You seem to be in a neutral space. Maybe take a few breaths and reflect a little deeper – I'm here for you.")

        st.markdown("---")
        st.write("**Your Mood Score:**", round(sentiment, 2))

        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "entry": user_input,
            "mood_score": round(sentiment, 2)
        }

        if os.path.exists(file_name):
            df = pd.read_csv(file_name)
            df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
        else:
            df = pd.DataFrame([entry])

        df.to_csv(file_name, index=False)
        st.success("📝 Your entry has been saved!")

# Mood Trend Graph
st.markdown("---")
st.subheader("📊 Mood Trend Over Time")

if os.path.exists(file_name):
    df = pd.read_csv(file_name)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    fig, ax = plt.subplots()
    ax.plot(df["timestamp"], df["mood_score"], marker="o", linestyle="-", color="purple")
    ax.set_xlabel("Date")
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b %d'))
    fig.autofmt_xdate()
    ax.set_ylabel("Mood Score")
    ax.set_title("Your Mood Over Time")
    ax.grid(True)
    st.pyplot(fig)
else:
    st.info("📁 No journal entries yet. Add some to see your mood trend!")

# Show Past Entries
st.markdown("---")
st.subheader("📔 Your Past Journal Entries")

if os.path.exists(file_name):
    st.dataframe(df[["timestamp", "entry", "mood_score"]].sort_values(by="timestamp", ascending=False).head(5))
else:
    st.info("No past entries found yet.")

# Download Journal
st.markdown("---")
st.subheader("📥 Download Your Journal")

if os.path.exists(file_name):
    with open(file_name, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{username}_journal.csv">Download Journal CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

