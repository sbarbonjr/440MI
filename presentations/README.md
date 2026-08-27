# Beamer Presentations

This directory contains a refreshed lecture sequence for the course `440MI / 305SM`, rewritten in Beamer and aligned with the repository's current material:

- notebooks for EDA, PCA, model training, Neptune tuning, and incremental learning
- Flask and Streamlit demos for fraud detection and streaming ML
- the synthetic pasteurization case study
- tutorials for Docker, Jenkins, and GitHub Actions

## Files

- `common.tex`: shared Beamer styling and macros
- `class01_intro_mlops_agile.tex` to `class15_model_monitoring.tex`: lecture decks

## Suggested workflow

Compile each deck from this directory, for example:

```bash
cd presentations
pdflatex class01_intro_mlops_agile.tex
```

If your TeX setup needs multiple runs for links or tables of contents, run `pdflatex` twice.

## Design choices

- The class sequence now explicitly fills the missing bridge topics:
  - `Class 8`: experiment tracking and model tuning
  - `Class 9`: delivery pipelines, Docker, and CI/CD
- Real examples are drawn from this repository instead of relying only on textbook slides.
- Each deck ends with a curated reading slide to support deeper study.

