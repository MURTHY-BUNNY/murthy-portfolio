# Murthy Portfolio — Full Backend Starter

This package provides a ready-to-run FastAPI backend and SQLite database for contact messages, plus a sample frontend integration.

## 1. Open in VS Code

1. Download and extract `Murthy_Portfolio_Full_Backend.zip`.
2. In VS Code, select **File → Open Folder** and open the extracted folder.
3. Open a terminal and enter the backend folder:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload
```

If PowerShell blocks activation, run this for the current terminal only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 2. Verify it works

- Health check: http://127.0.0.1:8000/
- Database check: http://127.0.0.1:8000/api/health
- Interactive API documentation: http://127.0.0.1:8000/docs

In `/docs`, open `POST /api/contact` → **Try it out** and use:

```json
{
  "name": "Murthy",
  "email": "murthy@example.com",
  "subject": "Portfolio enquiry",
  "message": "Hello, I would like to discuss a project."
}
```

Expected result: HTTP `201` and a success message. The database file is created at `backend/portfolio.db` by default.

## 3. Use the Contact page form

The existing `Contact.html` is connected to the API. Start the backend and frontend with VS Code Live Server to submit the form. If Live Server uses another port, add that exact origin to `FRONTEND_ORIGINS` in `backend/.env`, then restart Uvicorn. If the hosted API is not configured or cannot be reached, the form offers a prefilled email link and does not claim the message was sent. The standalone `frontend-integration/contact-form-example.html` is also available for testing.

On deployment, set the form's `data-api-base` attribute in `Contact.html` to the backend's HTTPS URL, or update the default `API_BASE` in `frontend-integration/contact-form.js`. Configure `FRONTEND_ORIGINS` on the backend with the frontend's exact origin.

## 4. Deployment reality check

GitHub Pages only hosts static HTML/CSS/JS. It does not run FastAPI. Deploy this backend folder to a Python-capable host and configure its `FRONTEND_ORIGINS` environment variable with the frontend origin, e.g. `https://murthy-bunny.github.io`.

SQLite is suitable for local learning. On a backend host, the filesystem may be temporary; configure a persistent disk and set `DATABASE_PATH`, or use managed PostgreSQL. A successful local test does not mean the API is already live.

## Security notes

- No public endpoint exposes stored messages.
- This starter does not send email notifications; it saves submissions to SQLite.
- Before public production use, add rate limiting, spam protection/CAPTCHA, monitoring, and a retention policy.
- Never put passwords, API keys, or other secrets in frontend JavaScript.
