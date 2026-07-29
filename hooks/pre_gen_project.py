"""Validate inputs before any files are written.

Exiting non-zero here aborts generation cleanly, leaving no half-made
directory behind.
"""

import re
import sys

PROJECT_SLUG = "{{ cookiecutter.project_slug }}"
R_PACKAGE_NAME = "{{ cookiecutter.r_package_name }}"
USE_R = "{{ cookiecutter.use_r }}"
USE_PYTHON = "{{ cookiecutter.use_python }}"
PYTHON_VERSION = "{{ cookiecutter.python_version }}"
R_VERSION = "{{ cookiecutter.r_version }}"
# Triple-quoted: a stray apostrophe in a name would otherwise break this hook
# rather than the value it is meant to validate.
AUTHOR_NAME = """{{ cookiecutter.author_name }}"""
AUTHOR_EMAIL = """{{ cookiecutter.author_email }}"""
AUTHOR_ORCID = """{{ cookiecutter.author_orcid }}"""

# The author fields ship as placeholders so that a stranger generating from
# the public template cannot silently publish work attributed to someone
# else. Rejecting them here turns a wrong answer into a loud one.
RC_ADVICE = """  Answer these at the prompt, or set them once for every template you use
  in ~/.cookiecutterrc:

      default_context:
        author_name: "Ada Lovelace"
        author_email: "ada@example.org"
        author_orcid: "0000-0000-0000-0000"
"""

errors = []
placeholders_left = False

if AUTHOR_NAME.strip() == "Your Name":
    placeholders_left = True
    errors.append(
        "author_name is still the template placeholder 'Your Name'.\n"
        "  It becomes the LICENSE copyright holder, the DESCRIPTION maintainer\n"
        "  and the cited author in CITATION.cff."
    )

if AUTHOR_EMAIL.strip() == "you@example.com":
    placeholders_left = True
    errors.append(
        "author_email is still the template placeholder 'you@example.com'.\n"
        "  It becomes the maintainer address in DESCRIPTION and CITATION.cff."
    )

# DESCRIPTION and CITATION.cff both split the name into given and family
# parts, and neither can guess which a single token is meant to be.
if len(AUTHOR_NAME.split()) < 2:
    errors.append(
        f"author_name {AUTHOR_NAME!r} has no family name.\n"
        "  DESCRIPTION uses person(given, family, ...) and CITATION.cff wants\n"
        "  the two separately. Give at least two words, or edit both files\n"
        "  after generation."
    )

# ORCID is optional; when supplied it must be well formed, because a wrong
# one silently attributes the work to a different researcher.
if AUTHOR_ORCID.strip() and not re.match(
    r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", AUTHOR_ORCID.strip()
):
    errors.append(
        f"author_orcid {AUTHOR_ORCID!r} is malformed.\n"
        "  Expected 0000-0000-0000-0000 (final character may be X).\n"
        "  Leave it blank to omit the ORCID entirely."
    )

# Directory name, Python dist name, and .Rproj stem all derive from this.
if not re.match(r"^[a-z][a-z0-9_]*$", PROJECT_SLUG):
    errors.append(
        f"project_slug {PROJECT_SLUG!r} is invalid.\n"
        "  Must start with a lowercase letter and contain only lowercase\n"
        "  letters, digits and underscores."
    )

# R is stricter than everything else: letters, digits and dots only. No
# hyphens, no underscores, must start with a letter, must not end with a dot.
if USE_R == "yes":
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9.]*[a-zA-Z0-9]$", R_PACKAGE_NAME):
        errors.append(
            f"r_package_name {R_PACKAGE_NAME!r} is not a valid R package name.\n"
            "  Letters, digits and dots only; must start with a letter and\n"
            "  must not end with a dot."
        )
    if not re.match(r"^\d+\.\d+$", R_VERSION):
        errors.append(
            f"r_version {R_VERSION!r} should be a MINOR series such as '4.6',\n"
            "  not a full patch version. R package binaries are not portable\n"
            "  across minor versions, but patch releases are interchangeable."
        )

if USE_PYTHON == "yes" and not re.match(r"^\d+\.\d+\.\d+$", PYTHON_VERSION):
    errors.append(
        f"python_version {PYTHON_VERSION!r} should be an exact patch version\n"
        "  such as '3.12.13'. uv downloads exactly this interpreter, so\n"
        "  pinning the patch costs nothing and guarantees reproducibility."
    )

if USE_R == "no" and USE_PYTHON == "no":
    errors.append("use_r and use_python are both 'no' — nothing would be generated.")

if errors:
    print("\nCannot generate project:\n", file=sys.stderr)
    for e in errors:
        print(f"  - {e}\n", file=sys.stderr)
    if placeholders_left:
        print(RC_ADVICE, file=sys.stderr)
    sys.exit(1)
