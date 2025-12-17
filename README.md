# Finny – Conversational Loan Management System

Finny is a **rule-based conversational loan origination system (LOS)** designed to simulate NBFC-style loan processing using a multi-agent architecture.

The system focuses on **deterministic decision-making** using underwriting rules, while AI is used **only for explanations and user guidance**.

---

## 🧩 Architecture

Finny follows a **5 Agent + 1 Master Agent** model:

* **Master Agent (FINNY)** – Manages/Orchestrates the entire loan flow
* **Sales Agent** – Captures loan intent, type, amount, and tenure
* **Verification Agent** – PAN validation and credit bureau fetch (mocked)
* **Underwriting Agent** – Rule-based eligibility checks (FOIR, limits, credit rules)
* **Document Agent** – Handles salary slip / document uploads (OCR-ready)
* **Sanction Agent** – Generates sanction letter for approved loans

---

## 🔄 Loan Flow (High Level)

1. User starts loan application via chat
2. Sales Agent collects loan details
3. PAN is verified and bureau data is fetched
4. Underwriting rules are applied
5. Outcome:

   * Approved
   * Conditionally Approved (documents required)
   * Rejected (with explanation)

---

## 📊 Core Logic

* EMI calculation
* FOIR calculation
* Interest rate logic
* Credit score–based rules

Mock credit bureau data is defined in:

```
core/mock_bureau.py
```

If a PAN is not found, realistic default values are generated.

---

## 🤖 AI Usage

AI is **restricted** to:

* Explaining approval or rejection
* Suggesting corrective steps after rejection

AI **does not** approve or reject loans.

---

## 🛠 Tech Stack

* Python
* Streamlit (conversational UI)
* Rule-based underwriting engine
* Mock credit bureau

---

## ▶️ Run Locally

```bash
git clone https://github.com/Krishna-721/Finny-Loan-Management.git
cd Finny-Loan-Management
pip install -r requirements.txt
streamlit run app.py
```

---

## 🚀 Future Scope

* OCR-based salary slip extraction
* Secure PAN & document encryption
* Database integration
* Java Spring Boot backend
* Next.js frontend

---

## 🔗 Links

* Live Demo: [https://finny-loan-management.streamlit.app](https://finny-loan-management.streamlit.app)
