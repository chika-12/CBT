# KDC Portal - School Management System

A comprehensive Django-based school management platform featuring Computer-Based Testing (CBT), digital library, and cloud file management, hosted on Render with Cloudinary integration.

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Cloudinary](https://img.shields.io/badge/Cloudinary-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

## ✨ Features

### 📚 Core Modules
- **Student Management** - Complete student records and profiles
- **CBT System** - Computer-Based Testing with automated grading
- **Digital Library** - Resource management with Cloudinary integration
- **Attendance Tracking** - Real-time attendance monitoring
- **Gradebook** - Academic performance tracking
- **Timetable Management** - Schedule organization

### 🎯 CBT Features
- Randomized question selection
- Timed examinations
- Instant result computation
- Question categorization
- Answer review system

### 📁 Library Features
- Cloudinary-powered file storage
- Document categorization
- Search functionality
- Access control by user role
- Preview capabilities

### 👥 User Roles
- **Super Admin** - Full system control
- **Administrators** - School management
- **Teachers** - Content creation and grading
- **Students** - Learning and assessment
- **Parents** - Progress monitoring

## 🚀 Live Demo
Access the platform at: [https://kdc-portal.onrender.com](https://kdc-portal.onrender.com)

## 🛠️ Technology Stack

- **Backend**: Django 4.x
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: PostgreSQL (Production), SQLite (Development)
- **File Storage**: Cloudinary
- **Hosting**: Render
- **Authentication**: Django Allauth
- **Task Queue**: Celery (if applicable)
- **Caching**: Redis (if applicable)

## 📦 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Cloudinary Account
- Render Account

### Local Development Setup

1. **Clone the repository**
```bash
git clone github.com/chika-12/CBT
cd kdc-portal
pip install -r requirements.txt
venv/Scripts/activate
python manage.py runserver