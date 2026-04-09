from langchain_groq import ChatGroq
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")
# ques = "who is pm of india"
# ans = llm.invoke(ques)
# print(ans.content)

st.title("🤖 Aians - AI QnA Bot")
st.markdown("My QnA Bot with langchain and Gemini")


if "messages" not in st.session_state:
    st.session_state.messages = []
    
for i in st.session_state.messages:
    role = i["role"]
    content = i["content"]
    st.chat_message(role).markdown(content)


query = st.chat_input("Aians🤖 can answer anything!!try it out...🤷‍♂️")

if query:
    print(query)
    
    st.session_state.messages.append({"role":"user", "content":query})
    st.chat_message("user").markdown(query)         #? user
    res = llm.invoke(query)
    st.chat_message("ai").markdown(res.content)     #? ai 
    st.session_state.messages.append({"role":"ai", "content":res.content})
    
# while True:

#     query = input("User: ")

#     if query.lower() in ["stop", "quit", "bye", "exit"]:
#         print("OK...😁👍")
#         break

#     res = llm.invoke(query)
#     print("AI:  ", res.content, "\n")
