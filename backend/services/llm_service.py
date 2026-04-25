from core.llm import llm


SYSTEM_PROMPT = """
Ты помощник преподавателя магистратуры.
Отвечай строго по теме, ясно, кратко, академично.
Если вопрос неоднозначен — уточни.
Если точного ответа не знаешь — не выдумывай.
"""


class LLMService:
    def build_prompt(self, messages: list[dict]) -> str:
        parts = [f"System: {SYSTEM_PROMPT.strip()}"]

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")

        parts.append("Assistant:")
        return "\n".join(parts)

    def generate_answer(self, messages: list[dict]) -> str:
        prompt = self.build_prompt(messages)

        result = llm(
            prompt,
            max_tokens=512,
            temperature=0.7,
            stop=["User:", "System:"],
        )

        return result["choices"][0]["text"].strip()