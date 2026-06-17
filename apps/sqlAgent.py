from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
import streamlit as st

load_dotenv()

# ? === AI based Task Management Application with Real Database ===

"""

1-> there will be one interface => where we can prompt to llm and based on our instructions 
    our AI agent => in real time do query to SQL database 
    
2-> means, our ai agent will perform sql query operations ( filter , search , add , delete , update ...everything) => based on our need  

3-> In langchain docs -> integrations -> tools/toolkits -> database -> we can use MCP Toolbox ||  SQLDatabase Toolkit for any SQL operations

4-> what we needed : 

#*** DB , LLM , tools , create agent , system prompt

5-> sqlite => provided by python => it is a database 

"""


db = SQLDatabase.from_uri("sqlite:///tasks.db")

db.run("""
       
       CREATE TABLE IF NOT EXISTS tasks (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           title TEXT NOT NULL,
           description TEXT,
           status TEXT CHECK (status IN ('pending' , 'in_progress' , 'completed')) DEFAULT 'pending',
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       );     
""")

print(" DB Created")

llm = ChatGroq(model="openai/gpt-oss-20b")
toolkit = SQLDatabaseToolkit(db=db , llm= llm)

#now this toolkit => will give us tool

tools = toolkit.get_tools()

# for t in tools:
#     print(t.name)
# => itne saare tools hain available : 
"""
    #* sql_db_query => llm use this when llm wants to do final opertaion
    #* sql_db_schema => use to fetch the schema of database
    #* sql_db_list_tables => this will gives the list of all tables present in upur database
    #* sql_db_query_checker => this is always run first before sql_db_query -> to check the main query is correct or not which id made by llm
"""


tavily_search_tool = TavilySearch(
    max_results=3,
    topic="general"
    )

# agent = create_agent(
#     model=llm,
#     tools=[tavily_search_tool],
#     system_prompt="You are a assitant for task management with database",
#     checkpointer=InMemorySaver(),
# )

system_prompt = """
You are a task management assistant that interacts with a SQL database containing a 'tasks' table. 

TASK RULES:
1. Limit SELECT queries to 10 results max with ORDER BY created_at DESC
2. After CREATE/UPDATE/DELETE, confirm with SELECT query
3. If the user requests a list of tasks, present the output in a structured table format to ensure a clean and organized display in the browser."

CRUD OPERATIONS:
    CREATE: INSERT INTO tasks(title, description, status)
    READ: SELECT * FROM tasks WHERE ... LIMIT 10
    UPDATE: UPDATE tasks SET status=? WHERE id=? OR title=?
    DELETE: DELETE FROM tasks WHERE id=? OR title=?

Table schema: id, title, description, status(pending/in_progress/completed), created_at."""
   
#* now we have everything => we are creating a agent now:

@st.cache_resource              #? is decorator lagane se => hamara agent baar baar refresh nhi hoga stremlit ka page refresh honr pr
def get_agent():
    agent = create_agent(
        model= llm, 
        tools= tools,
        system_prompt= system_prompt,
        checkpointer= InMemorySaver()
    )
    return agent

agent = get_agent()


#! uncomment this code => and run it in cli command line interface

# agent = create_agent(
#         model= llm, 
#         tools= tools,
#         system_prompt= system_prompt,
#         checkpointer= InMemorySaver()
#     )

# while True:
#     query = input("User: ")
#     response = agent.invoke(
#         {
#             "messages":[   #* messages is list of dictionary
#                 {
#                     "role":"user",
#                     "content":query   #* content is Users query | question for llm
#                 }  
#             ]
#         },#* as we are using "memory" -> we have to pass a key named = "configurable" -> jiski value v dictionary hogi and iski key hogi "thread_id" => and this thread_id must be unique
#         {
#             "configurable": {
#                 "thread_id":"1"
#             }
#         }
#     )
    
#     result = response["messages"][-1].content #? agent se jab v response milta hai vo hota hai ek dictionary ke form mein 
#     #* and us dict => meim key ka naam hota hai "messages" 
#     #? and us messages ki value hoti hai => list of all the steps => agent final answer laane se pehle jo jo step lrta hai vo sara stepo isme hota hai => tool call krna , verify krna this that => uske baad
#     #? usme se jo final response hota hai vo list ki last index pr hota hai isliye we do => .[-1] and usme se we only take content 
    
#     print(f"AI : {result}")

#! now from cli => web interface

#! in this commented work below => when we ask new question to llm it is replaced by the old one => so we cant trach history of converstation

# st.subheader("💻 TaskBot - Manage our database")

# prompt = st.chat_input("Ask me to manage your tasks..")

# if prompt:
#     st.chat_message("user").markdown(prompt)#? we are adding this line to show users each question on web interface before llm would ans
   
#     #! now jab tak response generate ho raha we will create a web loader
    
#     with st.chat_message("ai"):
#         with st.spinner("Processing..."):
#             response = agent.invoke(
#                 {
#                     "messages":[   #* messages is list of dictionary
#                         {
#                             "role":"user",
#                             "content":prompt   #* content is Users query | question for llm
#                         }  
#                     ]
#                 },#* as we are using "memory" -> we have to pass a key named = "configurable" -> jiski value v dictionary hogi and iski key hogi "thread_id" => and this thread_id must be unique
#                 {
#                     "configurable": {
#                         "thread_id":"1"
#                     }
#                 }
#             )
            
#             result = response["messages"][-1].content
#             st.markdown(result)

#! the code for tracking convo history : 
st.subheader("💻 TaskBot - Manage our database")

if "messages" not in st.session_state:
    st.session_state.messages = []    #? we created a list first for storing each user query and ai response then we will do appending work later


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])
    

prompt = st.chat_input("Ask me to manage your tasks..")
if prompt:
    st.chat_message("user").markdown(prompt)#? we are adding this line to show users each question on web interface before llm would ans
   
    st.session_state.messages.append(
        {
            "role":"user",
            "content":prompt
        }
    )   #? => this is done to store the users prompt in list 
    
    
    #! now jab tak response generate ho raha we will create a web loader
    with st.chat_message("ai"):
        with st.spinner("Processing..."):
            response = agent.invoke(
                {
                    "messages":[   #* messages is list of dictionary
                        {
                            "role":"user",
                            "content":prompt   #* content is Users query | question for llm
                        }  
                    ]
                },#* as we are using "memory" -> we have to pass a key named = "configurable" -> jiski value v dictionary hogi and iski key hogi "thread_id" => and this thread_id must be unique
                {
                    "configurable": {
                        "thread_id":"1"
                    }
                }
            )
            
            result = response["messages"][-1].content
            st.markdown(result)
            
            st.session_state.messages.append(
                {
                    "role":"ai",
                    "content":result
                }
            ) #? this is done => to store llm response in list

    