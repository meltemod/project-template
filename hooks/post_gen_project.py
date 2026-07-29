"""Post-generation: prune disabled stacks, write LICENSE, then bootstrap.

Every external command is guarded. A missing tool prints a note and is
skipped — it never fails generation, because a scaffolded project that
exists but is not yet bootstrapped is far more useful than no project.
"""

import datetime
import shutil
import subprocess
import sys
from pathlib import Path

USE_R = "{{ cookiecutter.use_r }}" == "yes"
USE_PYTHON = "{{ cookiecutter.use_python }}" == "yes"
LICENSE = "{{ cookiecutter.license }}"
AUTHOR = "{{ cookiecutter.author_name }}"

ROOT = Path.cwd()
YEAR = datetime.date.today().year


def drop(*paths: str) -> None:
    for p in paths:
        target = ROOT / p
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
        elif target.exists():
            target.unlink()


def run(cmd: list[str], label: str) -> bool:
    """Run a command, reporting outcome. Never raises."""
    exe = shutil.which(cmd[0])
    if exe is None:
        print(f"  skipped {label}: {cmd[0]} not installed")
        return False
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    except (subprocess.SubprocessError, OSError) as exc:
        print(f"  skipped {label}: {exc}")
        return False
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        print(f"  {label} FAILED (exit {proc.returncode})")
        for line in tail[-4:]:
            print(f"      {line}")
        return False
    print(f"  {label} ok")
    return True


# ---- prune stacks the user turned off ----------------------------------
if not USE_R:
    drop(".Rprofile", "DESCRIPTION", "renv",
         "{{ cookiecutter.project_slug }}.Rproj", "scripts/00-setup.R")

if not USE_PYTHON:
    drop("pyproject.toml", ".python-version")

# ---- LICENSE ------------------------------------------------------------
MIT = f"""MIT License

Copyright (c) {YEAR} {AUTHOR}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Apache-2.0 and CC-BY-4.0 run to thousands of words of legal text. Rather
# than reproduce them from memory (where a transcription slip would be a real
# legal defect), the stub records the choice and points at the canonical text.
STUB = """{name}

Copyright (c) {year} {author}

This work is licensed under the {name} licence.
SPDX-License-Identifier: {spdx}

Full licence text: {url}

TODO: replace this file with the complete licence text before distributing.
      This stub records the choice; it is not a substitute for the text.
"""

PROPRIETARY = f"""Copyright (c) {YEAR} {AUTHOR}. All rights reserved.

This software and its documentation are proprietary and confidential.
Unauthorised copying, distribution or use, in whole or in part, by any
medium, is strictly prohibited without prior written permission.
"""

if LICENSE == "MIT":
    (ROOT / "LICENSE").write_text(MIT, encoding="utf-8")
elif LICENSE == "Apache-2.0":
    (ROOT / "LICENSE").write_text(
        STUB.format(name="Apache License 2.0", spdx="Apache-2.0", year=YEAR,
                    author=AUTHOR, url="https://www.apache.org/licenses/LICENSE-2.0"),
        encoding="utf-8")
elif LICENSE == "CC-BY-4.0":
    (ROOT / "LICENSE").write_text(
        STUB.format(name="Creative Commons Attribution 4.0 International",
                    spdx="CC-BY-4.0", year=YEAR, author=AUTHOR,
                    url="https://creativecommons.org/licenses/by/4.0/legalcode"),
        encoding="utf-8")
elif LICENSE == "Proprietary":
    (ROOT / "LICENSE").write_text(PROPRIETARY, encoding="utf-8")
# "None" writes nothing.

# ---- bootstrap ----------------------------------------------------------
print("\nBootstrapping:")
run(["git", "init", "--quiet"], "git init")

if USE_PYTHON:
    run(["uv", "sync"], "uv sync")

if USE_R:
    # scripts/00-setup.R initialises renv when there is no lockfile and
    # restores when there is, so it covers both a fresh project and a clone.
    run(["Rscript", "scripts/00-setup.R"], "renv setup")

print(f"\nDone: {ROOT.name}")
if LICENSE in ("Apache-2.0", "CC-BY-4.0"):
    print("  NOTE: LICENSE is a stub — paste the full text before distributing.")
print("  Next: review README.md, declare dependencies, then commit.")
