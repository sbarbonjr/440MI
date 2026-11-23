# Beamer Presentations

This directory contains the 36-class lecture sequence for the course `440MI / 305SM`, written in Beamer and organized in three macro-blocks: **Python** (instrumental programming, Classes 1-12) → **Data-Driven** (data types, representation, modeling, and experiment tracking, Classes 13-19) → **Software Engineering and MLOps** (Classes 20-36). It draws on:

- notebooks for EDA, feature engineering, model training, Neptune tuning, and incremental learning
- Flask and Streamlit demos for fraud detection and streaming ML
- the synthetic pasteurization case study
- tutorials for Docker and GitHub Actions

## Files

- `common.tex`: shared Beamer styling and macros
- `common_visual.tex`: optional visual layer (tiles, Font Awesome icons via `fontawesome5`, progress-strip section dividers, glossary footer strip) used by the Class 22, 23, 25, 26, 27, and 28 decks
- `generate_class20_figures.py`, `generate_class22_figures.py`, `generate_class23_figures.py`, `generate_class25_figures.py`, `generate_class27_figures.py`, `generate_class28_figures.py`: regenerate the figures of those decks into `images/` (the Class 22, 23, 25, 27, and 28 figures are synthetic or schematic and say so on their face)
- `class01_intro_course.tex` to `class36_presentation_proposals.tex`: lecture decks, numbered in delivery order

Classes 21 and 24 are intervention sessions. Class 25 contains the course's agile tools and good-practices material, which the two-session pasteurization requirements practice puts to work: Session 1 is Class 26 and Session 2 is Class 28, with Class 27 (MLOps foundations and continuous training) in between.

## Suggested workflow

Compile each deck from this directory, for example:

```bash
cd presentations
pdflatex class01_intro_course.tex
```

If your TeX setup needs multiple runs for links or tables of contents, run `pdflatex` twice.

## Design choices

- The Python block (1-12) restores dedicated programming fundamentals — basic syntax, control flow, functions, files, OOP — that had previously been compressed into fewer sessions, drawing on the legacy `delete/2024/lessons/DataDriven_L1`-`L7` material.
- The Data-Driven block opens with data types and representation, then includes an encoding lab (15), feature engineering (16), Git (17), ML modeling (18), and ML experiment tracking, registry, evaluation, and decision-making (19). Online learning and concept drift move to Class 29, followed by the streaming practice in Class 30.
- Model deployment and prediction serving is Class 31, ahead of Docker and CI/CD (32) and monitoring/scalability (33). The two proposal-presentation sessions merge into one final Class 36.
- Class 17 (`class17_version_control.tex`) covers Git fundamentals, branching, merge conflicts, and pull requests. It precedes ML modeling (Class 18), so students can version the experiments they build in Class 19. Class 18 is `class18_ml_modeling.tex`; Class 19 is `class19_ml_experiment_tracking.tex` and contains experiment tracking, registry, evaluation, and decision-making.
- The encoding lab (Class 15) gives students practice selecting and applying encoders with a preprocessing pipeline, building on Class 14's representation concepts.
- Class 15's activity brief is in `documents/Class15_Encoding_Embedding_Activity.md`, with a worked notebook in `notebooks/Class15_Encoding_Embedding_Solution.ipynb` and its prepared all-rows exploratory fixture in `notebooks/Class15_Titanic_Imputed.csv`. The train/test split is introduced in Class 18 before model evaluation.
- Classes 27 (MLOps foundations / continuous training) and 33 (continuous monitoring / scalability) each include a "Practical Component" frame flagging that no runnable exercise exists yet in this repository for that topic — a candidate for a follow-up project or submodule.
- Real examples are drawn from this repository instead of relying only on textbook slides.
- Lecture decks end with curated reading; practice decks close with a deliverable or reflection prompt.

