from app.ai_reports.prompts import DAILY_TEMPLATE


class AIReportGenerator:
    """Optional AI layer; does not execute trades."""

    def __init__(self, provider: str = "mock", model: str = "gpt-4o-mini") -> None:
        self.provider = provider
        self.model = model

    def generate_daily_report(self, payload: dict) -> str:
        # TODO: plug real providers behind adapter interface.
        if self.provider == "mock":
            return f"[MOCK REPORT - {self.model}]\n" + DAILY_TEMPLATE.format(payload=payload)
        return "TODO: external provider integration"
