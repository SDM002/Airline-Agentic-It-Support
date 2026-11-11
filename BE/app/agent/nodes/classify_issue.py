"""classify_issue node: the LLM reads the employee's first message and returns its category, priority, team and airport.
Runs once per chat; the result is saved in the state for the next nodes.
"""

from pathlib import Path

from langchain.messages import SystemMessage
from pydantic import BaseModel, Field

from app.agent.state import AgentState
from app.config.settings import settings
from app.core.domain import Category, Priority, Team
from app.core.llm_client import llm
from app.services import employee_service

PROMPT = (Path(__file__).parents[2] / "prompts" / "classify_issue.txt").read_text().format(
    app_name=settings.APP_NAME, airline_name=settings.AIRLINE_NAME
)


# Output format the LLM must return (only the allowed categories, priorities and teams)
class IssueClassification(BaseModel):
    category: Category
    priority: Priority
    team: Team
    airport: str = Field(description="IATA airport code, or UNKNOWN")
    reason: str = Field(description="One short sentence: why this category, team and priority")


# LLM that answers with an IssueClassification instead of free text
classifier_llm = llm.with_structured_output(IssueClassification)


# Classify the issue; fall back to the employee's work location when no airport is mentioned
async def classify_issue(state: AgentState) -> dict:
    result = await classifier_llm.ainvoke([SystemMessage(PROMPT), *state["messages"]])
    if result.airport == "UNKNOWN":
        employee = await employee_service.get_employee(state["employee_id"])
        result.airport = employee["location"]
    return result.model_dump()
