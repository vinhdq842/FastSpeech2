import streamlit as st

st.header("Demo emotional TTS")
st.text_input("Enter your text here")
a = 0
if st.button("Submit"):
    a+=1
    st.write(a)


st.subheader("Neutral:")
st.subheader("Happy:")
st.subheader("Angry:")
st.subheader("Sad:")
