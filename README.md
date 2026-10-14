# AI Powered Placement Management System

Final-year project prototype using Python Flask + SQLite + an explainable placement matching engine.

## Run on Windows
1. Install Python 3.10+.
2. Extract the ZIP.
3. Open Command Prompt in the project folder.
4. Run `setup.bat` once.
5. For later runs, use `run.bat`.
6. Open http://127.0.0.1:5000

The database is created automatically at `database/placement.db`.

## Modules
Dashboard, Students, Companies/Jobs, AI Recommendations, Applications and JSON API.

## AI scoring
CGPA eligibility, skill matching, projects, internships, communication and aptitude are combined into a transparent 0–100 match score. A real ML model can later replace this baseline when historical labeled placement data is available.
