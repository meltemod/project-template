# project-template

A [Cookiecutter](https://cookiecutter.readthedocs.io/) template for
reproducible data-analysis projects using **renv** (R) and **uv** (Python),
either together or on their own.

## Usage

```bash
cookiecutter gh:meltemod/project-template
```

No install needed if you have `uv`:

```bash
uvx --from cookiecutter cookiecutter gh:meltemod/project-template
```

Local checkout:

```bash
cookiecutter ./project-template
```

## Prompts

| Variable | Default | Notes |
|---|---|---|
| `project_name` | `My Project` | Human-readable title |
| `project_slug` | derived | Lowercased, spaces/hyphens → underscores. Directory, Python dist and `.Rproj` name |
| `r_package_name` | derived | Dots, not underscores — **R permits neither hyphens nor underscores** in package names |
| `author_name` | *placeholder* | Rejected if left as the placeholder — see below |
| `author_email` | *placeholder* | Rejected if left as the placeholder — see below |
| `author_orcid` | *(empty)* | Omitted from `DESCRIPTION` and `CITATION.cff` when blank |
| `description` | placeholder | |
| `use_python` | `yes` | `no` removes `pyproject.toml` and `.python-version` |
| `use_r` | `yes` | `no` removes `.Rprofile`, `DESCRIPTION`, `renv/`, `.Rproj`, `00-setup.R` |
| `python_version` | `3.12.13` | **Exact patch.** uv downloads this interpreter |
| `r_version` | `4.6` | **Minor series.** See below |
| `license` | `MIT` | `MIT`, `Apache-2.0`, `CC-BY-4.0`, `Proprietary`, `None` |

Inputs are validated *before* any files are written, so a bad value aborts
cleanly rather than leaving a half-made directory.

## Personal defaults

The author fields ship as placeholders, and generation **aborts** if they are
left that way. A template that quietly stamps its own maintainer's name into
your `LICENSE`, your `DESCRIPTION` and your `CITATION.cff` is worse than one
that stops and asks.

To avoid retyping them, set them once in `~/.cookiecutterrc`:

```yaml
default_context:
  author_name: "Ada Lovelace"
  author_email: "ada@example.org"
  author_orcid: "0000-0000-0000-0000"   # omit the line if you have none
```

Cookiecutter reads that file for *every* template, so keep it to identity
keys — a generic key such as `description` would leak into unrelated
templates.
[r-package-template](https://github.com/meltemod/r-package-template) uses the
same key names deliberately, so one file serves both.

Precedence is `key=value` on the command line, then `~/.cookiecutterrc`, then
the defaults in `cookiecutter.json`. Point `--config-file` or the
`COOKIECUTTER_CONFIG` environment variable at a dotfiles-managed copy if you
work on more than one machine.

## What you get

```
<project_slug>/
├── config.yml           Shared settings, read by BOTH R and Python
├── CITATION.cff         Citation metadata, ORCID included
├── .env.example         Secret template; .env is gitignored
├── .Rprofile            Loads .env into R; activates renv
├── DESCRIPTION          R dependencies, DECLARED
├── renv/                activate.R + settings.json (no library/)
├── pyproject.toml       Python dependencies, declared
├── .python-version      Pinned interpreter
├── scripts/00-setup.R   renv init-or-restore bootstrap
├── data/{raw,interim,processed}/
├── outputs/{figures,tables}/
└── reports/  docs/
```

After generation the hook runs `git init`, then `uv sync`, then
`Rscript scripts/00-setup.R`. Each step is skipped with a note if the tool
isn't installed — a missing tool never fails generation.

## Design decisions

**Lockfiles are not shipped.** `uv.lock` and `renv.lock` are generated per
project by the post-generation hook. A template-level lock would either pin
nothing (both dependency lists start empty) or force every new project to
restore someone else's stack.

**`renv/activate.R` *is* shipped**, so `.Rprofile` works immediately. It pins
the renv version it was captured at; run `renv::upgrade()` in a generated
project to refresh.

**R is pinned by minor series, Python by exact patch.** Not an inconsistency —
a cost difference. uv downloads a pinned interpreter silently, so exactness is
free. R is system-wide with no per-project switching, so demanding an exact
patch would cost every collaborator a manual install for no benefit: package
binaries are ABI-compatible across patch releases but *not* across minor ones.

**`renv` uses `snapshot.type = "explicit"`**, so `renv.lock` records what
`DESCRIPTION` declares rather than what renv infers from `library()` calls.
Add a package to `DESCRIPTION` before using it. This avoids a new project
installing packages that never reach the lockfile.

**Neither stack declares dependencies by default.** Both lists start empty so
nothing unwanted is inherited.

## Caveat

`Apache-2.0` and `CC-BY-4.0` generate a **stub** `LICENSE` recording the choice
and linking the canonical text, rather than the full legal text — reproducing
thousands of words of licence from memory risks a transcription error that
would be a real legal defect. `MIT` and `Proprietary` are written in full.
The generated README flags the stub under "Known gaps".

## Requirements

- [`cookiecutter`](https://cookiecutter.readthedocs.io/) ≥ 2.x
- Optional: `uv`, R + `rig`, `git` — each only needed for its own bootstrap step
