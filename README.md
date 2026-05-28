# 🚗 Car Dealer Evaluation Platform 

**Project Name:** Car Dealer Evaluation Platform
**Developer:** TSERENNADMID TUMUR-OCHIR  
**Course:** IBM Full Stack Application Development Capstone
**Repository Name:** dealership-review-app

## 🌟 Features

- **Browse Dealerships**: View dealerships by state with detailed information across
- **User Authentication**: Secure login/register system
- **Review System**: Read and write dealership reviews
- **Sentiment Analysis**: AI-powered review sentiment detection
- **Responsive Design**: Mobile-friendly interface
- **State-wise Filtering**: Filter dealerships

## 🛠️ Tech Stack

- **Frontend**: React.js
- **Backend**: Django (Python)
- **API**: Node.js/Express
- **Database**: MongoDB + SQLite
- **Containerization**: Docker
- **Cloud**: IBM Cloud Code Engine

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- Docker
- Git

### Installation

1. **Clone Repository**

```bash
git clone https://github.com/Nandia203nad/IBM_Full-Stack-Application-Development-Capstone-Project.git
cd Cars Dealership Portal
```

2. **Start Django Backend**

```bash
cd server
py manage.py runserver
```

3. **Start MongoDB Service** (New Terminal)

```bash
cd server/database
docker-compose up
```

4. **Start React Frontend** (New Terminal)

```bash
cd server/frontend
npm install
npm start
```

### Access Points

- **Frontend**: http://localhost:3000
- **Django Admin**: http://localhost:8000/admin
- **API**: http://localhost:3030

## 📁 Project Structure

```
├── server/
│   ├── djangoapp/          # Django backend
│   ├── frontend/           # React frontend
│   ├── database/           # MongoDB setup
│   └── requirements.txt    # Python dependencies
├── README.md
└── .gitignore
```
- Indian automotive brands integration

- Tata Motors
- Mahindra
- Honda
- Toyota
