# Credit Approval System Backend

A Django REST API service for banking-style customer management, loan eligibility, and approval workflows, with PostgreSQL, Redis, and Celery support.

---

## Features
- Ingestion of data from excel to database via Celery background tasks.
- Customer registration with auto-calculated approved limit.
- Loan eligibility checking based on historical repayment data.
- Compound interest EMI calculation.
- Controlled loan approval and rejection with clear reasons.
- View loan(s) by customer or loan ID.
- Unit Testing for core logic.
- Interactive API documentation (Swagger UI).
- PostgreSQL integration.
- **Easy deployment via Docker Compose.**

## Tech Stack

- Django 4+, Django REST Framework
- PostgreSQL
- Redis & Celery (Asynchronous tasks)
- Docker & Docker Compose
- Python 3.10+
- Pandas & Openpyxl (for Excel ingestion)
- drf-yasg (Swagger Documentation)

## Project Structure

```
credit_approval/
│
├── core/                  # Django app (business logic, models, views, tasks)
│
├── credit_approval/       # Project folder (settings, wsgi, urls, celery)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── manage.py
├── customer_data.xlsx     # Input data
├── loan_data.xlsx         # Input data
└── ... (other files)
```

## Setup & Deployment

1. **Clone the repository**
2. **Configure `.env`** (Use the provided structure):
   ```
   DATABASE_URL=postgres://postgres:postgres@db:5432/postgres
   SECRET_KEY=your_secret
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=*
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/0
   ```
3. **Launch all services via Docker Compose**
   ```bash
   docker-compose up -d --build
   ```
   - Web Server: [http://localhost:8000/](http://localhost:8000/)
   - Swagger Documentation: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)

4. **Inject initial Excel data**
   - The ingestion is handled by a management command that triggers a Celery task.
   ```bash
   docker-compose exec web python manage.py inject_data
   ```

## API Endpoints

Base URL: `http://localhost:8000/api/`

### 1. Register Customer
**POST** `/register`
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 80000,
  "phone_number": "1234567890"
}
```

### 2. Check Loan Eligibility
**POST** `/check-eligibility`
```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 12.0,
  "tenure": 24
}
```

### 3. Create Loan
**POST** `/create-loan`
```json
{
  "customer_id": 1,
  "loan_amount": 150000,
  "interest_rate": 14,
  "tenure": 12
}
```

### 4. View Loan Details
**GET** `/view-loan/{loan_id}`

### 5. View Loans by Customer
**GET** `/view-loans/{customer_id}`

---

### Swagger/OpenAPI Documentation
Interactive API docs and testing UI available at:
`http://localhost:8000/swagger/`
