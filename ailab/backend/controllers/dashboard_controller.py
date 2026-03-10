class DashboardController:
    def get_dashboard(self) -> dict:
        return {
            "hero_title": "Лаборатория идей",
            "hero_subtitle": "Локальный центр исследования проблем, ниш и продуктовых гипотез.",
            "trends": ["AI tools", "developer tools", "automation", "productivity"],
        }
