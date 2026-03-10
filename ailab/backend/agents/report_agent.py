from pathlib import Path

from backend.ai.prompt_templates import IDEA_REPORT_TEMPLATE
from backend.utils.file_writer import write_text_file
from backend.utils.slug_generator import slugify


class ReportAgent:
    def run(self, report_dir: Path, idea: dict) -> Path:
        path = report_dir / f"{slugify(idea['title'])}.md"
        content = IDEA_REPORT_TEMPLATE.format(
            title=idea["title"],
            problem=idea["problem"],
            summary=idea["summary"],
        )
        write_text_file(path, content)
        return path
