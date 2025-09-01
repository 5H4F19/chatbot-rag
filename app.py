# app.py
"""Minimal FastAPI wiring for the chatbot.

This file only wires the RuleBasedFlow and RAGService and exposes two endpoints:
- POST /chat: checks rule-based triggers, otherwise runs RAGService.answer
- POST /chatbot: simulated external endpoint used when a trigger fires

Ensure dependencies are installed before running the app.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rule_based_flow import RuleBasedFlow
from rag_service import RAGService
import httpx


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
        try:
            # Call the external /chatbot API
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:8000/chatbot", json={
                    "user_id": req.user_id,
                    "trigger_id": trigger_id
                })
                response_data = response.json()
            return {
                "triggered": True,
                "trigger_id": trigger_id,
                "matched_keyword": matched_kw,
                "answer": response_data.get("message", "External API call successful.")
            }
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to call external API: {e}")

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
