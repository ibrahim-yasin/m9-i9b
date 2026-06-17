import os
import shutil

from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

def get_llm_client(model: str = "phi3:mini-4k-instruct-q4_K_M"):
    ollama_host = os.environ.get("OLLAMA_HOST")

    # Step 1: OLLAMA_HOST override
    if ollama_host:
        return ChatOllama(model=model, base_url=ollama_host)

    # Step 2: local Ollama
    if shutil.which("ollama") is not None:
        if not _ollama_has_model(model):
            raise OllamaModelMissingError(
                f"Model {model!r} not pulled. Run: ollama pull {model}"
            )
        return ChatOllama(model=model)

    # Step 3: OpenAI fallback
    if os.environ.get("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Step 4: Anthropic fallback
    if os.environ.get("ANTHROPIC_API_KEY"):
        return ChatAnthropic(
            model="claude-3-5-sonnet-latest",
            temperature=0
        )

    # Step 5: fail
    raise NoLLMClientAvailableError(
        "No LLM provider available. Install Ollama (https://ollama.com) "
        f"and run: ollama pull {model}\n"
        "Or set OPENAI_API_KEY / ANTHROPIC_API_KEY in your .env."
    )