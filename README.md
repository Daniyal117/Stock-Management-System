# Stock Management System

This project is a simple stock management system built with Django. It helps users manage stock data, view transactions, and get stock prices quickly using Redis caching. The application has a clear API structure and is easy to deploy with Docker.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [API Endpoints](#api-endpoints)
6. [Caching with Redis](#caching-with-redis)
7. [Docker Setup](#docker-setup)
8. [Contributing](#contributing)
9. [License](#license)

---

## Project Overview

This application allows users to:
- Register and manage their accounts.
- View stock information like prices and trading volume.
- Buy and sell stocks.
- See a history of their transactions.

It uses Redis to store frequently accessed data, making it faster to retrieve information.

---

## Features

- User registration and account management.
- Adding and viewing stock information.
- Keeping track of user transactions.
- Fast data retrieval using Redis caching.
- Documentation for APIs.
- Easy deployment with Docker.

---

## Installation

### 1. Clone the Repository

Use this command to clone the project:

```bash
git clone https://github.com/Daniyal117/Stock-Management-System.git
cd Stock-Management-System
```

### 2. For Windows:

```bash
python3 -m venv env
. env\scripts\activate 
```

### 3. For macOS/Linux:


```bash
python3 -m venv env
source env/bin/activate
```

### 4.pip install -r requirements.txt
```bash
pip install -r requirements.txt
```

### 5. Apply Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```
### 6. Run the Server
```bash
python3 manage.py runserver
```
You can access the app at http://127.0.0.1:8000.

### 5. USAGE
API Documentation: Access the API documentation at http://127.0.0.1:8000/swagger/ to see available endpoints.

## API Endpoints

Here are some important API endpoints:

| Method | Endpoint                        | Description                         |
|--------|---------------------------------|-------------------------------------|
| POST   | `/users/`                       | Register a new user                |
| GET    | `/users/{username}/`            | Get user data                      |
| DELETE | `/users/{username}/`            | Delete a user                      |
| POST   | `/stocks/`                      | Add stock data                     |
| GET    | `/stocks/`                      | Get all stocks                     |
| POST   | `/transactions/`                | Create a new transaction           |
| GET    | `/transactions/{username}/`      | Get all transactions for a user    |



###  Docker Setup:
To make it easier to deploy this project, we use Docker. Here’s how to set it up

### Build the Docker Image
Run this command to build the Docker image:
```bash
docker build -t app .
```
### Run the Docker Container
Use this command to start the application in a Docker container:
```bash
docker run -p 8000:8000 app
```


