# Production Deployment Manual

This document outlines deployment guides for releasing the Fleet Management System on Render.com and configuring production integrations.

---

## 1. Render.com Infrastructure Setups

We utilize a **Render Blueprint (`render.yaml`)** to spin up the entire production environment in one click.

### Steps to Deploy:
1. Push this codebase to a private Git repository (GitHub/GitLab).
2. Log in to your [Render Dashboard](https://dashboard.render.com/).
3. Navigate to **Blueprints** and click **New Blueprint Instance**.
4. Connect your Git repository.
5. Render will parse `render.yaml` and configure:
   * A Managed PostgreSQL database.
   * A Managed Redis instance.
   * Django Web service (`fleet-backend`).
   * Celery worker (`fleet-worker`).
   * Celery Beat scheduler (`fleet-beat`).
   * React Admin panel (`fleet-admin-panel`) hosted as a Static Site.
6. Approve the blueprint. Render will automatically build and provision the stack.

---

## 2. Environment Variables Checklist

### Django Backend API (`fleet-backend`)
Configure these keys in the Render web dashboard environment settings:

| Variable Name | Description | Recommended Value |
| --- | --- | --- |
| `SECRET_KEY` | Django security token | *Random 50-character string* |
| `DEBUG` | Deactivates dev checks | `False` |
| `ALLOWED_HOSTS` | Server host names | `fleet-backend.onrender.com` |
| `DATABASE_URL` | PostgreSQL connection string | *Injected by Render* |
| `REDIS_URL` | Redis connection string | *Injected by Render* |
| `OCR_PROVIDER` | Swaps OCR engine | `google` OR `aws` OR `mock` |
| `COMPANY_COMMISSION_PERCENTAGE` | Payout deduction pct | `15.0` (for 15% fleet cut) |
| `JWT_SECRET_KEY` | JWT signing security token | *Random 50-character string* |

### Static Site Admin Panel (`fleet-admin-panel`)
* **`VITE_API_URL`**: Set this to your live backend domain, e.g. `https://fleet-backend.onrender.com`.

---

## 3. Configuring OCR Providers

### Google Vision API
To enable production-grade Google Vision OCR for scanning Uber screenshots and CNG receipts:
1. Go to Google Cloud Console, enable the **Cloud Vision API**.
2. Create a service account and download the **JSON credentials key**.
3. Convert your JSON key to a single-line string or configure authentication credentials.
4. Set the following environment variables:
   * `OCR_PROVIDER=google`
   * `GOOGLE_VISION_API_KEY=your_vision_api_key_here`

### AWS Textract
To enable AWS Textract:
1. Create an IAM User on AWS with `AmazonTextractFullAccess` permission.
2. Generate an Access Key and Secret Key.
3. Configure these environment variables on Render:
   * `OCR_PROVIDER=aws`
   * `AWS_ACCESS_KEY_ID=your_access_key`
   * `AWS_SECRET_ACCESS_KEY=your_secret_key`
   * `AWS_TEXTRACT_REGION_NAME=us-east-1` (or your preferred region)

---

## 4. Production Security Checklists
* **SSL/HTTPS ONLY:** Render automatically generates Let's Encrypt SSL certificates for all static sites and web endpoints. Ensure all client queries hit `https://`.
* **Database Backups:** Enable daily snapshots in the Render PostgreSQL dashboard settings.
* **CORS Limits:** In `/backend/config/settings.py`, replace `CORS_ALLOW_ALL_ORIGINS = True` with `CORS_ALLOWED_ORIGINS = ["https://your-admin-site.onrender.com"]` pointing specifically to your static panel address.
* **API Throttling:** Configure DRF default throttle rates inside `REST_FRAMEWORK` config block to protect resources against DDoS or login spamming.
