from core.llm import llm


SYSTEM_PROMPT = """
Ты помощник преподавателя магистратуры.
Отвечай строго по теме, ясно, кратко, академично.
Если вопрос неоднозначен — уточни.
Если точного ответа не знаешь — не выдумывай.
"""

MAX_CONTEXT_TOKENS = 4096
MAX_OUTPUT_TOKENS = 768
MIN_OUTPUT_TOKENS = 128
SAFETY_MARGIN = 64


class LLMService:
    def build_prompt(self, messages: list[dict]) -> str:
        parts = [f"System: {SYSTEM_PROMPT.strip()}"]

        for msg in messages[-6:]:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")

        parts.append("Assistant:")
        return "\n".join(parts)

    def _calculate_max_tokens(self, prompt: str) -> int:
        prompt_tokens = len(llm.tokenize(prompt.encode("utf-8")))
        available_tokens = MAX_CONTEXT_TOKENS - prompt_tokens - SAFETY_MARGIN

        if available_tokens < MIN_OUTPUT_TOKENS:
            return MIN_OUTPUT_TOKENS

        return min(available_tokens, MAX_OUTPUT_TOKENS)

    def generate_answer(self, messages: list[dict]) -> str:
        prompt = self.build_prompt(messages)
        max_tokens = self._calculate_max_tokens(prompt)

        result = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            stop=["User:", "System:"],
        )

        return result["choices"][0]["text"].strip()

    def stream_answer(self, messages: list[dict]):
        prompt = self.build_prompt(messages)
        max_tokens = self._calculate_max_tokens(prompt)

        for chunk in llm(
            prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            stop=["User:", "System:"],
            stream=True,
        ):
            text = chunk["choices"][0]["text"]
            if text:
                yield text