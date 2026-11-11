"""All tools the agent may call, one file per tool."""

from app.tools.assign_ticket import assign_ticket
from app.tools.create_ticket import create_ticket
from app.tools.find_similar_tickets import find_similar_tickets
from app.tools.get_employee_profile import get_employee_profile
from app.tools.get_ticket_status import get_ticket_status
from app.tools.request_approval import request_approval
from app.tools.search_knowledge_base import search_knowledge_base
from app.tools.update_ticket import update_ticket

TOOLS = [
    search_knowledge_base,
    get_employee_profile,
    find_similar_tickets,
    create_ticket,
    get_ticket_status,
    update_ticket,
    assign_ticket,
    request_approval,
]
