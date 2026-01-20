# Finny — Conversational Loan Origination System (LOS)

Finny is a **deterministic, rule-based conversational Loan Origination System (LOS)** designed to closely mirror how real NBFCs and fintech lenders process retail loan applications.

The system intentionally separates **decision-making** from **explanation**:

* Loan approvals and rejections are made **only through predefined underwriting rules**
* AI is used **strictly for explainability, guidance, and user communication** — never for credit decisions

This design reflects real-world financial systems where **auditability, predictability, and regulatory trust** are non-negotiable.

---

## Why Finny

Most loan demos and student projects rely heavily on black-box AI models to make credit decisions. While impressive on the surface, such systems are:

* Hard to audit
* Difficult to explain to users
* Unrealistic for regulated environments

**Finny takes a different approach.**

It models how actual lenders work internally:

* Structured intake of loan intent
* Deterministic underwriting rules (FOIR, income, credit score)
* Clear approval, conditional approval, or rejection outcomes
* Human-readable explanations at every step

The result is a system that feels conversational to the user, while remaining **fully controllable and transparent** for the lender.

---

## Product Capabilities

### Conversational Loan Application

Users apply for loans through a guided, chat-based flow that captures:

* Loan type
* Requested amount
* Tenure
* Basic applicant details

The interaction is designed to resemble modern fintech onboarding journeys.

### Rule-Based Underwriting Engine

Loan eligibility is evaluated using deterministic rules, including:

* EMI calculation
* Fixed Obligation to Income Ratio (FOIR)
* Credit score thresholds
* Income-based eligibility limits

All decisions are reproducible and traceable.

### Explainable Outcomes

Every loan application results in one of three outcomes:

* **Approved**
* **Conditionally Approved** (additional documents required)
* **Rejected**

For each outcome, Finny provides a clear explanation and, where applicable, suggests corrective actions — without allowing AI to influence the actual decision.

---

## System Architecture

Finny is built using a **multi-agent architecture** inspired by internal NBFC workflows.

### Agents

* **Master Agent (FINNY)**
  Orchestrates the entire loan lifecycle and manages state across agents.

* **Sales Agent**
  Captures loan intent, amount, tenure, and product selection.

* **Verification Agent**
  Performs PAN validation and fetches credit bureau data (mocked for simulation).

* **Underwriting Agent**
  Applies deterministic eligibility and risk rules.

* **Document Agent**
  Handles document collection and validation (OCR-ready).

* **Sanction Agent**
  Generates sanction letters for approved loans.

---

## Core Logic

* EMI calculation
* FOIR computation
* Interest rate determination
* Credit score–based eligibility rules

Mock credit bureau data is defined in:

```
core/mock_bureau.py
```

If a PAN is not found, realistic default bureau values are generated to simulate real-world edge cases.

---

## AI Usage Policy

AI in Finny is **explicitly restricted** to:

* Explaining approval or rejection decisions
* Guiding users after a rejection

AI **never**:

* Approves loans
* Rejects loans
* Alters underwriting logic

This mirrors compliance-friendly AI usage in real financial institutions.

---

## Technology Stack

* Python
* Streamlit (conversational UI)
* Rule-based underwriting engine
* Mock credit bureau integration

---

## Running the Project Locally

```bash
git clone https://github.com/Krishna-721/Finny-Loan-Management.git
cd Finny-Loan-Management
pip install -r requirements.txt
streamlit run app.py
```

---

## Future Roadmap

* OCR-based salary slip extraction
* Secure PAN and document encryption
* Persistent database integration
* Java Spring Boot backend
* Next.js frontend

---

## Live Demo

[https://finny-loan-management.streamlit.app](https://finny-loan-management.streamlit.app)

---

## Disclaimer

Finny is a **simulation and learning project** designed to demonstrate system design, underwriting logic, and explainable AI patterns. It does not process real financial data or issue actual loans.
