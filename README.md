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

## 4. Deploy the backend to Render

The root `render.yaml` defines a FastAPI web service and PostgreSQL database. To deploy:

1. Sign in to Render and open the [new Blueprint page](https://dashboard.render.com/blueprints).
2. Connect `MURTHY-BUNNY/murthy-portfolio`, select `main`, and apply the Blueprint.
3. Wait for the web service and database to become available. The API URL is `https://murthy-portfolio-contact-api.onrender.com`.
4. The Contact page is configured to submit to this API.

This Blueprint uses Render's **free** web and PostgreSQL plans. Free web services can sleep when idle, so the first request can take about a minute. Render's free PostgreSQL database expires after 30 days; back up or upgrade the database before it expires if you need to keep submissions. No hosted service can be created from GitHub Pages alone; you must authorize Render and apply the Blueprint in your account.

GitHub Pages hosts only the static HTML/CSS/JS frontend; it does not run FastAPI. `DATABASE_URL` selects PostgreSQL in the deployed service; local development continues to use SQLite unless you set `DATABASE_URL`.

The deployment URL is not available until the Blueprint has been created in your Render account. Until the frontend is configured with that URL, the contact form will show the email fallback rather than claim a message was delivered.

## 5. Email notifications

The API saves submissions to PostgreSQL and can email a notification through Brevo SMTP. In Render, open the web service's **Environment** settings and add:

- `SMTP_HOST` = `smtp-relay.brevo.com`
- `SMTP_PORT` = `587`
- `SMTP_USERNAME` = the SMTP login shown in Brevo
- `SMTP_PASSWORD` = a Brevo SMTP key (not an API key)
- `MAIL_FROM` = a sender address verified in Brevo
- `MAIL_TO` = `kothagundlamurthy@gmail.com` (optional; this is the default recipient)

Save the variables and redeploy the web service. Until SMTP credentials and a verified sender are configured, messages are still saved, but the API explicitly reports that email notification was not sent. Use Render's environment settings for credentials; never commit them to GitHub.

## Security notes

- No public endpoint exposes stored messages.
- Submissions are stored even if email delivery is unavailable.
- Before public production use, add rate limiting, spam protection/CAPTCHA, monitoring, and a retention policy.
- Never put passwords, API keys, or other secrets in frontend JavaScript.
