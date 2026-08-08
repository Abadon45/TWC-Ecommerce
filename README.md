# TWC Ecommerce

Django storefront for TWC Online Store. The active customer journey is intentionally focused on four pages:

- Home
- Shop and product detail
- Checkout with an in-page cart drawer
- Thank-you / order-complete page

The cart is stored in the Django session and is exposed through the drawer. The current checkout completion is demo-mode: it records the submitted address and creates a signed session snapshot for the thank-you page without calling the legacy order POST API.

## Requirements

- Python 3.10+
- PostgreSQL 14+ (the default settings expect an external PostgreSQL database)
- Node.js is optional and is only needed when changing the frontend package assets

## Local setup

```bash
git clone git@github.com:abadon45/TWC-Ecommerce.git
cd TWC-Ecommerce

python -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt

export DJANGO_SETTINGS_MODULE=TWC.settings.local
python src/manage.py migrate
python src/manage.py runserver
```

Open `http://127.0.0.1:8000/`.

Put local credentials and API overrides in `.env`; do not commit that file. The settings module reads environment values for database, host, debug, and external API configuration. Production secrets should be supplied through the deployment environment rather than stored in source control.

## Docker

Build and run the application image:

```bash
docker build -t twc-ecommerce .
docker run --rm --env-file .env -p 8000:8000 twc-ecommerce
```

The image uses `TWC.settings.production`, installs the pinned Python dependencies, collects static files, and starts Gunicorn on port `8000`. The container expects PostgreSQL and any external services to be reachable using the values supplied in `.env`.

Before the first production run, apply migrations from a one-off container:

```bash
docker run --rm --env-file .env twc-ecommerce python manage.py migrate
```

At minimum, provide a strong `SECRET_KEY`, `DEBUG=False`, PostgreSQL connection variables (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, and `POSTGRES_PORT`), and the external API values required by the storefront.

## Verification

Run the Django system checks and the cart regression tests:

```bash
python src/manage.py check
python src/manage.py test cart -v 1
```

The cart tests cover drawer-oriented checkout completion, demo thank-you rendering, address persistence, and empty-cart handling.

## Project notes

- Product and address data still come from the configured dashboard APIs.
- The cart no longer depends on a separate cart page; checkout is opened from the drawer.
- Adding a product opens the drawer and updates the cart state in the page.
- Removing an item requires confirmation and uses the drawer toaster for feedback.
- The final order step is simulated until a replacement order API is available.

## Security before deployment

Review `src/TWC/settings/base.py` and replace any legacy fallback credentials or external service defaults with environment-only values before deploying publicly. Set `DEBUG=False`, restrict `ALLOWED_HOSTS`, configure trusted origins and secure cookies for the real domain, and run `python manage.py check --deploy` against the production settings.
