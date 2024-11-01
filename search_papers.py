import json
import os
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Literal, TypedDict

import requests


class Config(TypedDict):
    include_terms: list[str]
    union: bool
    exclude_terms: list[str]
    category: str
    max_results: int
    model: str
    days_before: int


config: Config = json.loads((Path(__file__).parent / "config.json").read_text())

SearchableElement = Literal["abs", "all"]


def get_search_intervals() -> tuple[tuple[date, date], tuple[str, str]]:
    end = datetime.now().date()
    end_str = end.strftime("%Y%m%d") + "235900"
    start = end - timedelta(days=config["days_before"])
    start_str = start.strftime("%Y%m%d") + "000000"
    return (start, end), (start_str, end_str)


def create_query(
    include: Iterable[str],
    exclude: Iterable[str],
    union: bool,
    search_include_in: SearchableElement = "abs",
    search_exclude_in: SearchableElement = "abs",
) -> str:
    operator = " AND " if union else " OR "
    include_query = operator.join([f"{search_include_in}: {term}" for term in include])
    exclude_query = " OR ".join([f"{search_exclude_in}: {term}" for term in exclude])

    if exclude_query:
        return f"{include_query} ANDNOT ({exclude_query})"

    return include_query


type PaperData = dict[str, str]


def extract_data(document: str) -> list[PaperData]:
    data: list[PaperData] = []
    root = ET.fromstring(document)

    for element in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
        paper = {}
        paper["title"] = (
            element.find(".//{http://www.w3.org/2005/Atom}title")
            .text.replace("\n", "")
            .replace("  ", " ")
            .strip()
        )

        paper["link"] = element.find(".//{http://www.w3.org/2005/Atom}id").text.replace(
            "\n", ""
        )

        paper["abstract"] = (
            element.find(".//{http://www.w3.org/2005/Atom}summary")
            .text.replace("\n", "")
            .strip()
        )

        published = element.find(
            ".//{http://www.w3.org/2005/Atom}published"
        ).text.replace("\n", "")
        paper["published"] = datetime.fromisoformat(published).strftime("%d.%m.%Y")

        all_authors = [
            author.text.replace("\n", "")
            for author in element.findall(
                ".//{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name"
            )
        ]

        paper["authors"] = (
            f"{all_authors[0]} et al." if len(all_authors) > 1 else all_authors[0]
        )

        data.append(paper)

    return data


def main() -> int:
    (start, end), (start_str, end_str) = get_search_intervals()
    search_query = create_query(
        config["include_terms"],
        config["exclude_terms"],
        config["union"],
    )
    url = f"https://export.arxiv.org/api/query?search_query={search_query}+AND+cat:{config['category']}+AND+submittedDate:[{start_str}+TO+{end_str}]&max_results={config['max_results']}&sortBy=submittedDate&sortOrder=descending"
    print(f"Reqested URL: {url}")
    response = requests.get(url)

    dir_filepath = Path.home() / "papers"

    if not dir_filepath.is_file():
        os.makedirs(dir_filepath)

    filepath = (
        dir_filepath / f"{start.strftime('%d-%m-%Y')}__{end.strftime('%d-%m-%Y')}.json"
    )
    filepath.write_text(json.dumps(extract_data(response.text)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
