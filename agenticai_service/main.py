from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.graph_nodes import graph
from langchain_core.messages import HumanMessage
from pprint import pp
import time
from pydantic import BaseModel

app = FastAPI(
    title="AgenticAI Service",
    description="A service for managing AgenticAI agents and their interactions.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for CORS
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AgenticAI Service!"}


class QueryData(BaseModel):
    query: str
    thread_id: str = "default_thread"

@app.post("/query")
async def query_agent(data: QueryData):
    config = {"configurable": {"thread_id": data.thread_id}}
    
    result = []
    # data = {
    #     "appointment_id": 4,
    #     "patient_id": 2,
    #     "doctor_id": 3,
    #     "slot_id": 3,
    #     "success": "false",
    #     "remarks": "New appointment for this patient."
    #     }
    for s in graph.stream(
        {
            "messages": [
                HumanMessage(content=data.query),
            ],
            "next": "Supervisor",
            "agent_history": [
                HumanMessage(content=""),
            ]
        }, config=config
    ):
        try:
            if "__end__" not in s:
                result.append(s)
        except Exception as e:
            time.sleep(10)

    return (result[-1]["Communicate"]["messages"][0].content)


            



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
    )