"""search_knowledge node (RAG): finds the best matching SOP and policy sections in Pinecone for the employee's issue.
Always runs before the agent uses any MongoDB tool, so answers are based on the airline's own documents.
"""

from langchain.messages import HumanMessage

from app.agent.state import AgentState
from app.services import knowledge_service


# Search the knowledge base with the latest employee message and the classified category
async def search_knowledge(state: AgentState) -> dict:
    issue = next(m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage))
    return {"knowledge": await knowledge_service.search(issue, state["category"])}
