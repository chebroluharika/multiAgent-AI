import streamlit as st
import time

# Custom CSS for fancy styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f6;
    }
    h1 {
        color: #4a90e2;
        text-align: center;
        font-family: 'Arial', sans-serif;
    }
    .stButton button {
        background-color: #4a90e2;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #357abd;
    }
    .stTextInput input {
        border-radius: 12px;
        padding: 10px;
        border: 1px solid #4a90e2;
    }
    .stProgress > div > div > div {
        background-color: #4a90e2;
    }
    .stAlert {
        border-radius: 12px;
        padding: 16px;
        background-color: #e6f7ff;
        border: 1px solid #4a90e2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and header
st.title("✨ Fancy Streamlit UI ✨")
st.header("Welcome to the Ultimate Streamlit Experience")

# Columns for layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Interactive Widgets")
    name = st.text_input("Enter your name", placeholder="John Doe")
    age = st.slider("Select your age", 0, 100, 25)
    if st.button("Submit"):
        with st.spinner("Processing..."):
            time.sleep(2)  # Simulate processing
            st.success(f"Hello, {name}! You are {age} years old.")

with col2:
    st.subheader("Visualizations")
    progress_bar = st.progress(0)
    status_text = st.empty()
    for i in range(101):
        progress_bar.progress(i)
        status_text.text(f"Progress: {i}%")
        time.sleep(0.02)  # Simulate progress

# Expander for additional content
with st.expander("Click here for more info"):
    st.write("This is a fancy Streamlit app designed to showcase advanced UI features.")
    st.image("https://via.placeholder.com/600x200.png?text=Fancy+Image", use_column_width=True)

# Custom HTML for a fancy footer
st.markdown(
    """
    <div style="text-align: center; padding: 16px; background-color: #4a90e2; color: white; border-radius: 12px;">
        <p>Made with ❤️ by Streamlit | Powered by Python</p>
    </div>
    """,
    unsafe_allow_html=True,
)