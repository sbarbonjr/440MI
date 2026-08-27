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

The materials in this repository follow a 15-class sequence:

1. Introduction to data-driven systems engineering, MLOps, and agile AI
2. Python, notebooks, and exploratory data analysis
3. PCA and dimensionality reduction
4. Feature engineering and preprocessing pipelines
5. Modeling, metrics, and adaptation
6. Serving models with APIs and interfaces
7. Software engineering foundations for ML systems
8. Experiment tracking and hyperparameter tuning
9. Delivery pipelines, containers, and CI/CD
10. Requirements engineering for data-driven systems
11. Process models and lifecycle choices
12. Agile toolkit for data and software teams
13. MLOps foundations and operational maturity
14. Project proposal and milestone planning
15. Model monitoring and drift response

The class slides live in [presentations/](presentations/), with both `.tex` sources and compiled PDFs.

## Repository Map

```text
.
├── documents/         Supporting project documents and case-study material
├── notebooks/         Jupyter notebooks for class exercises and demonstrations
├── pasteurization/    Streaming and monitoring example for the pasteurization case
├── presentations/     Beamer slide decks for Classes 1-15
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

- Start with [presentations/class01_intro_mlops_agile.pdf](presentations/class01_intro_mlops_agile.pdf) for the course framing
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
