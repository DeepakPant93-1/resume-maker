from langchain_core.messages import AIMessage

from app.core.llm import ModelFactory

message_text = ModelFactory.message_text


def test_message_text_handles_string_content():
    assert message_text(AIMessage(content="ok")) == "ok"


def test_message_text_handles_gemini_style_parts():
    parts = [{"type": "text", "text": "ok", "extras": {"signature": "abc"}}]
    assert message_text(AIMessage(content=parts)) == "ok"
