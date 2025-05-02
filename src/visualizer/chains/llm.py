from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from visualizer.tools import complete_python_task

from dotenv import load_dotenv
load_dotenv()


# load prompt
with open("src/visualizer/prompts/main_prompt.md", "r") as f:
    prompt = f.read()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

model = llm.bind_tools(tools=[complete_python_task])

chat_template = ChatPromptTemplate.from_messages([
    ("system", prompt),
    ("placeholder", "{messages}"),
])

# chain
model = chat_template | model 
