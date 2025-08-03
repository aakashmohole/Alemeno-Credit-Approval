
# Credit Approval System Backend

A Django REST API service for banking-style customer management, loan eligibility, and approval workflows, with PostgreSQL (NeonDB) and Docker support.



## Images

*Below you can add screenshots/screens captures as proof of API working, data injections, or Swagger UI.*

| Screenshot Description         | Preview / Link                      |
|-------------------------------|-----------------------------------|
| Postman Register Customer API | ![register](./images/register.png) |
| Swagger UI Overview            | ![swagger](./images/swagger.png)   |
| Data Injection Success         | ![data-injection](./images/data_injection.png) |

_Replace the above image paths with actual screenshots you capture during testing._

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup: Local Development](#setup-local-development)
- [Setup: Docker (Production/Cloud)](#setup-docker-productioncloud)
- [Database & Initial Data Injection](#database--initial-data-injection)
- [API Endpoints & Examples](#api-endpoints--examples)
- [Swagger/OpenAPI Documentation](#swaggeropenapi-documentation)
- [Proof Screenshots](#proof-screenshots)
- [Troubleshooting](#troubleshooting)

## Features
- Injection of data from excel to database
- Customer registration with auto-calculated approved limit.
- Loan eligibility checking based on historical repayment data.
- Compound interest EMI calculation.
- Controlled loan approval and rejection with clear reasons.
- View loan(s) by customer or loan ID.
- Interactive API documentation (Swagger UI).
- NeonDB/Postgres integration.
- **Easy deployment via Docker Compose.**

## Tech Stack

- Django 4+, Django REST Framework
- PostgreSQL (NeonDB cloud DB)
- Docker & Docker Compose
- Python 3.10+
- Openpyxl (for Excel injection)
- drf-yasg (Swagger Documentation)

## Project Structure

```
credit_approval/
│
├── core/                  # Django app (business logic, models, views)
│
├── credit_approval/       # Project folder (settings, wsgi, urls)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── manage.py
├── customer_data.xlsx     # Input data
├── loan_data.xlsx         # Input data
└── ... (other files)
```

## Setup: Local Development

1. **Clone the repository**
2. **Create a virtual environment & activate**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # (If no requirements.txt: pip install django djangorestframework psycopg2-binary python-dotenv openpyxl drf-yasg gunicorn)
   ```
4. **Configure `.env`** with your NeonDB credentials (do not commit real data):
   ```
   NEON_DATABASE_URL= your_db_url
   SECRET_KEY=your_secret
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=*
   ```
5. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. **Inject initial Excel data**
   - Place `customer_data.xlsx` and `loan_data.xlsx` in the project root.
   ```bash
   python manage.py inject_data
   ```
7. **Run server**
   ```bash
   python manage.py runserver
   ```

## Setup: Docker (Production/Cloud)

1. **Build Docker image**
   ```bash
   docker-compose build
   ```
2. **Launch all services**
   ```bash
   docker-compose up
   ```
   - Server will be live at: [http://localhost:8000/](http://localhost:8000/)
3. **Inject initial data (run in separate terminal if needed)**
   ```bash
   docker-compose run web python manage.py inject_data
   ```

No need to Dockerize the database: **Django connects directly to NeonDB via `.env`**.

## Database & Initial Data Injection

**Data files required:**
- `customer_data.xlsx` (Customer ID, First Name, Last Name, Age, Phone Number, Monthly Salary, Approved Limit)
- `loan_data.xlsx` (Customer ID, Loan ID, Loan Amount, Tenure, Interest Rate, Monthly payment, EMIs paid on Time, Date of Approval, End Date)

**On inject success:**
```
Data injection completed successfully.
```

## API Endpoints & Examples

Base URL: `http://localhost:8000/api/`

### EXAMPLE VIDEO PROF-

[![Watch the video](https://youtu.be/HLHRf7H_2BU?si=Y3aeEr7eke4UJgPS)](https://youtu.be/HLHRf7H_2BU?si=Y3aeEr7eke4UJgPS)


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

Response:
```json
{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": 80000.00,
  "approved_limit": 2880000.00,
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
Response (`approval`, `corrected_interest_rate`, etc. as per rules).
```json
{
  "customer_id": 1,
  "approval" : true,
  "interest_rate": 5%,
  "corrected_interest_rate": 8.0%,
  "tenure": 24,
  "monthly_installment" : ....
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
Response shows approval and monthly EMI.

```json
{
  "loan_id": null,
  "customer_id": "1",
  "loan_approved": false,
  "message": "Total EMIs exceed 50% of monthly salary.",
  "monthly_installment": 0
}
```

### 4. View Loan Details
**GET** `/view-loan/{loan_id}`

```json
{
  "loan_id": "7507",
  "customer": {
    "id": "132",
    "first_name": "Allan",
    "last_name": "Palacios",
    "phone_number": "9712913338",
    "age": 54
  },
  "loan_amount": 800000.0,
  "interest_rate": 13.01,
  "monthly_installment": 23406.0,
  "tenure": 63
}

```

### 5. View Loans by Customer
**GET** `/view-loans/{customer_id}`

```json
[
  {
    "loan_id": "1198",
    "loan_amount": 900000.0,
    "interest_rate": 14.82,
    "monthly_installment": 32147.0,
    "repayments_left": 49
  },
  {
    "loan_id": "3535",
    "loan_amount": 800000.0,
    "interest_rate": 16.94,
    "monthly_installment": 30292.0,
    "repayments_left": 39
  },
  {
    "loan_id": "4725",
    "loan_amount": 400000.0,
    "interest_rate": 10.64,
    "monthly_installment": 12039.0,
    "repayments_left": 6
  },
  {
    "loan_id": "4189",
    "loan_amount": 100000.0,
    "interest_rate": 13.04,
    "monthly_installment": 2614.0,
    "repayments_left": 17
  }
]

```



## Swagger/OpenAPI Documentation

Interactive API docs and testing UI available at:

```
http://localhost:8000/swagger/
```

If not active, ensure `drf-yasg` is installed and your project's `urls.py` includes the schema view, as previously described.

## Proof Screenshots

| Description                | Image or Example                          |
|----------------------------|-------------------------------------------|
| Docker Compose running     | ![docker-running](images    |
| Data Injection Success     | ![data-inject](images/in       |
| Swagger API UI             | ![swagger-ui](images/swagger       |
| Test API in Postman        | ![postman-success](images     |

*Add your screenshots to an `images/` directory; update paths as needed.*

## Troubleshooting

- **Migration/Data Errors:**  
  If you ever see `invalid input syntax for type integer: ""`, delete problematic rows from your DB, or drop/recreate the dev database.
- **Docker can't find Gunicorn:**  
  `pip install gunicorn` in your `requirements.txt`.
- **DB connection issues:**  
  Verify all DB credentials in `.env` are correct for NeonDB.
- **Container not running:**  
  Check logs via `docker-compose logs web`.

**Enjoy your full-stack, production-ready Django backend!**
If you have further deployment/security/API documentation needs, reach out or consult OpenAPI at `/swagger/`.

[imageageace your real screenshots as `images/docker-up.png`, `images/inject-ok.png`, etc., in your repository to display them in this section.)*