"""Guardrail rules: what is blocked, redacted or removed, and what the employee is told.
Deterministic (no LLM calls); PII uses LangChain's own detectors.
"""

import re

from langchain.agents.middleware.pii import apply_strategy, detect_credit_card, detect_email

from app.config.settings import settings

# Input: password or code shared, e.g. "my password is abc123"
SECRET_SHARED = re.compile(r"\b(password|passcode|pwd|pin|otp|mfa code)\b\s*(is|was|=|:)\s*\S+", re.IGNORECASE)

# Input: attempts to change the agent's instructions
PROMPT_INJECTION = re.compile(
    r"ignore (all |any )?(the )?(previous|prior|above|earlier) instructions"
    r"|disregard (all |any )?(the )?(previous |prior |above )?instructions"
    r"|you are now\b|developer mode|jailbreak"
    r"|(reveal|show|print) (me )?(your|the) (system )?(prompt|instructions)",
    re.IGNORECASE,
)

# Input: replacement text and replies for blocked messages
SECRET_REMOVED = "[message removed by guardrail: it contained a password or code]"
SECRET_REPLY = (
    "For your security, please never share passwords or MFA codes in chat. IT will never ask for them. "
    "I did not store that message. Please describe the problem without the password."
)
INJECTION_REPLY = f"I can only help with {settings.AIRLINE_NAME} IT support issues. Please describe the IT problem you are facing."

# Output: SOP steps reserved for IT engineers
IT_ONLY_STEP = re.compile(r"IT only", re.IGNORECASE)

# Output: the agent asking the employee for a secret
ASKS_FOR_SECRET = re.compile(
    r"\b(share|send|tell|give|provide)\b( me| us)?[^.\n]{0,25}\b(password|otp|mfa code|verification code)\b"
    r"|what is your (password|otp|mfa code|pin)",
    re.IGNORECASE,
)

# Output: reply used instead of a request for a secret
SAFE_REPLY = "I can't ask for passwords or MFA codes. Please describe the problem, and IT will verify your identity securely if needed."

# Both directions: PII types to redact
PII_DETECTORS = [detect_email, detect_credit_card]


# Version of a message that is safe to store outside the chat (e.g. conversation title)
def safe_to_store(text: str) -> str:
    if SECRET_SHARED.search(text):
        return SECRET_REMOVED
    return redact_pii(text)[0]


# Replace emails and card numbers with [REDACTED_...]; return the text and the PII types found
def redact_pii(text: str) -> tuple[str, list[str]]:
    found = []
    for detect in PII_DETECTORS:
        matches = detect(text)
        if matches:
            found.append(matches[0]["type"])
            text = apply_strategy(text, matches, "redact")
    return text, found
