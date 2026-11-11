"""Guardrail rules: what is blocked, redacted or removed, and what the employee is told. All deterministic (no LLM calls).

PII detection uses LangChain's own detectors (the ones behind PIIMiddleware).
"""

import re

from langchain.agents.middleware.pii import apply_strategy, detect_credit_card, detect_email

from app.config.settings import settings

# --- Input: messages that must never reach the LLM or be stored

# "my password is abc123", "OTP: 482913", "pin = 4321"
SECRET_SHARED = re.compile(r"\b(password|passcode|pwd|pin|otp|mfa code)\b\s*(is|was|=|:)\s*\S+", re.IGNORECASE)

# Attempts to change the agent's instructions
PROMPT_INJECTION = re.compile(
    r"ignore (all |any )?(the )?(previous|prior|above|earlier) instructions"
    r"|disregard (all |any )?(the )?(previous |prior |above )?instructions"
    r"|you are now\b|developer mode|jailbreak"
    r"|(reveal|show|print) (me )?(your|the) (system )?(prompt|instructions)",
    re.IGNORECASE,
)

SECRET_REMOVED = "[message removed by guardrail: it contained a password or code]"

SECRET_REPLY = (
    "For your security, please never share passwords or MFA codes in chat. IT will never ask for them. "
    "I did not store that message. Please describe the problem without the password."
)
INJECTION_REPLY = f"I can only help with {settings.AIRLINE_NAME} IT support issues. Please describe the IT problem you are facing."

# --- Output: what the agent must never tell an employee

# Steps reserved for IT engineers in the SOPs
IT_ONLY_STEP = re.compile(r"IT only", re.IGNORECASE)

# The agent asking the employee to hand over a secret
ASKS_FOR_SECRET = re.compile(
    r"\b(share|send|tell|give|provide)\b( me| us)?[^.\n]{0,25}\b(password|otp|mfa code|verification code)\b"
    r"|what is your (password|otp|mfa code|pin)",
    re.IGNORECASE,
)

SAFE_REPLY = "I can't ask for passwords or MFA codes. Please describe the problem, and IT will verify your identity securely if needed."

# --- PII (both directions): redacted with LangChain's detectors

PII_DETECTORS = [detect_email, detect_credit_card]


def safe_to_store(text: str) -> str:
    """The version of an employee message that may be stored outside the chat (e.g. as a conversation title)."""
    if SECRET_SHARED.search(text):
        return SECRET_REMOVED
    return redact_pii(text)[0]


def redact_pii(text: str) -> tuple[str, list[str]]:
    """Returns the text with emails and card numbers replaced by [REDACTED_...], and the PII types found."""
    found = []
    for detect in PII_DETECTORS:
        matches = detect(text)
        if matches:
            found.append(matches[0]["type"])
            text = apply_strategy(text, matches, "redact")
    return text, found
