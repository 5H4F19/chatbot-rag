# app.py
"""Minimal FastAPI wiring for the chatbot.

This file only wires the RuleBasedFlow and RAGService and exposes two endpoints:
- POST /chat: checks rule-based triggers, otherwise runs RAGService.answer
- POST /chatbot: simulated external endpoint used when a trigger fires

Ensure dependencies are installed before running the app.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from rule_based_flow import RuleBasedFlow
from rag_service import RAGService


app = FastAPI()


# Instantiate services at import; errors will be raised early if deps are missing
rule_flow = RuleBasedFlow()
rag_service = RAGService()


class ChatRequest(BaseModel):
    user_id: str
    question: str


class ChatbotRequest(BaseModel):
    user_id: str
    trigger_id: str


@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    trigger_id, matched_kw = rule_flow.check_trigger(req.question)
    if trigger_id:
        # In production you'd POST to the external service here; we simulate it.
        return {
            "triggered": True,
            "trigger_id": trigger_id,
            "matched_keyword": matched_kw,
            "answer": f"Rule-based flow triggered for keyword '{matched_kw}'. (Simulated external API call.)"
        }

    answer, sources = rag_service.answer(req.question)
    return {
        "triggered": False,
        "answer": answer,
        "sources": sources
    }


@app.post("/chatbot")
async def chatbot_endpoint(req: ChatbotRequest):
    return {
        "user_id": req.user_id,
        "trigger_id": req.trigger_id,
        "message": f"Simulated external API response for trigger_id {req.trigger_id}"
    }
