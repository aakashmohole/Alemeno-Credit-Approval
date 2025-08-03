
# Credit Approval System Backend

A Django REST Framework based backend API for a Credit Approval System that manages customers and loan approvals based on credit scores and loan eligibility logic.

---

## Table of Contents

- [Project Setup](#project-setup)  
- [Environment Variables](#environment-variables)  
- [Database Migration & Data Injection](#database-migration--data-injection)  
- [API Endpoints](#api-endpoints)  
- [Images](#images)  
- [Notes](#notes)  

---

## Project Setup

1. **Clone the repo** (Assuming you have it locally)

2. **Create and activate a Python virtual environment**

   ```
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install required packages**

   ```
   pip install -r requirements.txt
   
   # If you don't have a requirements.txt, install these:
   pip install django djangorestframework psycopg2-binary python-dotenv openpyxl drf-yasg
   ```

4. **Configure `.env` file**

   Create a `.env` file in your project root with these variables (fill with your NeonDB Postgres details):

   ```
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_password
   DB_HOST=your_db_host
   DB_PORT=your_db_port
   ```

5. **Apply database migrations**

   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Inject initial data**

   Place provided Excel files `customer_data.xlsx` and `loan_data.xlsx` in your project root.

   Run:

   ```
   python manage.py inject_data
   ```

7. **Run the development server**

   ```
   python manage.py runserver
   ```

---

## Environment Variables

| Variable   | Description              |
|------------|--------------------------|
| DB_NAME    | Postgres database name   |
| DB_USER    | Postgres username        |
| DB_PASSWORD| Postgres password        |
| DB_HOST    | Database host URL/IP     |
| DB_PORT    | Database port (usually 5432) |

---
Certainly! Below is an enhanced **README.md** excerpt including a detailed **Data Injection** section with instructions and a placeholder for your data injection success screenshot. You can add this section into the existing README content (or merge accordingly).

## Data Injection

You need to inject the initial customer and loan data from the provided Excel files into the database as the first step after setting up your project.

### Prerequisites:

- Make sure your virtual environment is activated.
- Excel files `customer_data.xlsx` and `loan_data.xlsx` must be placed in your Django project root directory (same level as `manage.py`).

### Excel Files Details:

| File Name         | Columns                                                        |
|-------------------|----------------------------------------------------------------|
| customer_data.xlsx | Customer ID, First Name, Last Name, Age, Phone Number, Monthly Salary, Approved Limit |
| loan_data.xlsx     | Customer ID, Loan ID, Loan Amount, Tenure, Interest Rate, Monthly payment, EMIs paid on Time, Date of Approval, End Date |

### Running Data Injection

This project includes a custom Django management command to ingest data asynchronously (background worker style):

```bash
python manage.py inject_data
```

- This command will read both Excel files, create or update customers and loans into the database.
- The command will print a success message upon completion:

```
Data injection completed successfully.
```

### Troubleshooting

- Ensure `openpyxl` is installed for Excel reading:

```bash
pip install openpyxl
```

- If you get errors about file not found, make sure both Excel files are correctly named and placed in the project root.
- You can adjust the paths inside `inject_data.py` if your files are located elsewhere.

### Sample Command Output

```text
Reading customer data from customer_data.xlsx
Inserted/Updated 100 customers.
Reading loan data from loan_data.xlsx
Inserted/Updated 300 loans.
Data injection completed successfully.
```

## Images

| Screenshot Description             | Preview / Link                               |
|----------------------------------|---------------------------------------------|
| Data Injection Success Output     | ![data-injection](./images/data_injection.png above image path with your actual screenshot showing the terminal output of the data injection command.*

## API Endpoints

Base URL: `http://127.0.0.1:8000/api/`

---

### 1. **Register Customer**

**POST** `/register`

Request Body (JSON):

```
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 80000,
  "phone_number": "1234567890"
}
```

Response (201 Created):

```
{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": 80000.00,
  "approved_limit": 2880000.00,
  "phone_number": "1234567890"
}
```

---

### 2. **Check Loan Eligibility**

**POST** `/check-eligibility`

Request Body (JSON):

```
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 10.0,
  "tenure": 24
}
```

Response (200 OK):

```
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 10.0,
  "corrected_interest_rate": 12.0,
  "tenure": 24,
  "monthly_installment": 9416.67
}
```

- `approval`: whether the loan is approved or not based on credit score logic  
- `corrected_interest_rate`: adjusted interest rate if original didn't match the credit score slab  
- `monthly_installment`: EMI amount calculated based on compound interest

---

### 3. **Create Loan**

**POST** `/create-loan`

Request Body (JSON):

```
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 12.0,
  "tenure": 24
}
```

Response (201 Created if approved):

```
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved successfully.",
  "monthly_installment": 9416.67
}
```

Response (400 Bad Request if rejected):

```
{
  "loan_id": null,
  "customer_id": 1,
  "loan_approved": false,
  "message": "Loan not approved due to credit rating or limits.",
  "monthly_installment": 9416.67
}
```

---

### 4. **View Single Loan Details**

**GET** `/view-loan/{loan_id}`

Response (200 OK):

```
{
  "loan_id": 1,
  "customer": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "1234567890",
    "age": 30
  },
  "loan_amount": 200000,
  "interest_rate": 12.0,
  "monthly_installment": 9416.67,
  "tenure": 24
}
```

---

### 5. **View All Loans by Customer**

**GET** `/view-loans/{customer_id}`

Response (200 OK):

```
[
  {
    "loan_id": 1,
    "loan_amount": 200000,
    "interest_rate": 12.0,
    "monthly_installment": 9416.67,
    "repayments_left": 10
  },
  {
    "loan_id": 2,
    "loan_amount": 100000,
    "interest_rate": 15.0,
    "monthly_installment": 4700.00,
    "repayments_left": 5
  }
]
```

`repayments_left` = Total tenure - EMIs paid on time

---

## Images

*Below you can add screenshots/screens captures as proof of API working, data injections, or Swagger UI.*

| Screenshot Description         | Preview / Link                      |
|-------------------------------|-----------------------------------|
| Postman Register Customer API | ![register](./images/register.png) |
| Swagger UI Overview            | ![swagger](./images/swagger.png)   |
| Data Injection Success         | ![data-injection](./images/data_injection.png) |

_Replace the above image paths with actual screenshots you capture during testing._

---

## Additional Notes

- Use `python-dotenv` to load `.env` file automatically.
- All IDs (`customer_id`, `loan_id`) are integers and auto-generated by the database.
- Decimal fields like `approved_limit` and `monthly_installment` are returned with up to 2 decimal places.
- API validation returns appropriate HTTP status codes:
  - `201 Created` for successful resource creation  
  - `200 OK` for successful GET/check  
  - `400 Bad Request` for invalid input or failed conditions  
- For API docs, visit:  
  `http://127.0.0.1:8000/swagger/` after running the server if Swagger is set up.

---

If you want me to help generate the **Postman collection** or further detailed developer docs, just ask!

---

*Happy Coding!* 🚀
```

If you want, I can generate a **requirements.txt** sample or help with any other doc. Just let me know!