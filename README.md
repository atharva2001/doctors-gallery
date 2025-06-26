# 🩺 Doctors Gallery – Microservice-Based Appointment System

Doctors Gallery is a doctor-patient appointment booking platform built with modern backend technologies and performance-focused design. Patients can discover doctors, view available slots, and book appointments. Doctors can manage their availability with flexible slot creation and updates.

---

## 🚀 Motivation

This system is designed to bridge the gap between patients and doctors by enabling an easy, secure, and efficient booking experience. Doctors Gallery goes beyond basic CRUD operations by adopting microservices, optimizing performance, and enabling future AI integration.

---

## 🧠 Key Features

- 👨‍⚕️ Doctors can **create, edit, and manage time slots**
- 🧑‍⚕️ Patients can **browse doctors and book appointments**
- ✅ **Doctors approve or reject** appointments
- 🛡️ Secure with **JWT authentication and role-based access**
- 🚦 **Rate-limiting** to protect against DDoS
- ⚡ **Redis caching** and **database indexing** for high performance
- 🧱 Microservice architecture for scalability

---

## 🧰 Tech Stack

| Category       | Technologies                     |
|----------------|----------------------------------|
| Backend        | FastAPI                          |
| Databases      | MongoDB, PostgreSQL, SQLite      |
| ORM            | SQLAlchemy                       |
| Cache          | Redis                            |
| Security       | JWT, Role-Based Permissions, Rate-Limiting |
| Deployment     | Docker                           |
| Performance    | Async I/O, Caching, Indexing     |

---

## 🔐 Security Highlights

- **JWT token-based authentication**
- **Access-based route protection**
- **Rate limiting** to mitigate brute force and DDoS attacks

---

## ⚙️ Performance Optimizations

- ⚡ Asynchronous endpoints using FastAPI
- 🔄 Redis used to cache frequently queried database results
- 🗃️ Indexed database fields for fast read operations

---

## 📦 Deployment

This project is containerized using Docker for reliable and reproducible deployment.

```bash
# Clone the repo
git clone https://github.com/atharva2001/doctors-gallery.git
cd doctors-gallery

# Build and run the containers
docker-compose up --build
