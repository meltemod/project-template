# One-time R environment bootstrap. Run from the project root.
#
#   Rscript scripts/00-setup.R
#
# Safe to re-run. After it finishes, commit renv.lock.
#
# Dependencies are declared in DESCRIPTION, not in this file. renv is
# configured with snapshot type "explicit", so renv.lock records exactly what
# DESCRIPTION declares rather than what renv infers from library() calls in
# code. Add a package to DESCRIPTION before using it.

if (!file.exists("DESCRIPTION")) {
  stop("Run this from the project root, not from scripts/.", call. = FALSE)
}

# ---- R version ----------------------------------------------------------
# This project pins the R MINOR series, not an exact patch. Package binaries
# are not portable across minor versions (R's ABI changes, and CRAN ships a
# separate binary repo per minor release), so restoring renv.lock on a
# different series risks slow source builds. Patch releases are ABI-stable
# and safe to differ.
r_series <- paste(R.version$major,
                  strsplit(R.version$minor, ".", fixed = TRUE)[[1]][1],
                  sep = ".")

if (r_series != "{{ cookiecutter.r_version }}") {
  warning(
    "This project pins R {{ cookiecutter.r_version }}.x; you are running ",
    getRversion(), ".\n",
    "  renv::restore() may fall back to compiling packages from source.\n",
    "  If you use rig:  rig add {{ cookiecutter.r_version }} && rig default {{ cookiecutter.r_version }}",
    call. = FALSE
  )
}

# ---- renv bootstrap -----------------------------------------------------
if (!requireNamespace("renv", quietly = TRUE)) {
  message("Installing renv ...")
  install.packages("renv", repos = "https://cloud.r-project.org")
}

if (!file.exists("renv.lock")) {
  message("No renv.lock found - initialising a new renv library.")
  renv::init(bare = TRUE, restart = FALSE)
} else {
  message("renv.lock found - restoring the recorded library.")
  renv::restore(prompt = FALSE)
}

# Record what DESCRIPTION declares, not what renv infers from library() calls.
# Without this, a package installed but not yet referenced by any script would
# be silently omitted from renv.lock.
renv::settings$snapshot.type("explicit")

# ---- dependencies, read from DESCRIPTION --------------------------------
fields <- read.dcf("DESCRIPTION", fields = c("Depends", "Imports"))
declared <- unlist(strsplit(fields[!is.na(fields)], ","))
pkgs <- trimws(sub("\\(.*", "", declared))   # drop version constraints
pkgs <- setdiff(pkgs[nzchar(pkgs)], "R")     # R itself is not installable

if (length(pkgs) > 0L) {
  message("Declared in DESCRIPTION: ", paste(pkgs, collapse = ", "))
  missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]
  if (length(missing) > 0L) {
    message("Installing: ", paste(missing, collapse = ", "))
    renv::install(missing)
  } else {
    message("All declared packages already present.")
  }
} else {
  message("No packages declared yet. Add an Imports: field to DESCRIPTION,")
  message("then re-run this script.")
}

renv::snapshot(prompt = FALSE)

cat("\nSetup complete.\n",
    "  R:    ", as.character(getRversion()), "\n",
    "  Next: declare packages in DESCRIPTION, re-run, then commit renv.lock\n",
    sep = "")
