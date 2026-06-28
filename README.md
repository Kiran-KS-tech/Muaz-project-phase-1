# Fleet Management System

A production-ready Fleet Management System for taxi/rideshare businesses. Features a Django REST Framework backend API, a React Admin Web Panel, and a Flutter Driver Mobile Application.

---

## Technical Stack Overview

### Backend API (`/backend`)
* **Core:** Python 3.12, Django 5.0, Django REST Framework
* **Auth:** JSON Web Token (JWT) using SimpleJWT, Phone OTP authentication
* **Task Queues:** Celery (Asynchronous operations & Periodic scheduling via Celery Beat)
* **Broker & DB:** Redis & PostgreSQL
* **Production Static Server:** WhiteNoise
* **Audit Trail:** Dynamic thread-local database signal logs

### Admin Control Panel (`/admin-frontend`)
* **Core:** React 18, Vite, React Router 6, Axios
* **Styling:** Tailwind CSS, custom glassmorphism components
* **Mode:** Dual API / Offline simulation fallback

### Driver Companion App (`/driver-mobile`)
* **Core:** Flutter 3, Dart
* **State Management:** Provider
* **Network client:** Dio (with JWT Bearer interceptor)
* **Operations:** Uber screenshot upload, CNG receipt scan, Cash Advance request forms

---

## Directory Structure

```
fleet-management/
├── backend/
│   ├── config/             # Django settings, celery, URLs routing
│   ├── apps/               # Custom modular applications
│   │   ├── accounts/       # User profiles, RBAC permission roles, OTP
│   │   ├── drivers/        # Driver management (Aadhaar, details)
│   │   ├── cars/           # Vehicle status, insurance, maintenance alerts
│   │   ├── documents/      # Expiries check daily (Celery task)
│   │   ├── earnings/       # Uber screenshot uploads & OCR status
│   │   ├── expenses/       # Fuel/CNG bill logging & OCR processing
│   │   ├── advances/       # Cash advance requests & approval actions
│   │   ├── settlements/    # Weekly settlement calculations
│   │   ├── reports/        # Vehicle profitability, PDF/Excel/CSV exports
│   │   ├── audit/          # Record update changes signal logger
│   │   └── ocr/            # Google Vision / AWS Textract OCR service
│   ├── requirements.txt
│   └── Dockerfile
├── admin-frontend/         # Vite React dashboard client
│   ├── src/
│   │   ├── pages/          # Login, Dashboard, Drivers, Cars, Settlements
│   │   └── services/       # Axios API client & mock database fallback
│   └── tailwind.config.js
├── driver-mobile/          # Flutter companion app
│   ├── lib/
│   │   ├── screens/        # Login, Dashboard, Advance requests
│   │   ├── services/       # Dio API service layer
│   │   └── providers/      # Auth state manager
│   └── pubspec.yaml
├── docker-compose.yml      # Local multi-container configuration
└── render.yaml             # Render Blueprint manifest
```

---

## Local Development Quickstart

Ensure you have [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/) installed.

### 1. Launch Environment via Docker
From the project root directory, run:
```bash
docker-compose up --build
```
This spins up:
* **PostgreSQL** at `localhost:5432`
* **Redis** at `localhost:6379`
* **Django Web API** at `http://localhost:8000`
* **Celery Worker & Celery Beat** (scheduler running tasks in background)

### 2. Access the Backend Admin Panel
Create a Django superuser:
```bash
docker exec -it fleet_api python manage.py createsuperuser
```
Access Django native admin at: `http://localhost:8000/admin/`

### 3. Launch React Admin Panel
Navigate to `/admin-frontend` and run:
```bash
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.
* Use `Demo Login` to instantly navigate using offline simulation mode, OR
* Login using the credentials: `admin@fleetmanage.com` / `adminpassword123` (requires Docker API services to be online).

### 4. Build Flutter Driver App
Navigate to `/driver-mobile` and run:
```bash
flutter pub get
flutter run
```
* Use any phone number to trigger a login.
* The mock environment will print the generated OTP to the terminal console / toast a notification. Enter `123456` or the printed code to authenticate.
