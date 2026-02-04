# 🏦 Finny — Conversational Loan Origination System (LOS)

[![Live Demo](https://img.shields.io/badge/Demo-Live-brightgreen?style=for-the-badge\&logo=streamlit)](https://finny-loan-management.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge\&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)](LICENSE)

Finny is a **deterministic, rule-based conversational Loan Origination System (LOS)** designed to closely mirror how real NBFCs and fintech lenders process retail loan applications.

The system intentionally separates **decision-making** from **explanation**:

* ✅ Loan approvals and rejections are made **only through predefined underwriting rules**
* 🤖 AI is used **strictly for explainability, guidance, and user communication** — never for credit decisions

This design reflects real-world financial systems where **auditability, predictability, and regulatory trust** are non-negotiable.

---

## 🎯 Why Finny?

Most loan demos and student projects rely heavily on black-box AI models to make credit decisions. While impressive on the surface, such systems are:

* ❌ Hard to audit
* ❌ Difficult to explain to users
* ❌ Unrealistic for regulated environments

**Finny takes a different approach.**

It models how actual lenders work internally:

* ✅ Structured intake of loan intent
* ✅ Deterministic underwriting rules (FOIR, income, credit score)
* ✅ Clear approval, conditional approval, or rejection outcomes
* ✅ Human-readable explanations at every step

The result is a system that feels conversational to the user, while remaining **fully controllable and transparent** for the lender.

---

## 🚀 Product Capabilities

### 1. Conversational Loan Application

Users apply for loans through a guided, chat-based flow that captures:

* 🏦 Loan type (Personal, Home, Education, Business)
* 💰 Requested amount
* 📅 Tenure (6–240 months)
* 👤 Basic applicant details

The interaction is designed to resemble modern fintech onboarding journeys.

---

### 2. Rule-Based Underwriting Engine

Loan eligibility is evaluated using deterministic rules, including:

* 📊 **EMI Calculation** using standard formula
* 💳 **Fixed Obligation to Income Ratio (FOIR)** computation
* 🎯 **Credit Score Thresholds** (minimum 700 for approval)
* 💰 **Income-Based Eligibility Limits** via pre-approved amounts
* 🎚️ **Tiered Approval Logic**:

  * **Tier 1**: Loan ≤ Pre-approved limit → **Instant Approval** ✅
  * **Tier 2**: Loan ≤ 2× Pre-approved limit → **Conditional Approval** ⏳ (salary slip required)
  * **Tier 3**: Loan > 2× Pre-approved limit OR Score < 700 → **Rejected** ❌

All decisions are **reproducible and traceable**.

---

### 3. Explainable Outcomes

Every loan application results in one of three outcomes:

* ✅ **Approved** — Instant approval with clear terms
* ⏳ **Conditionally Approved** — Additional documents required
* ❌ **Rejected** — Clear explanation with improvement suggestions

For each outcome, Finny provides a clear explanation and, where applicable, suggests corrective actions — **without allowing AI to influence the actual decision**.

---

## 🏗️ System Architecture

Finny is built using a **multi-agent architecture** inspired by internal NBFC workflows.

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Streamlit)                   │
│                         app.py (Main)                           │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MASTER AGENT                              │
│              Orchestrates loan lifecycle & state                │
└───────────────────┬─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┬───────────┬──────────┐
        ▼           ▼           ▼           ▼          ▼
┌──────────────────────────────────────────────────────────────┐
│                    SPECIALIZED AGENTS                        │
│  🛒 Sales    🔍 Verification   ⚖️ Underwriting             │
│  📄 Document  📋 Sanction                                    │
└───────────────────┬──────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┬───────────┐
        ▼           ▼           ▼           ▼
┌──────────────────────────────────────────────────────────────┐
│                  CORE BUSINESS LOGIC                         │
│  • EMI Calculation    • Interest Rate Engine                 │
│  • FOIR Computation   • Mock Credit Bureau                   │
│  • PDF Generation     • Validation Utils                     │
└──────────────────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   AI LAYER      │    │  UI/THEME       │
│  (Groq LLM)     │    │  COMPONENTS     │
└─────────────────┘    └─────────────────┘
```

---

## 🤖 Agent Responsibilities

| Agent                 | Responsibility                                                    |
| --------------------- | ----------------------------------------------------------------- |
| 🎯 Master Agent       | Orchestrates entire loan lifecycle and manages conversation state |
| 🛒 Sales Agent        | Captures loan intent, amount, tenure, and product selection       |
| 🔍 Verification Agent | PAN validation and credit bureau data retrieval                   |
| ⚖️ Underwriting Agent | Applies deterministic eligibility rules and calculates EMI/FOIR   |
| 📄 Document Agent     | Handles document upload and validation (OCR-ready)                |
| 📋 Sanction Agent     | Generates professional PDF sanction letters                       |

---

## 🧮 Core Business Logic

### Interest Rate Calculation

```
Base Rate (by loan type):
  Personal:  12.5%
  Home:      8.75%
  Business:  15.0%
  Education: 10.5%

Dynamic Adjustments:
  +1.25–1.50%  if Self-Employed / Business Owner
  -0.50%       if Amount ≥ ₹20,00,000
  -0.50%       if Credit Score ≥ 750
  +1.00%       if Credit Score < 700
  ±0.25%       based on Tenure
```

### EMI Formula

```
EMI = P × r × (1+r)^n / ((1+r)^n - 1)
Where:
P = Principal
r = Monthly Interest Rate
n = Tenure (months)
```

### FOIR Calculation

```
FOIR = ((Existing EMI + New EMI) / Monthly Income) × 100
```

Location: All logic in `core/` directory (`emi.py`, `interest.py`, `foir.py`)

---

## 🤖 AI Usage Policy

### ✅ What AI Does

* 🎯 Recommends loan products based on user's stated purpose
* 📝 Explains rejection reasons in user-friendly language
* 💡 Provides guidance on improving eligibility
* 💬 Makes the interaction conversational and empathetic

### ❌ What AI Never Does

* Approves or rejects loans
* Calculates interest rates or EMI
* Modifies underwriting logic
* Overrides rule-based decisions

This mirrors compliance-friendly AI usage in real financial institutions.

---

## 💻 Technology Stack

| Component        | Technology               |
| ---------------- | ------------------------ |
| Frontend         | Streamlit (Python)       |
| Backend Logic    | Python 3.9+ (Rule-based) |
| AI / LLM         | Groq API (LLaMA 3.3 70B) |
| PDF Generation   | ReportLab                |
| State Management | Streamlit Session State  |
| Styling          | Custom CSS + HTML        |
| Data Storage     | Mock Python Dictionaries |
| Deployment       | Streamlit Cloud          |

---

## 🚀 Quick Start

### Local Setup

```bash
git clone https://github.com/Krishna-721/Finny-Loan-Management.git
cd Finny-Loan-Management

pip install -r requirements.txt

echo "GROQ_API_KEY=your_api_key_here" > loanflow_demo/.env

cd loanflow_demo
streamlit run app.py
```

### Try It Live

👉 Launch Finny Demo

---

## 🧪 Demo Flow

* ✅ Click **"yes"** when prompted to start
* 💬 Enter loan purpose (e.g., medical emergency, home renovation) or a big paragraph, doesnt matter how you give it!
* 🏦 Select loan type and employment status
* 💰 Enter desired amount and tenure
* 🆔 Provide PAN number (try `ABCDE1234F` for instant approval)
* 📊 View instant decision with detailed breakdown
* 📄 If conditionally approved, upload salary slip (any PDF for demo)
* 📥 Download your sanction letter

---

## 🧾 Sample Test PANs

| PAN        | Credit Score | Pre-approved Limit | Expected Outcome      |
| ---------- | ------------ | ------------------ | --------------------- |
| ABCDE1234F | 780          | ₹4,00,000          | ✅ Instant Approval    |
| QWERT4321Z | 680          | ₹8,00,000          | ⏳ Conditional         |
| PQRST9876Y | 590          | ₹1,00,000          | ❌ Likely Rejection    |
| ABCPS1234K | 782          | ₹10,00,000         | ✅ High Limit Approval |

---

## 📁 Project Structure

```Finny-Loan-Management/
│
├── loanflow_demo/              # Main application directory
│   │
│   ├── app.py                  # 🎯 Main Streamlit application
│   │   ├── Session state management
│   │   ├── Chat interface
│   │   ├── Agent orchestration
│   │   └── UI rendering
│   │
│   ├── agents/                 # 🤖 Specialized Agent Modules
│   │   ├── sales_agent.py     # Collects loan requirements
│   │   ├── verification_agent.py # PAN & credit bureau validation
│   │   ├── underwriting_agent.py # Approval/rejection logic
│   │   ├── document_agent.py  # Document upload/validation
│   │   └── sanction_agent.py  # PDF sanction letter generation
│   │
│   ├── core/                   # 🧮 Business Logic Modules
│   │   ├── emi.py             # EMI calculation formula
│   │   ├── foir.py            # FOIR computation
│   │   ├── interest.py        # Dynamic interest rate engine
│   │   ├── mock_bureau.py     # Simulated credit bureau database
│   │   ├── utils.py           # Helper functions (PAN validation)
│   │   └── pdf_generator.py   # Sanction letter PDF generation
│   │
│   ├── ai/                     # 🤖 AI/LLM Layer
│   │   ├── groq_client.py     # Groq API integration
│   │   ├── persona.py         # Master Agent conversation flow
│   │   └── explain.py         # AI-powered explanations
│   │
│   ├── theme/                  # 🎨 UI Components
│   │   ├── chat_ui.py         # Chat message rendering
│   │   ├── theme.py           # Global CSS/styling
│   │   ├── style.css          # Additional styles
│   │   └── components.py      # Reusable UI elements
│   │
│   ├── output/                 # 📄 Generated PDFs (auto-created)
│   ├── conversation_logs.txt   # 📝 Audit trail
│   ├── requirements.txt        # 📦 Python dependencies
│   └── .env                    # 🔐 Environment variables (not in repo)
│
├── README.md                   # 📖 This file
├── .gitignore
└── LICENSE
```

---

## 📝 Audit Trail Example

```
[2025-12-13 14:22:57] USER: medical emergency
[2025-12-13 14:22:57] AI_RECOMMENDATION: Personal Loan
[2025-12-13 14:23:04] USER: Personal | Salaried
[2025-12-13 14:23:28] USER: ₹90,000 for 36 months
[2025-12-13 14:24:10] CIBIL_SCORE: 780
[2025-12-13 14:24:15] UNDERWRITING_DECISION: APPROVED
```

---

## 🔮 Future Enhancements

* OCR-based salary slip extraction
* Secure PAN and document encryption
* Persistent database integration
* Microservices backend (Spring Boot)
* Next.js frontend
* ML-based credit risk scoring (decision support only)
* Admin dashboard for portfolio monitoring

---

## ⚠️ Disclaimer

Finny is a simulation and learning project designed to demonstrate system design, rule-based underwriting, and explainable AI patterns. It does **not** process real financial data or issue actual loans.

---

## 👨‍💻 Author

**Vamshi Krishna**
GitHub: @Krishna-721

---

⭐ If you find this project useful, please give it a star!

Made with ❤️ for transparent, explainable fintech
