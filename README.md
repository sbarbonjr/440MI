# Data-driven Systems Engineering

**University of Trieste**

This repository contains the working materials for the course **Data-driven Systems Engineering**. The course connects **data analysis**, **machine learning**, **software engineering**, and **MLOps** through a sequence of classes that moves from exploration to deployment and monitoring.

The repository is organized around two recurring teaching cases:

- **Fraud detection as a service** for tabular classification, APIs, dashboards, and delivery pipelines
- **Pasteurization monitoring** for streaming data, online learning, drift detection, and operational monitoring

## Course Overview

The course is designed to help students reason about a complete data-driven system instead of treating modeling as an isolated notebook activity. Across the classes, students learn how to:

- inspect and understand data with Python
- transform data into usable features
- train and evaluate models
- expose predictions through services and interfaces
- structure development work with software engineering and agile practices
- package, deploy, monitor, and evolve ML-enabled systems

## Course Structure

The materials in this repository follow a 36-class sequence organized in three macro-blocks: **Python** (instrumental programming) → **Data-Driven** (data types, representation, and modeling) → **MLOps** (software engineering and operations).

### I. Python (Classes 1-12)

1. Introduction to the course (MLOps, Agile, Data Mining)
2. What is Python?
3. Basic Python programming
4. Control flow and data structures
5. Practice 1 (hands-on with the Streamlit demo)
6. Files and plotting
7. Functions and good practices
8. Classes and OOP in Python
9. Dealing with data (pandas)
10. Exploratory data analysis
11. Python programming with machine learning (the scikit-learn API)
12. EDA practice

### II. Data-Driven (Classes 13-20)

13. Data types — tabular, time series, spectral/signal, image
14. Structured / semi-structured / unstructured data, encoding, and embeddings
15. Feature engineering (cleaning, curation, selection)
16. ML modeling 1 and experiment tracking
17. ML modeling 2 and decision-making
18. Online machine learning and concept drift
19. Streaming sensor practice
20. Model deployment and prediction serving

### III. MLOps (Classes 21-36)

21. Intervention: Cybertec (guest session)
22. Introduction to software engineering
23. Requirements engineering
24. Intervention: YesAlps (guest session)
25. Requirements engineering practice
26. Process models and Agile foundations
27. Agile toolkit practice
28. MLOps foundations
29. MLOps practice and continuous training
30. Good practices (Docker, CI/CD)
31. Continuous monitoring and scalability
32. Practical project — brainstorm and definitions
33. Intervention: Sbroiavacca (guest session)
34. Project requirements and development plan
35. Presentation of proposals, part 1
36. Presentation of proposals, part 2

The class slides live in [presentations/](presentations/), with both `.tex` sources and compiled PDFs. Classes 21, 24, and 33 are external guest sessions with material provided by the speakers, not slide decks from this repository. Classes 29 and 31 flag a practical component that does not yet have runnable code in this repository (a continuous-training pipeline and a monitoring/scalability exercise, respectively) — good candidates for a separate project or submodule.

## Repository Map

```text
.
├── documents/         Supporting project documents and case-study material
├── notebooks/         Jupyter notebooks for class exercises and demonstrations
├── pasteurization/    Streaming and monitoring example for the pasteurization case
├── presentations/     Beamer slide decks for Classes 1-36
├── streamlit/         Demo apps and model-serving support files
├── tutorials/         Docker, GitHub Actions, and Jenkins examples
├── Class6_model_api.py Example model API script
├── requirements.txt   Python dependencies
└── README.md          Main course guide
```

## Main Learning Threads

### 1. Data Analysis and Modeling

Students begin with Python-based exploration, data cleaning, plotting, dimensionality reduction, feature engineering, model building, and evaluation. The notebooks are used to make this workflow concrete and inspectable.

### 2. Software Engineering for Data-driven Systems

The course then broadens from modeling to system design. Topics include requirements, process models, lifecycle choices, agile coordination, maintainability, and the difference between notebook success and system quality.

### 3. MLOps and Operationalization

The final thread focuses on repeatability and lifecycle continuity: experiment tracking, packaging, CI/CD, serving, monitoring, drift detection, and project planning for systems that must remain useful after deployment.

## Running Cases

### Fraud Detection

The fraud case is used to discuss:

- class imbalance
- feature construction for tabular data
- classification metrics and threshold decisions
- model serving through APIs and dashboards
- deployment and monitoring trade-offs

Relevant materials include notebooks in [notebooks/](notebooks/), the Streamlit app in [streamlit/](streamlit/), and the supporting documents in [documents/](documents/).

### Pasteurization Monitoring

The pasteurization case is used to discuss:

- synthetic sensor generation
- streaming data flows
- online or incremental learning
- drift detection
- operational dashboards and monitoring loops

Relevant code lives mainly in [pasteurization/](pasteurization/) and [streamlit/](streamlit/).

## Key Technologies Used in the Course

- **Python** for the general programming layer
- **Jupyter** for exploration and teaching notebooks
- **pandas**, **Matplotlib**, and related plotting tools for EDA
- **scikit-learn** for preprocessing, pipelines, and classical ML
- **River** for online learning and drift-aware workflows
- **Flask** for lightweight APIs and service endpoints
- **Streamlit** for interactive demos and dashboards
- **Docker** for packaging and reproducible execution
- **GitHub Actions** and **Jenkins** for CI/CD examples

These tools are not presented as interchangeable. Each appears in the course because it supports a different part of the lifecycle.

## How to Use This Repository

### During the course

- read the class slides in [presentations/](presentations/)
- run the matching notebooks in [notebooks/](notebooks/)
- inspect the case-study code in [pasteurization/](pasteurization/) and [streamlit/](streamlit/)
- use the tutorials in [tutorials/](tutorials/) to connect code to packaging and automation

### For project work

- start from a notebook or baseline script
- move reusable logic into structured code
- define requirements and milestones early
- think about interfaces, deployment, and monitoring before the final stage

## Setup

1. Clone the repository.

```bash
git clone <repository-url>
cd 440MI
```

2. Create and activate a virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the dependencies.

```bash
pip install -r requirements.txt
```

4. Launch Jupyter for the notebooks if needed.

```bash
jupyter notebook
```

5. Run Streamlit apps or Python services as required by the specific class materials.

## Suggested Entry Points

- Start with [presentations/class01_intro_course.pdf](presentations/class01_intro_course.pdf) for the course framing
- Open [notebooks/Class2_EDA.ipynb](notebooks/Class2_EDA.ipynb) for the first hands-on data analysis material
- Inspect [pasteurization/serving.py](pasteurization/serving.py) and [pasteurization/synth_sensors.py](pasteurization/synth_sensors.py) for the streaming case
- Explore [streamlit/Main.py](streamlit/Main.py) for the dashboard-facing side of the repository

## Learning Outcomes

By the end of the course, students should be able to:

- analyze datasets with Python and communicate findings clearly
- design preprocessing and feature pipelines for reproducible modeling
- compare modeling alternatives using suitable metrics
- explain how an ML model becomes part of a usable software system
- connect requirements, process choices, and agile practices to technical delivery
- describe and implement basic MLOps workflows for packaging, deployment, and monitoring

## Notes

- The repository includes both source materials and runnable examples.
- Some generated presentation support files are intentionally ignored to keep the repository clean.
- The `delete/` directory contains legacy presentation material and is excluded from version control.

## License

This repository is maintained for educational use in the context of the University of Trieste course. See institutional guidance for reuse and redistribution policies.
