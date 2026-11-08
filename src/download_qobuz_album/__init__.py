import shlex
import os
import re
from functools import cache
from pathlib import Path
from typing import NamedTuple, Self

import backoff
import typer
from bs4 import BeautifulSoup, Tag
from httpx2 import Client, HTTPError, Request
from tqdm import tqdm


def load_soup(path: Path):
    return BeautifulSoup(path.read_text())


class ValidationLink(NamedTuple):
    filename: str
    url: str

    @classmethod
    def from_link_el(cls, el: Tag) -> Self:
        return cls(
            filename=el.parent.parent.td.text,  # type: ignore
            url=el["data-uri"].replace("/xx", "/6"),  # type: ignore
        )


def links(soup: BeautifulSoup) -> list[ValidationLink]:
    return [
        ValidationLink.from_link_el(x)
        for x in soup.find_all("a", id=re.compile("tracks_id.*"))
    ]


@cache
def cookie() -> str:
    return os.environ["COOKIE"]


class ValidationRequest(NamedTuple):
    filename: str
    request: Request


def requests(links: list[ValidationLink]) -> list[ValidationRequest]:
    return [
        ValidationRequest(
            x.filename,
            Request(
                method="GET",
                url=f"https://www.qobuz.com/{x.url}",
                headers={"Cookie": cookie(), "Accept": "application/json"},
            ),
        )
        for x in links
    ]


class DownloadLink(NamedTuple):
    filename: str
    url: str

    def format(self) -> str:
        return f"curl {shlex.quote(self.url)} -o {shlex.quote(self.filename)}.flac"


@backoff.on_exception(backoff.expo, HTTPError, max_tries=3)
def resolve(client: Client, request: ValidationRequest) -> DownloadLink:
    resp = client.send(request.request).raise_for_status().json()
    return DownloadLink(request.filename, resp["url"])


app = typer.Typer()


@app.command()
def main(html: Path, outf: Path) -> None:
    soup = load_soup(html)
    validation_links = links(soup)
    validation_requests = requests(validation_links)
    client = Client()

    download_links = [
        resolve(client, request)
        for request in tqdm(validation_requests, desc="Resolving")
    ]
    outf.write_text("\n".join(x.format() for x in download_links))


if __name__ == "__main__":
    app()
