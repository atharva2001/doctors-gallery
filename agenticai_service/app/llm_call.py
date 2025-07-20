from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

import os 
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
                    model='gemini-2.5-flash',
                    temperature=0.0,
                    api_key=os.environ["GEMINI_API_KEY"],
                    
                    )

# llm = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0.0,
#     api_key=os.environ["OPENAI_API_KEY"],
# )

# llm = ChatAnthropic(
#     model="claude-3-5-sonnet-latest",
#     temperature=0.0,
#     api_key=os.environ["ANTROPHIC_KEY"],
# )


