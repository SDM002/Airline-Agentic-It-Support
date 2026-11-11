"""The fixed business values. Used by the agent, the tools and the API so they always agree."""

from typing import Literal

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

Priority = Literal["P1", "P2", "P3", "P4"]

Team = Literal[
    "Application Support",
    "Network Support",
    "Hardware Support",
    "IT Support",
    "Identity & Access Management",
]

Status = Literal["open", "in-progress", "awaiting-approval", "resolved", "closed"]

Level = Literal["L1", "L2"]
