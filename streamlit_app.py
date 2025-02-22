# streamlit_app.py
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Text to SQL")

st.markdown("# Text to SQL - PagilaDB🤖")
st.markdown('''Your friendly assistant for converting natural language queries into SQL statements!
               Ask questions about the Pagila DVD rental database.''')

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Predefined queries
# Update the predefined_queries list
predefined_queries = [
    'List the top 10 most rented movies with their rental counts',
    'Calculate total revenue for each movie category',
    'Find customers who have spent more than $150 total',
    'Show all movies in the Action category with their rental rates',
]

st.markdown("### Predefined Queries")
for query in predefined_queries:
    if st.button(query):
        st.session_state.predefined_query = query

st.markdown("### Enter Your Question")
question = st.text_input("Input: ", key="input", value=st.session_state.get('predefined_query', ''))

if st.button("Submit"):
    response = requests.post("http://localhost:8000/query", 
                           json={"question": question})
    if response.status_code == 200:
        data = response.json()
        st.markdown("## Generated SQL Query")
        st.code(data['query'], language='sql')
        
        st.markdown("## Query Results")
        df = pd.DataFrame(data['result'])
        st.dataframe(df)

        # Update chat history
        st.session_state.chat_history.append(f"👨‍💻: {question}")
        st.session_state.chat_history.append(f"🤖: {data['query']}")
    else:
        st.error(f"Error: {response.text}")

    st.session_state.pop('predefined_query', None)

st.markdown("## Chat History")
for message in st.session_state.chat_history:
    st.text(message)

if st.button("Clear History"):
    st.session_state.chat_history = []
    st.success("Chat history cleared!")
