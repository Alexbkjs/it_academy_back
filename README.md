# 🚀 Backend FastAPI with PostgreSQL and SQLAlchemy

Backend built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**. This project serves as a foundation for modern web applications and APIs.

## 🛠️ Features

- **FastAPI**: High-performance Python web framework for building APIs.
- **PostgreSQL**: Powerful, open-source relational database.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library for Python.
- **Alembic**: Database migrations tool for SQLAlchemy.

## 📝 Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.8+**
- **PostgreSQL**
- **Git**

## 📦 Installation and Setup

Follow these steps to clone the repository and set up the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/UPCoD-UNKD/it-academy-rpg-back.git
cd it-academy-rpg-back
```

### 2. Create and Activate a Virtual Environment

For Unix/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up the PostgreSQL Database

- #### 4.1. Create a PostgreSQL database:

```bash
createdb your_database_name
```

- #### 4.2. Update the Database Connection Settings:
  Update the .env file with your PostgreSQL credentials:

```bash
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/your_database_name

```
- #### 4.3. Create an initial “alembic” migration:
  

```bash
alembic init alembic 

```
- #### 4.4. Replace the content of alembic/env.py with content in w_alembic_custom_config/env.py:
 

```bash


```
- #### 4.4. Initial database setup:
  

```bash
alembic revision --message "Initial database setup"

```

#### 5. Apply Database Migrations

```bash
alembic upgrade head
```
- #### 5.1. Filling the Database:  

```bash
python3 seed_db_with_related_v2.py

```

#### 6. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at http://127.0.0.1:8000.



## ✅ Running Tests

To run tests, you can use pytest:

```bash
pytest
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue.

1. - Fork the repository.
2. - Create a new branch (git checkout -b feature-branch).
3. - Commit your changes (git commit -m 'Add some feature').
4. - Push to the branch (git push origin feature-branch).
5. - Open a Pull Request.

## 🛡️ License

This project is licensed under the Apache License. See the LICENSE file for more details.

## 🌟 Acknowledgements

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
