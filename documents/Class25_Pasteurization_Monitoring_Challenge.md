# NorthRiver Dairy Pasteurization Monitoring Challenge

## Student case brief

### Background

NorthRiver Dairy is a medium-sized dairy producer that operates a semi-automated pasteurization line. The company produces several batches every day for local supermarkets, schools, and hospital kitchens.

The pasteurization process is controlled by industrial equipment, but the operational team currently has no unified application for monitoring the process in real time. Operators can see raw sensor readings on separate technical screens, yet they must manually interpret the information and decide whether a situation requires attention.

The company has recently experienced operational incidents. In one case, temperature remained outside the desired range for a short period, but the operator noticed the deviation too late. In another, a pressure variation was visible in the technical data but was not considered important until the batch had already been completed. No unsafe product reached customers, but the incidents caused rework, delayed production, and higher quality-control costs.

NorthRiver Dairy wants a lightweight monitoring and alerting application before investing in a larger industrial platform. Your team has been asked to develop its first release.

### Business goal

The application must help plant personnel monitor a live pasteurization process, identify abnormal conditions early, and keep a traceable record of important alerts. It supports human decision-making; it must **not** directly control pumps, valves, heaters, or other physical equipment.

### Live data source

The simulator publishes readings through Server-Sent Events (SSE). Use the team identifier assigned by the instructor:

```text
https://four40mi-pasteurization-simulator.onrender.com/stream?team=G01
```

The event is named `sensor-reading`. The schema is at:

```text
https://four40mi-pasteurization-simulator.onrender.com/schema
```

The service uses a shared global clock. Teams connected at the same time see equivalent process observations, even if they started their applications at different moments.

An observation may include `timestamp`, `event_id`, `batch_id`, `state`, `T`, `pH`, `P`, `Kappa`, `Mu`, `Tau`, `Q_in`, `Q_out`, and `dTdt`. The process states are:

```text
Idle → Fill → HeatUp → Hold → Cool → Discharge
```

### Stakeholders

**Elena Rossi — Operations Manager**

> “My main concern is that operators need to know what needs attention now. A dashboard full of numbers is not enough. We need clear alerts, and we need to distinguish between a minor deviation and a serious operational risk.”

**Marco Bianchi — Quality Manager**

> “We must be able to explain what happened during a batch. If an alert occurred, I need to know the batch, the affected measurement, the configured rule, the observed value, and when the alert was raised.”

**Sofia Conti — Senior Plant Operator**

> “Do not make the application too complicated. During a shift, I need to see whether the system is connected, which batch is running, the current process state, and whether I need to act. I also need to acknowledge that I have seen an alert.”

**Daniel Weber — IT and Maintenance Engineer**

> “This first release must use the existing simulation service. It should run as a small web application and should not require users to install special industrial software. The application must not send commands to the production equipment.”

### What is known at project start

- The application must consume the live sensor stream.
- Users must be able to configure at least some alert thresholds.
- The dashboard must show the current process state and batch identifier.
- Alerts must have a visible severity level.
- The application must retain a local history of alerts during a user session.
- An operator must be able to acknowledge an alert.
- The application must clearly indicate whether the live data connection is active.
- The application must not control the pasteurization equipment.
- The interface must be understandable by an operator without programming knowledge.

### What is deliberately unknown

The stakeholder narrative is not a complete specification. Your team must identify and resolve questions such as:

- Which sensors require alerts in the first release?
- What is the acceptable range for each sensor?
- When is an alert a warning and when is it critical?
- Should one abnormal reading create an alert immediately?
- Can an acknowledged alert become active again?
- What should happen when the live stream disconnects?
- Should thresholds be identical for every process state?
- How long should alert history remain available?
- Which users may modify alert configurations?
- How should the application behave if a sensor value is missing or invalid?

Do not silently invent answers. Ask the instructor, record the answer source, or state and justify an explicit team assumption.

### Constraints

- Implement the application using Streamlit.
- Do not alter the simulator or its stream contract.
- Build a monitoring and alerting tool, not a controller for industrial equipment.
- Demonstrate the solution in a web browser.
- Prioritize: a small, validated vertical slice is preferable to many unvalidated features.

### Expected first release

At the end of the first release, NorthRiver Dairy expects a usable prototype that can connect to the simulator; display current status and selected sensor data; configure selected rules; detect, classify, display, record, and acknowledge alerts; explain why an alert occurred; and demonstrate validation against agreed acceptance criteria.

### Change request: issued in Session 2

Quality Management introduces the following rule after the first release:

> During the `Hold` state, temperature compliance is more important than during other states. A critical temperature alert must be raised only when the configured limit is violated for a configurable number of consecutive readings. The alert history must record the process state in which the alert was created.

Analyze its impact on the backlog, SRS, tests, architecture, interface, and operational guide. Update the relevant artifacts before implementing or planning the evolved increment.

---

## Team brief: expected process and deliverables

