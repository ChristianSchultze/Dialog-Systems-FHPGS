import ollama


def make_llm():
    """Create an LLM callable that runs Ollama locally"""
    def llm(instructions: str, prompt: str, model: str = "llama3") -> str:
        response = ollama.chat(
            model=model,
            messages=[{"role": "system", "content": instructions}, {"role": "user", "content": prompt}],
            options={"num_ctx": 8192}
        )
        return response['message']['content'].strip()

    return llm