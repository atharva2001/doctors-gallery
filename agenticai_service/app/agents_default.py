from langchain_core.messages import AIMessage
# from agents import comms_agent
from .agent_nodes import comms_agent
# For agents in the crew 
def crew_nodes(state, crew_member, name):
    
    input = {'messages': [state['messages'][-1]], 'agent_history' : state['agent_history']}
    result = crew_member.invoke(input)

    return {"agent_history": [AIMessage(content= result["output"], additional_kwargs= {'intermediate_steps' : result['intermediate_steps']}, name=name)]}

def comms_node(state):
    input = {'messages': [state['messages'][-1]], 'agent_history' : state['agent_history']}
    result = comms_agent.invoke(input)
    return {"messages": [result]}