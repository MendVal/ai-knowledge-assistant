class FakeLLMProvider:
    """Proveedor falso para pruebas: no usa red ni consume cuota."""

    def __init__(
        self,
        answer: str = "respuesta de prueba",
        error: Exception | None = None,
    ):
        self.answer = answer
        self.error = error
        self.calls: list[dict] = []

    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        top_p: float = 1.0,
        max_tokens: int = 300,
    ) -> str:
        self.calls.append(
            {
                "messages": messages,
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens,
            }
        )

        if self.error:
            raise self.error

        return self.answer