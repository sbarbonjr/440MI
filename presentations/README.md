# Beamer Presentations

This directory contains the 36-class lecture sequence for the course `440MI / 305SM`, written in Beamer and organized in three macro-blocks: **Python** (instrumental programming, Classes 1-12) → **Data-Driven** (data types, representation, modeling, and experiment tracking, Classes 13-19) → **Software Engineering and MLOps** (Classes 20-36). It draws on:

- notebooks for EDA, feature engineering, model training, Neptune tuning, and incremental learning
- Flask and Streamlit demos for fraud detection and streaming ML
- the synthetic pasteurization case study
- tutorials for Docker and GitHub Actions

## Files

- `common.tex`: shared Beamer styling and macros
- `class01_intro_course.tex` to `class36_presentation_proposals.tex`: lecture decks, numbered in delivery order

Classes 21, 24, and 34 are intervention sessions. Their material is provided directly for those sessions, rather than authored as course decks in this repository.

## Suggested workflow

Compile each deck from this directory, for example:

```bash
cd presentations
pdflatex class01_intro_course.tex
```

If your TeX setup needs multiple runs for links or tables of contents, run `pdflatex` twice.

## Design choices

- The Python block (1-12) restores dedicated programming fundamentals — basic syntax, control flow, functions, files, OOP — that had previously been compressed into fewer sessions, drawing on the legacy `delete/2024/lessons/DataDriven_L1`-`L7` material.
- The Data-Driven block opens with data types and representation, then includes an encoding lab (15), feature engineering (16), Git (17), ML modeling (18), and ML experiment tracking, registry, evaluation, and decision-making (19). Online learning and concept drift move to Class 28, followed by the streaming practice in Class 29.
- Model deployment and prediction serving is Class 30, ahead of Docker and CI/CD (31) and monitoring/scalability (32). The two proposal-presentation sessions merge into one final Class 36.
- Class 17 (`class17_version_control.tex`) covers Git fundamentals, branching, merge conflicts, and pull requests. It precedes ML modeling (Class 18), so students can version the experiments they build in Class 19. Class 18 is `class18_ml_modeling.tex`; Class 19 is `class19_ml_experiment_tracking.tex` and contains experiment tracking, registry, evaluation, and decision-making.
- The encoding lab (Class 15) gives students practice selecting and applying encoders with a preprocessing pipeline, building on Class 14's representation concepts.
- Class 15's activity brief is in `documents/Class15_Encoding_Embedding_Activity.md`, with a worked notebook in `notebooks/Class15_Encoding_Embedding_Solution.ipynb` and its prepared all-rows exploratory fixture in `notebooks/Class15_Titanic_Imputed.csv`. The train/test split is introduced in Class 18 before model evaluation.
- Classes 27 (MLOps practice / continuous training) and 32 (continuous monitoring / scalability) each include a "Practical Component" frame flagging that no runnable exercise exists yet in this repository for that topic — a candidate for a follow-up project or submodule.
- Real examples are drawn from this repository instead of relying only on textbook slides.
- Lecture decks end with curated reading; practice decks close with a deliverable or reflection prompt.

