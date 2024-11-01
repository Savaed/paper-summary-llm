import json
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

from rich.progress import Progress
from rich.status import Status

from search_papers import Config, get_search_intervals


class OllamaError(Exception): ...


def check_ollama() -> None:
    if not shutil.which("ollama"):
        raise OllamaError(
            "Ollama executable not found. Please install it. More info: https://ollama.com/download"
        )

    _, stderr = subprocess.Popen(
        ["ollama", "list"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()

    if stderr:
        raise OllamaError(
            "Ollama deamon is not started. Start it using: 'systemctl start ollama'"
        )


def check_model(model: str) -> None:
    _, stderr = subprocess.Popen(
        ["ollama", "show", model],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()

    if stderr:
        status = Status(f"Downloading {model}...")
        status.start()

        _, _ = subprocess.Popen(
            ["ollama", "pull", model],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()
        status.stop()

    print(f"[INFO] Model {model} downloaded")


def main() -> int:
    check_ollama()
    (start, end), _ = get_search_intervals()
    papers = json.loads(
        (
            Path.home()
            / f"papers/{start.strftime('%d-%m-%Y')}__{end.strftime('%d-%m-%Y')}.json"
        ).read_text()
    )
    template = (Path(__file__).parent / "template.tmpl").read_text()
    config: Config = json.loads((Path(__file__).parent / "config.json").read_text())
    output_filepath = Path.home() / "papers" / "summary.md"

    model = config["model"]

    _, stderr = subprocess.Popen(
        ["ollama", "show", model],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()

    if stderr:
        status = Status(f"Downloading {model}...")
        status.start()

        _, _ = subprocess.Popen(
            ["ollama", "pull", model],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()
        status.stop()

    with open(output_filepath, "a") as f:
        with Progress() as bar:
            summarizing_task_id = bar.add_task(
                "Summarizing papers...", total=len(papers)
            )

            for paper in papers:
                prompt = template.replace("{abstract}", paper["abstract"])

                process = subprocess.Popen(
                    ["ollama", "run", config["model"], prompt],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )
                output, _ = process.communicate()

                if not output.startswith("summary:"):
                    output = f"summary: {output}"

                pattern = r"summary:\s*(.+?)\s*\n\nkeywords:\s*((?:[^,\n]+(?:,\s*)?)+)"
                match = re.search(pattern, output, re.DOTALL)

                if not match:
                    continue

                summary = match.group(1).strip()
                keywords = ", ".join([k.strip() for k in match.group(2).split(",")])

                text = f"""
                # {paper['title']}

                > **{paper['authors']} ({paper['published']})** 

                {summary}

                *keywords: {keywords}*

                {paper['link']}
                """

                f.write(textwrap.dedent(text))
                bar.advance(summarizing_task_id)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OllamaError as ex:
        print(f"[ERROR] {ex}")
    except KeyboardInterrupt:
        print("[INFO] Received CTRL+C signal. Quiting...")
