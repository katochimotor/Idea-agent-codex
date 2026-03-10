from backend.services.text_cleaner import clean_text


class ExtractorAgent:
    def run(self, discussions: list[dict]) -> list[dict]:
        problems = []
        for item in discussions:
            cleaned = clean_text(item["text"])
            problems.append(
                {
                    "problem_statement": cleaned,
                    "source": item["platform"],
                    "url": item["url"],
                }
            )
        return problems
