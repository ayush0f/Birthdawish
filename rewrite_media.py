import json
import re
from pathlib import Path


def resolve_url(url_by_name: dict[str, str], filename: str) -> str | None:
    if filename in url_by_name:
        return url_by_name[filename]

    low = filename.lower()
    if low.endswith(".jpg"):
        return url_by_name.get(filename[:-4] + ".jpeg") or url_by_name.get(filename[:-4] + ".png")
    if low.endswith(".jpeg"):
        return url_by_name.get(filename[:-5] + ".jpg") or url_by_name.get(filename[:-5] + ".png")
    if low.endswith(".png"):
        return url_by_name.get(filename[:-4] + ".jpg") or url_by_name.get(filename[:-4] + ".jpeg")
    return None


def main() -> int:
    root = Path(__file__).resolve().parent
    rows = json.loads(root.joinpath("selected-rows.json").read_text(encoding="utf-8"))

    url_by_name: dict[str, str] = {}
    if isinstance(rows, list):
        for r in rows:
            if isinstance(r, dict) and isinstance(r.get("name"), str) and isinstance(r.get("url"), str):
                url_by_name[r["name"]] = r["url"]

    html_path = root / "index.html"
    html = html_path.read_text(encoding="utf-8")

    missing: set[str] = set()
    replaced = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal replaced
        filename = match.group(1)
        url = resolve_url(url_by_name, filename)
        if not url:
            missing.add(filename)
            return match.group(0)
        replaced += 1
        return f'src="{url}"'

    # Replace src="memories/<file>" and src="messages/<file>"
    html2 = re.sub(r'src="(?:memories|messages)/([^"?#]+)"', repl, html)
    html_path.write_text(html2, encoding="utf-8")

    print(f"replaced={replaced}")
    if missing:
        print("missing_files=")
        for x in sorted(missing):
            print(f" - {x}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

