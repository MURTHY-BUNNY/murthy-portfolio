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

## 3. Test the sample contact form

For a quick local test, open `frontend-integration/contact-form-example.html` using VS Code Live Server. If Live Server uses another port, add that exact origin to `FRONTEND_ORIGINS` in `backend/.env`, then restart Uvicorn.

The integration script expects a form with `id="contact-form"` and input names `name`, `email`, `subject`, `message`. Copy/adapt `frontend-integration/contact-form.js` for your existing `Contact.html`; don't replace your portfolio styling with the sample HTML.

## 4. Connect your existing portfolio

1. Keep the existing portfolio frontend on GitHub Pages.
2. In your `Contact.html`, ensure the form fields have the expected `name` attributes and `id="contact-form"`.
3. Add `<p id="form-status" role="status" aria-live="polite"></p>` to show success/error feedback.
4. Add the JavaScript file after the form.
5. During local testing, use `http://127.0.0.1:8000` as `API_BASE`.
6. After deploying the backend, change `API_BASE` to its HTTPS URL.

## 5. Deployment reality check

GitHub Pages only hosts static HTML/CSS/JS. It does not run FastAPI. Deploy this backend folder to a Python-capable host and configure its `FRONTEND_ORIGINS` environment variable with the frontend origin, e.g. `https://murthy-bunny.github.io`.

SQLite is suitable for local learning. On a backend host, the filesystem may be temporary; configure a persistent disk and set `DATABASE_PATH`, or use managed PostgreSQL. A successful local test does not mean the API is already live.

## Security notes

- No public endpoint exposes stored messages.
- This starter does not send email notifications; it saves submissions to SQLite.
- Before public production use, add rate limiting, spam protection/CAPTCHA, monitoring, and a retention policy.
- Never put passwords, API keys, or other secrets in frontend JavaScript.
