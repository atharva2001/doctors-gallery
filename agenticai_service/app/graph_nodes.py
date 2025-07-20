import operator
from typing import Annotated, Sequence, TypedDict
import functools
from langchain_core.messages import BaseMessage

from langgraph.graph import StateGraph, END
from .agents_default import crew_nodes, comms_node
from langgraph.checkpoint.memory import InMemorySaver

from .agent_nodes import supervisor_chain, get_agent, creation_agent, member_options


# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str 
    
    agent_history: Annotated[Sequence[BaseMessage], operator.add]


# math_node = functools.partial(crew_nodes, crew_member=math_agent, name="Math Agent")

# text_node = functools.partial(crew_nodes, crew_member=text_agent, name="Text Agent")

# api_node = functools.partial(crew_nodes, crew_member=api_agent, name="API Agent")


get_node = functools.partial(crew_nodes, crew_member=get_agent, name="GetAgent")

creation_node = functools.partial(crew_nodes, crew_member=creation_agent, name="CreationAgent")

# api_node = functools.partial(crew_nodes, crew_member=api_agent, name="API Agent")



workflow = StateGraph(AgentState)

workflow.add_node("Creation Agent", creation_node)
workflow.add_node("Get Agent", get_node)
# workflow.add_node("API Agent", api_nod/e)

workflow.add_node("Communicate", comms_node)
# workflow.add_node("Planner Agent", planner_node)

workflow.add_node("Supervisor", supervisor_chain)



workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x["next"],  # next must match a node name!
    ["Creation Agent", "Get Agent"]  # possible destinations
)
workflow.add_edge('Creation Agent', 'Communicate') # add one edge for the text agent to communicate
workflow.add_edge('Get Agent', 'Communicate') # add one edge for the math agent
workflow.add_edge('Supervisor', END) # add one edge for each of the agents

# The supervisor populates the "next" field in the graph state
# which routes to a node or finishes


# Finally, add entrypoint
# workflow.set_entry_point("Supervisor")
# workflow.add_conditional_edges("Supervisor", lambda x: x["next"], member_options)
# Finally, add entrypoint
workflow.set_entry_point("Supervisor")


checkpointer = InMemorySaver()

graph = workflow.compile(
    # interrupt_before=["Communicate"],
    checkpointer=checkpointer
)
