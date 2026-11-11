"""classify_issue node: decides the issue's category, priority, team and airport."""

from pathlib import Path

from langchain.messages import SystemMessage
from pydantic import BaseModel, Field

from app.agent.state import AgentState
from app.core.domain import Category, Priority, Team
from app.core.llm_client import llm
from app.services import employee_service

PROMPT = (Path(__file__).parents[2] / "prompts" / "classify_issue.txt").read_text()


class IssueClassification(BaseModel):
    category: Category
    priority: Priority
    team: Team
    airport: str = Field(description="IATA airport code, or UNKNOWN")
    reason: str = Field(description="One short sentence: why this category, team and priority")


classifier_llm = llm.with_structured_output(IssueClassification)


async def classify_issue(state: AgentState) -> dict:
    result = await classifier_llm.ainvoke([SystemMessage(PROMPT), *state["messages"]])
    if result.airport == "UNKNOWN":
        # Employee did not say where they are: use their work location from MongoDB
        employee = await employee_service.get_employee(state["employee_id"])
        result.airport = employee["location"]
    return result.model_dump()
