#changegit 
from langchain_ollama import ChatOllama
from amadeus import Client, ResponseError
from langchain.agents import initialize_agent, load_tools
from langchain.agents import AgentType
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.agents import initialize_agent
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
LANGCHAIN_API_KEY='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'

# %%
llm = ChatOllama(
    model="llama3-groq-tool-use",
    temperature=0,
)

# %%


class FlightSearchSchema(BaseModel):
    originLocationCode: str = Field(..., description="First airport code")
    destinationLocationCode: str = Field(..., description="Second airport code")
    departureDate: str = Field(..., description="Date of departure")
    adults: int = Field(..., description="Number of adults")

@tool("flight_search-tool", args_schema=FlightSearchSchema, return_direct=True)
def flight_search(query: str):
    """
    Searches flights based on the provided parameters.
    The query should include origin, destination, departure date, and number of adults.
    """
    import pdb;pdb.set_trace()
    # Parse the query string into individual parameters
    params = {}
    for param in query.split(','):
        key, value = param.strip().split(':')
        params[key.strip()] = value.strip()
    
    try:
        # Validate and create FlightSearchSchema instance
        search_params = FlightSearchSchema(
            originLocationCode=params['originLocationCode'],
            destinationLocationCode=params['destinationLocationCode'],
            departureDate=params['departureDate'],
            adults=int(params['adults'])
        )
        
        amadeus = Client(
            client_id='5G1CNwDfyBXnZuKLoAkicMoqgEqn26Ex',
            client_secret='0yDZezKgpgNP215B'
        )
        
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=search_params.originLocationCode,
            destinationLocationCode=search_params.destinationLocationCode,
            departureDate=search_params.departureDate,
            adults=search_params.adults
        )
        return str(response.data)  # Convert to string for easier handling
    except KeyError as e:
        return f"Missing parameter: {str(e)}"
    except ValueError as e:
        return f"Invalid parameter value: {str(e)}"
    except ResponseError as error:
        return f"API error: {error.response.body}"

# %%
flight_search = Tool(
    name='flight_search',
    func=flight_search,
    description="""
    Searches for flights based on provided parameters. 
    Input should be a string with comma-separated key-value pairs: 
    'originLocationCode: XXX, destinationLocationCode: YYY, departureDate: YYYY-MM-DD, adults: N'
    Convert city names to airport codes before using. 
    If any required information is missing, ask the user for it.
    """
)

# %%

tools = [flight_search]


# create our agent
agent = create_react_agent(
    tools=tools,
    llm=llm,
    prompt= hub.pull("hwchase17/react",api_key = LANGCHAIN_API_KEY)+"convert all airport names to respective airport codes"  
)

# %%
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,handle_parsing_errors=True)


# %%
import pdb;pdb.set_trace()
agent_executor.invoke({"input":"give me top 5 flights from jfk to mumbai on 25th august 2024 "})

# %%



