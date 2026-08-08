# TWC Ecommerce

Django storefront for TWC Online Store. The active customer journey is intentionally focused on four pages:

- Home
- Shop and product detail
- Checkout with an in-page cart drawer
- Thank-you / order-complete page

The cart is stored in the Django session and is exposed through the drawer. The current checkout completion is demo-mode: it records the submitted address and creates a signed session snapshot for the thank-you page without calling the legacy order POST API.

## Project story

This was my first full-stack project. I built the original e-commerce application manually before using AI, then spent several years migrating and improving it. I recently returned to the codebase with Codex to audit the storefront, simplify the active customer journey, modernize the interface, and make the cart and demo checkout easier to maintain.

That history is part of the project: it is an example of building a working system from the ground up, learning from its accumulated complexity, and then using AI-assisted development to make focused improvements.

## Architecture at a glance

This is a real Django application rather than a tutorial prototype. Its supporting architecture includes:

- Django with PostgreSQL
- Celery and Redis configuration for background work
- Docker, Nginx, and Supervisor deployment configuration
- Tailwind CSS, Bootstrap, jQuery, and SweetAlert in the storefront assets
- Static and media file handling
- Separate Django applications for the cart, storefront, and user areas
- Legacy HTML assets and templates under `html/` and `src/`

The active customer-facing flow is intentionally smaller than the full legacy codebase:

```text
Home → Shop / Product detail → Checkout with cart drawer → Thank-you page
```

## Current status

This repository should be presented as an early full-stack e-commerce application that was manually built and later revisited as an exercise in AI-assisted modernization. It is not currently a production order-processing system: the legacy order API is defunct, so checkout completion is simulated for demonstration purposes.

The README and code intentionally make that limitation explicit. Before production use, the order integration, credentials, external service configuration, deployment security settings, and operational monitoring would need to be replaced or revalidated.

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

- The active product catalog is a checked-in snapshot at `src/onlinestore/data/products.json`, so the home, shop, detail, category-count, and cart stock flows continue working if the product API goes offline. Product image URLs in that snapshot may still point to remote storage.
- Address lookup prefers the configured service and falls back to the checked-in `src/onlinestore/data/addresses.json` snapshot if the service is unavailable. Other legacy integrations still use their configured services.
- The cart no longer depends on a separate cart page; checkout is opened from the drawer.
- Adding a product opens the drawer and updates the cart state in the page.
- Removing an item requires confirmation and uses the drawer toaster for feedback.
- The final order step is simulated until a replacement order API is available.
- The `html/` directory contains legacy/static HTML material retained for reference.

### Refreshing the product snapshot

The snapshot is intentionally versioned and is not refreshed automatically at runtime. When the source catalog is available, save the successful JSON response from the product endpoint to `src/onlinestore/data/products.json`, preserving the top-level `success` and `products` fields, then run:

```bash
python -m json.tool src/onlinestore/data/products.json >/dev/null
python src/manage.py check
```

The address snapshot uses the same response shape as the address endpoint. Save a successful response to `src/onlinestore/data/addresses.json` when the source data changes, then validate it with `python -m json.tool`.

## Security before deployment

Review `src/TWC/settings/base.py` and replace any legacy fallback credentials or external service defaults with environment-only values before deploying publicly. Set `DEBUG=False`, restrict `ALLOWED_HOSTS`, configure trusted origins and secure cookies for the real domain, and run `python manage.py check --deploy` against the production settings.
