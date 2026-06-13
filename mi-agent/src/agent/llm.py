from langchain_openai import ChatOpenAI

from src.config import settings

llm = ChatOpenAI(
    model=settings.openrouter_model,
    base_url=settings.openrouter_base_url,
    api_key=settings.openrouter_api_key,
    temperature=0.3,
    max_tokens=4096,
)
