"""One-time extraction from the owner's read-only frozen Git object database."""

import ast
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = None
COMMIT = "bd50cf7cbba76ccd75517d06037662dff4797b05"


def git(*args):
    return subprocess.check_output(["git", "-C", str(SOURCE), *args])


def write(path, data):
    target = (ROOT / path).resolve()
    assert target.is_relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    Path("\\\\?\\" + str(target)).write_bytes(data)


def adapt(text):
    # Include dotted monkeypatch targets and architecture assertions as well as imports.
    text = re.sub(
        r"^(\s*)(from|import) (engines|models|scraper|utils)(?=[. ])",
        r"\1\2 prospector_engine.\3",
        text,
        flags=re.M,
    )
    return re.sub(r"([\"'])(engines|models|scraper|utils)(?=\.)", r"\1prospector_engine.\2", text)


def main():
    global SOURCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Read-only source CLI Git repository")
    SOURCE = parser.parse_args().source
    if (ROOT / "src/prospector_engine").exists():
        raise SystemExit(
            "Extraction already exists; use audit_provenance.py instead of overwriting it"
        )
    assert git("rev-parse", "refs/tags/v1.0.0^{commit}").decode().strip() == COMMIT
    paths = git("ls-tree", "-r", "--name-only", COMMIT).decode().splitlines()
    inventory = []
    tests = []
    for path in paths:
        core = path.endswith(".py") and (
            path.startswith(("src/engines/", "src/models/", "src/scraper/google_maps/"))
            or path in ("src/utils/parser.py", "src/utils/__init__.py", "src/scraper/__init__.py")
        )
        test = path.startswith(
            ("tests/unit/", "tests/integration/", "tests/e2e/")
        ) and path.endswith(".py")
        if core:
            raw = git("show", f"{COMMIT}:{path}")
            destination = "src/prospector_engine/" + path[4:]
            content = adapt(raw.decode("utf-8"))
            write(destination, content.encode())
            deps = []
            for node in ast.walk(ast.parse(content)):
                if isinstance(node, ast.ImportFrom):
                    deps.append(node.module or "")
                elif isinstance(node, ast.Import):
                    deps.extend(alias.name for alias in node.names)
            inventory.append(
                dict(
                    source=path,
                    commit=COMMIT,
                    destination=destination,
                    source_sha256=hashlib.sha256(raw).hexdigest(),
                    classification="ADAPTADO POR PACKAGING"
                    if content != raw.decode()
                    else "COPIADO SIN CAMBIO FUNCIONAL",
                    dependencies=sorted(set(deps)),
                )
            )
        elif test:
            category = (
                "LIVE_E2E"
                if "/e2e/" in path
                else "CLI_ONLY"
                if "cli" in path or "version" in path
                else "PORTABLE_ONLY"
                if "portable" in path
                else "EXPORT_ONLY"
                if "export" in path or "utils" in path
                else "ENGINE_INTEGRATION"
                if "/integration/" in path
                else "ENGINE_CORE"
            )
            migrated = category in ("ENGINE_CORE", "ENGINE_INTEGRATION", "LIVE_E2E")
            tests.append(dict(source=path, category=category, migrated=migrated))
            if migrated:
                write(path, adapt(git("show", f"{COMMIT}:{path}").decode()).encode())
        elif path.startswith("src/"):
            inventory.append(
                dict(source=path, commit=COMMIT, destination=None, classification="NO EXTRAÍDO")
            )
        elif path.startswith("tests/research/") and path.endswith(".py"):
            tests.append(dict(source=path, category="RESEARCH", migrated=False))
    write("LICENSE", git("show", f"{COMMIT}:LICENSE"))
    write(
        "docs/extraction-manifest.json",
        json.dumps(inventory, indent=2, ensure_ascii=False).encode(),
    )
    write("docs/test-migration.json", json.dumps(tests, indent=2).encode())
    print(
        f"Extracted {sum(x['destination'] is not None for x in inventory)} modules; migrated {sum(x['migrated'] for x in tests)} test files"
    )


if __name__ == "__main__":
    main()
