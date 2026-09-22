from google import genai
from google.genai import types
from .config import settings

_client = genai.Client(api_key=settings.gemini_api_key)

def answer_with_gemini(question, chunks):
    context = "\n\n".join(
        f"[SOURCE {i}] {c.path}:{c.start_line}-{c.end_line}\n"
        f"```{c.language}\n{c.content}\n```"
        for i,c in enumerate(chunks,1)
    )

    prompt = f"""You are RepoMind, an AI codebase assistant.

Answer the user's question using ONLY the supplied repository context.
If the context is insufficient, say so clearly.
Never invent files, functions, APIs, or behavior.
Explain code accurately and concisely.
Cite relevant evidence using [SOURCE N].

USER QUESTION:
{question}

REPOSITORY CONTEXT:
{context}
"""

    response = _client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=1800
        )
    )
    return response.text or "Gemini returned an empty response."
