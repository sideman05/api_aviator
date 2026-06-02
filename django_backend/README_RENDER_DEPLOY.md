# Render Deployment

This guide deploys the Django backend to Render with the no-cost setup:

- One free web service for the API
- The monitor running inside that web service
- One PostgreSQL database

Important: Render does not offer the `free` plan for background workers. To
avoid the paid worker, set `AVIATOR_RUN_MONITOR_IN_WEB=True` and run only one
Gunicorn worker process.

In this no-cost mode the monitor starts from the web service when the monitor
page or status endpoint is opened. If the free web service sleeps or restarts,
the monitor will stop until the service wakes up again.

The monitor dashboard now renders recent logs and recent odds server-side, so
it still shows useful data even when the live stream endpoint is disabled.

## Files Used

Important backend files:

```text
api/django_backend/render.yaml
api/django_backend/start.sh
api/django_backend/requirements.txt
api/django_backend/manage.py
```

From the full Flutter project, there are two Render YAML files:

```text
api/render.yaml
api/django_backend/render.yaml
```

Use `api/render.yaml` when the deployed repository/root directory is the `api`
folder. It contains `rootDir: django_backend`.

Use `api/django_backend/render.yaml` when the deployed repository/root directory
is already the Django backend folder.

If your GitHub repository root is the full Flutter project folder, create the
Render services manually with the commands below, or move the appropriate YAML
to the repository root before creating a Render Blueprint.


## Option 1: Deploy With render.yaml

In Render:

1. Create a new Blueprint.
2. Connect your GitHub repository.
3. Select the correct `render.yaml`.
4. Let Render create:
   - `aviator-backend-web`
   - `aviator-backend-db`

The web service uses the `free` plan.

The YAML already sets:

```bash
buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput
startCommand: bash start.sh
```

## Option 2: Manual Render Setup

Create a PostgreSQL database first.

If you are using Neon instead of a Render database, skip the Render database
step and copy the Neon direct connection string into `DATABASE_URL` for the web
service.

Then create a Python web service:

```bash
Build Command:
pip install -r requirements.txt && python manage.py collectstatic --noinput

Start Command:
bash start.sh
```

## Required Environment Variables

Set these on the web service:

```bash
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.onrender.com
DATABASE_URL=<your Render PostgreSQL connection string>
DJANGO_SECRET_KEY=<one strong secret>
AVIATOR_RUN_MONITOR_IN_WEB=True
AVIATOR_AUTO_START_MONITOR=True
GUNICORN_WORKERS=1
```

For Neon, use:

```bash
DATABASE_URL=<your Neon direct postgresql://... connection string>
DATABASE_CONN_MAX_AGE=600
```

If you choose the Neon pooled URL, set `DATABASE_CONN_MAX_AGE=0`.

Optional monitor login variables:

```bash
AVIATOR_PHONE=<phone number>
AVIATOR_PASSWORD=<password>
AVIATOR_BROWSER=auto
AVIATOR_CHECK_INTERVAL=0.5
AVIATOR_WAIT_TIMEOUT=45
AVIATOR_MAX_IFRAME_DEPTH=6
```

Optional admin access-key variable:

```bash
AVIATOR_ACCESS_KEY_ADMIN_TOKEN=<secret admin token>
```

## Important Start Command

Use this for the web service:

```bash
bash start.sh
```

Do not use plain Gunicorn unless you also run migrations separately.

`bash start.sh` runs:

```bash
python manage.py migrate --noinput
gunicorn aviator_backend.wsgi:application
```

This prevents missing PostgreSQL tables from causing HTTP 500 errors.

## Flutter API Base URL

When building the Flutter app for the hosted backend, pass your Render URL:

```bash
flutter build apk --dart-define=AVIATOR_API_BASE_URL=https://your-service-name.onrender.com
```

The app will call:

```text
POST /api/access-keys/validate/
GET /api/prediction/
```

## Verify Deployment

After Render finishes deploying, open these URLs:

```text
https://your-service-name.onrender.com/monitor/status/
https://your-service-name.onrender.com/monitor/odds/
```

Expected result:

```json
{"success": true}
```

For the monitor status endpoint, `running` should become `true` after the web
service starts the in-process monitor.

The prediction endpoint may return `409` until the monitor reports that a round
has ended. That is expected and is not a server crash.

## If You Still Get HTTP 500

Check Render logs for messages like:

```text
relation "api_app_monitorstate" does not exist
relation "api_app_monitorlog" does not exist
no such table
```

That means migrations did not run on the database used by the web service.

Fix:

```bash
python manage.py migrate --noinput
```

Then redeploy the web service with:

```bash
bash start.sh
```
