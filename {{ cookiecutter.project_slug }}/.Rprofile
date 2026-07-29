source("renv/activate.R")
# Project-level R startup for {{ cookiecutter.project_name }}.
#
# The first line is renv's. Leave it at the top — renv rewrites it on init.

# Load .env so R and Python read configuration and secrets from ONE file.
# R's .Renviron parser accepts the same KEY=value format as .env, and ignores
# blank lines and lines beginning with '#'. This keeps a single secret in a
# single gitignored place, rather than a .Renviron and a .env drifting apart.
if (file.exists(".env")) {
  readRenviron(".env")
}

# Prefer binary package installs on macOS. Source installs of packages with
# compiled dependencies (sf, terra, ...) need a system GDAL/PROJ/GEOS
# toolchain; the CRAN macOS binaries bundle those libraries already.
if (Sys.info()[["sysname"]] == "Darwin") {
  options(pkgType = "binary")
}

if (interactive()) {
  message("{{ cookiecutter.project_slug }} | R ", getRversion())
}
