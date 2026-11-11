"""Business vocabulary (categories, priorities, teams, statuses, levels) as Literal types, so the LLM, tools, API and frontend accept only these values."""

from typing import Literal

# Issue type, chosen by classify_issue
Category = Literal[
    "Check-in Application",
    "Crew Scheduling",
    "ERP",
    "Network",
    "Email / M365",
    "Printer",
    "Barcode Scanner",
    "Access Request",
    "Other",
]

# Urgency: P1 airport-wide outage ... P4 access request or question
Priority = Literal["P1", "P2", "P3", "P4"]

# Support team a ticket is routed to
Team = Literal[
    "Application Support",
    "Network Support",
    "Hardware Support",
    "IT Support",
    "Identity & Access Management",
]

# Ticket lifecycle
Status = Literal["open", "in-progress", "awaiting-approval", "resolved", "closed"]

# Support level an engineer works at
Level = Literal["L1", "L2"]
