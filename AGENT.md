# VietJourney AI — Autonomous Agent Handbook (AGENT.md)

Welcome, Agent. This repository is **VietJourney AI**, an enterprise-grade Tour Management & AI Concierge System.
Whenever you are tasked with adding features, refactoring, or fixing bugs, adhere to the guidelines below.

---

## 1. Primary Directives

1. **Maintain Zero-Breakage Policy**:
   - The test suite in `backend/tests` must pass 100% after every change.
   - Run verification via:
     ```powershell
     .venv\Scripts\python.exe -m pytest -q
     ```
2. **Preserve Clean Architecture**:
   - `models.py`: Database schema definitions only.
   - `schemas.py`: Pydantic validation and serialization models.
   - `crud.py`: Transactional business logic with DB sessions.
   - `routers/`: Thin HTTP adapters mapping schemas to CRUD calls.
   - `email_service.py`: Asynchronous dispatching of transactional emails.
3. **Domain Ground Truth & Prompt Execution Suite**:
   - **Rebuild Prompt Suite (`prompts/`)**: For generating modules from scratch, review `prompts/README.md` and copy the dedicated prompt files (`prompts/00_*.md` to `prompts/06_*.md`).
   - **Standardized Multi-Agent Skills (`skill/`)**:
     - `skill/00_KhaoSat_NghiepVu.md`: Business domain & user requirements.
     - `skill/01_System_Architecture_Agent.md`: Compound AI system architecture.
     - `skill/02_Database_Design_Agent.md`: Database entities, constraints, and relationships.
     - `skill/03_Backend_Business_Logic_Agent.md`: Core business logic, deposit rules, VietQR, SMTP.
     - `skill/04_AI_Engineering_Gemini_Agent.md`: Gemini API integration & DB grounding.
     - `skill/05_Frontend_UIUX_SPA_Agent.md`: Modern SPA frontend, Magic Link tracking, and XSS sanitization.
     - `skill/06_QA_Test_Automation_Agent.md`: Automated test matrix & self-healing protocols.
     - `skill/07_HuongDan_NapTaiLieu_Va_VibeCoding.md`: Tiered context engineering guide & defense cheat-sheet.

---

## 2. Execution Workflows

### When Modifying Backend Endpoints
1. Update or create the schema in `backend/app/schemas.py`.
2. Implement the transactional CRUD function in `backend/app/crud.py`.
3. Wire the endpoint in the respective router in `backend/app/routers/`.
   - *Caution*: Always place static routes (like `/search`, `/magic-track`, `/summary`) **above** path-variable routes (like `/{id}`).
4. Add unit / integration tests in `backend/tests/` and verify pass status.

### When Modifying Frontend Views
1. Templates are located in `frontend/*.html`.
2. Shared client application logic is in `frontend/js/app.js`.
3. Styling uses compiled Tailwind classes from `frontend/vendor/tailwind.css`.
4. All dynamic user-supplied data inserted into the DOM must be sanitized via DOMPurify.

---

## 3. Key Commands

| Task | Command |
| :--- | :--- |
| **Run Backend Dev Server** | `.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload` |
| **Run Pytest Test Suite** | `.venv\Scripts\python.exe -m pytest backend/tests -q` |
| **Quick Start (Windows)** | `start.bat` |
| **Seed Database (Demo)** | `.venv\Scripts\python.exe scripts/setup_database.py --demo` |
| **Compile Tailwind CSS** | `.tools\node_modules\.bin\tailwindcss.cmd -i frontend/css/tailwind-input.css -o frontend/vendor/tailwind.css --minify` |
