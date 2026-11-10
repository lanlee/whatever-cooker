#!/usr/bin/env python3
"""Stage only public website assets, never repository or deployment credentials."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist"


def build():
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    for name in ("index.html", "global.css", "whatever-cooker.png", "robots.txt",
                 "sitemap.xml", "65fde1274feecdeaa8521d523a4b9edd.txt",
                 "blog", "content", "protein-plate"):
        source = ROOT / name
        if source.is_dir():
            shutil.copytree(source, OUTPUT / name)
        else:
            shutil.copy2(source, OUTPUT / name)
    return OUTPUT


if __name__ == "__main__":
    print(build())