Use an iterative-incremental agile process. Adapt it to your team, but make this cycle visible:

```text
Elicit → Specify and prioritize → Build a thin increment → Validate → Evolve
```

### Milestones

| Milestone | Goal | Required artifacts |
|---|---|---|
| M1: Discovery | Understand needs, stakeholders, constraints, and uncertainty | stakeholder map, question log, glossary, assumptions |
| M2: Specification baseline | Agree a smallest testable increment | prioritized backlog, SRS v1, acceptance criteria, process model |
| M3: MVP | Demonstrate one working vertical slice | Streamlit application and source code |
| M4: Validation | Produce evidence of what works and what does not | test record, defects/issues, traceability matrix |
| M5: Evolution | Respond coherently to the change request | SRS v2, updated backlog, impact analysis, release notes |

### Required artifacts

1. Product vision and stakeholder map.
2. Prioritized product backlog.
3. User stories and acceptance criteria.
4. SRS v1 and v2, in concise IEEE-style structure.
5. Development-process model: roles, board states, Definition of Ready, Definition of Done, review, and change handling.
6. Operational requirements and user guide.
7. Working Streamlit application.
8. Traceability matrix from requirement to acceptance evidence.
9. Validation report and evolution note.

### SRS minimum structure

| Section | Include |
|---|---|
| Introduction | purpose, scope, stakeholders, definitions, assumptions |
| Overall description | user roles, operating environment, external SSE interface, constraints |
| Functional requirements | uniquely identified `FR-xx` requirements using clear “shall” language |
| Non-functional requirements | measurable usability, performance, reliability, maintainability, and security expectations |
| Domain/business rules | alert concepts, severity, process-state rules, traceability expectations |
| Operational requirements | deployment, configuration, recovery, support, limitations |
| Validation and traceability | acceptance criteria, test idea, priority, dependencies |

### Operational guide minimum structure

- How to start the application and select a team stream.
- How to configure, reset, and interpret alert rules.
- Meaning of severity, acknowledgement, active alerts, and alert history.
- Expected behavior for missing data, invalid readings, and stream disconnection.
- Recovery steps and known limitations.
- Explicit statement that the application does not control plant equipment.

### Traceability example

| ID | Requirement / story | Acceptance criterion | Implementation | Test evidence | Status |
|---|---|---|---|---|---|
| FR-04 | Operator configures a temperature rule | A configured threshold is used for subsequent readings | Alert rule form and evaluator | TC-08 screenshot/log | Passed |

---

## Instructor facilitation guide — not distributed to students

### Recommended two-session conduct

**Session 1 — 90–120 minutes**: introduce the challenge and a live stream; give teams 10 minutes to annotate the brief; run short stakeholder-interview rounds; require a first backlog, one FR, one NFR, and an open assumption before coding; close with each team stating its MVP and validation evidence.

**Between sessions**: teams implement the MVP. Encourage the smallest vertical slice: connect to SSE, evaluate one configurable rule, show one meaningful alert, record it, and test it.

**Session 2 — 90–120 minutes**: teams demonstrate validation evidence rather than only the interface; ask for one traceability path from stakeholder statement to test result; issue the change request; run a brief impact-analysis review; close with a retrospective.

### Canonical stakeholder answers

Use these answers consistently across teams. For an unlisted question, distinguish a known fact, a technical constraint, and a legitimate product decision that the team must propose.

| Topic | Canonical response |
|---|---|
| System role | The system supports human decisions; it does not control equipment or make production decisions autonomously. |
| First-release focus | Temperature, pressure, pH, and `dTdt` are sensible candidates, but teams must prioritize and justify the MVP. |
| Alert fatigue | Excessive alerts are harmful. Consider persistence, deduplication, or state-aware logic rather than alerting on every sample. |
| History | Local session history is sufficient for the first release. Long-term persistence is future scope. |
| Configuration | A designated operator or quality user may adjust thresholds in this prototype. Authentication is out of scope but must be documented as a limitation. |
| Disconnection | The operator must clearly see stale or disconnected data. The system must not imply monitoring continues normally. |
| Missing data | Do not silently treat missing or invalid data as normal. Show a comprehensible condition and record evaluator behavior. |
| Severity | There must be at least warning and critical. Exact policy may be proposed and justified by the team. |
| Auditability | Each alert should identify enough context to explain its rule and batch/state. |
| Safety | The prototype is educational, not a certified safety system, and must say so clearly. |

### Useful prompts

- Who uses this feature, and what decision will they make?
- Can I observe a pass or fail for that statement?
- Is this a functional requirement, quality attribute, domain rule, or assumption?
- What happens if the stream is unavailable exactly when it is needed?
- What is the smallest vertical slice that proves this idea?
- Which requirement and test must change after the new `Hold` rule?

Reward evidence and reasoning over visual polish. A strong team distinguishes stakeholder facts, technical constraints, and assumptions; writes testable requirements; demonstrates a small working increment; and shows coherent change impact.
