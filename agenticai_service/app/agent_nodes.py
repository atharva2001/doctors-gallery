# Create all the agents


from .llm_call import llm
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate, SystemMessagePromptTemplate

from langchain_core.messages import AIMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from .agent_creation import create_tool_agent

from enum import Enum

from .toolkit import creation_toolkit, get_toolkit


#define output structure
class CommsOutput(BaseModel):
    messages: AIMessage = Field(description = 'Friendly and helpful agent response to the human query')

    class Config:
        arbitrary_types_allowed = True

#create the parser for the chain based on specified output
comms_parser = JsonOutputParser(pydantic_object=CommsOutput)

system_prompt_template = PromptTemplate(

                template= """ You are a talkative and helpful assistant that answers user queries and communicates to user about what the agents have responded. 
                You will summarize and only give the user what they need to know.
                You will also keep track of the agent history and use it to answer the user query.
                            The agent history is as follows: 
                        \n{agent_history}\n""",
                input_variables=["agent_history"],  )

system_message_prompt = SystemMessagePromptTemplate(prompt=system_prompt_template)

prompt = ChatPromptTemplate.from_messages(
    [
        system_message_prompt,
        MessagesPlaceholder(variable_name="messages"),
    ])

comms_agent = (prompt| llm) 

get_agent = create_tool_agent(
    llm, 
    get_toolkit, 
    "You are an get all agent that fetches all the get query appointments and slots from the database. " 
) 


creation_agent = create_tool_agent(
    llm, 
    creation_toolkit, 
    "You are a creation agent that is reponsible for creation of data. Use tools carefully and then create/post the data."
)


members = ["Get Agent", "Creation Agent"]

#create options map for the supervisor output parser.
member_options = {member:member for member in members}

#create Enum object
MemberEnum = Enum('MemberEnum', member_options)

from pydantic import BaseModel

#force Supervisor to pick from options defined above
# return a dictionary specifying the next agent to call 
#under key next.
class SupervisorOutput(BaseModel):
    next: MemberEnum 

system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    " crew of workers:  {members}. Given the following user request, and crew responses"
    " respond with the worker to act next."
    "Each worker will perform a task and respond with their results and status. When finished with the task,"
    "If you require any other information from the user, route to communicate to ask the user for more information."
    " route to communicate to deliver the result to user. Given the conversation and crew history below, who should act next?"
            "Select one of: {options} "
            "\n{format_instructions}\n"
    "Return the result in a processable JSON format for other agents."
)
# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed

# Using openai function calling can make output parsing easier for us
supervisor_parser = JsonOutputParser(pydantic_object=SupervisorOutput)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_history")
       
    ]
).partial(options=str(members), members=", ".join(members), format_instructions = supervisor_parser.get_format_instructions())


supervisor_chain = (
    prompt | llm |supervisor_parser
)


