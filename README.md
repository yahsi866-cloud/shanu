# Vehicle API

## Deploy to Render

1. Push to GitHub
2. Connect to Render
3. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`
