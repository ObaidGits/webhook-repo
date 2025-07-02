# webhook-repo

Flask server to receive GitHub webhooks and display live activity.

## Run locally

1. Install Python 3.11+
2. Create `.env` with `MONGO_URI`
3. `pip install -r requirements.txt`
4. `python server/app.py`
5. Open `http://localhost:5000/`

## Deploy to Render

Push to GitHub → Create new Web Service → Connect → set `gunicorn server.app:app` → Done.

Webhook URL: `https://YOUR-RENDER-URL/webhook`
