# Backend API - Diplomová práca

Flask + PostgreSQL backend pre PERT+RACI projekt management systém.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (Mac/Linux)
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Database

Vytvor `.env` súbor (alebo skopíruj `.env.example`):

```env
DATABASE_URL=postgresql://postgres:daniela13@localhost:5432/diplonovka_db
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-diplomovka-2024
JWT_SECRET_KEY=dev-jwt-secret-key-diplomovka-2024
JWT_ACCESS_TOKEN_EXPIRES=3600
CORS_ORIGINS=http://localhost:9000,http://localhost:9001
HOST=0.0.0.0
PORT=5000
```

### 3. Create Database

```bash
python create_database.py
```

### 4. Seed Database

```bash
python seed_database.py
```

### 5. Run Server

```bash
python run.py
```

Server beží na: **http://localhost:5000**

---

## 📡 API Endpoints

### Health Check

```
GET /api/health
```

### Authentication

```
POST   /api/auth/register     - Register new user
POST   /api/auth/login        - Login user
GET    /api/auth/me           - Get current user
PUT    /api/auth/profile      - Update profile
POST   /api/auth/change-password - Change password
POST   /api/auth/logout       - Logout
```

### Projects

```
GET    /api/projects          - Get all projects
GET    /api/projects/:id      - Get project by ID
POST   /api/projects          - Create project
PUT    /api/projects/:id      - Update project
DELETE /api/projects/:id      - Delete project

POST   /api/projects/:id/sprints        - Create sprint
PUT    /api/projects/:id/sprints/:sid   - Update sprint
DELETE /api/projects/:id/sprints/:sid   - Delete sprint
```

### Teams

```
GET    /api/teams             - Get all team members
GET    /api/teams/:id         - Get team member by ID
POST   /api/teams             - Create team member
PUT    /api/teams/:id         - Update team member
DELETE /api/teams/:id         - Delete team member
```

### Tasks

```
GET    /api/tasks             - Get all tasks
GET    /api/tasks/:id         - Get task by ID
POST   /api/tasks             - Create task (with PERT + RACI)
PUT    /api/tasks/:id         - Update task
DELETE /api/tasks/:id         - Delete task
POST   /api/tasks/bulk-update - Bulk update tasks (PERT/RACI optimization)
```

### Experiments

```
GET    /api/experiments       - Get all experiments
GET    /api/experiments/:id   - Get experiment by ID
POST   /api/experiments       - Create experiment (Manager+)
PUT    /api/experiments/:id   - Update experiment (Manager+)
DELETE /api/experiments/:id   - Delete experiment (Manager+)
GET    /api/experiments/stats - Get experiment statistics
```

### Analytics

```
GET    /api/analytics/dashboard          - Main dashboard metrics
GET    /api/analytics/pert-raci          - PERT+RACI integration metrics
GET    /api/analytics/workload           - Team workload distribution
GET    /api/analytics/project-efficiency - Project efficiency metrics
GET    /api/analytics/comparison         - Methodology comparison data
```

---

## 🔐 Authentication

Backend používa **JWT (JSON Web Tokens)** pre autentifikáciu.

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "admin123"
}
```

Response:

```json
{
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "name": "Admin User",
    "role": "admin",
    "avatar": "...",
    "createdAt": "2024-01-01T00:00:00"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Using Token

```http
GET /api/projects
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Demo Accounts

| Email                 | Password   | Role      |
| --------------------- | ---------- | --------- |
| admin@example.com     | admin123   | admin     |
| manager@example.com   | manager123 | manager   |
| developer@example.com | dev123     | developer |

---

## 🗄️ Database Schema

### Users

- id, email, password_hash, name, role, avatar, created_at

### Team Members

- id, name, email, role, system_role, avatar, status, workload, skills, active_projects

### Projects

- id, name, description, template, icon, progress, status, due_date, team_member_ids, total_story_points, estimated_duration

### Sprints

- id, project_id, name, goal, start_date, end_date, status, total_tasks, completed_tasks, task_ids

### Tasks (with PERT + RACI)

- id, project_id, sprint_id, name, description, status, priority, type, story_points
- **PERT**: pert_optimistic, pert_most_likely, pert_pessimistic, pert_expected
- **RACI**: raci_responsible[], raci_accountable, raci_consulted[], raci_informed[]

### Project Roles

- id, project_id, member_id, role, permissions (can_edit, can_delete, can_manage_team, can_manage_sprints)

### Experiments

- id, name, description, hypothesis, status, methodology, start_date, end_date, participants, results

---

## 🛠️ Development

### Database Migrations

```bash
# Initialize migrations (first time)
flask db init

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Reset Database

```bash
# Drop and recreate
python create_database.py

# Reseed
python seed_database.py
```

---

## 🔒 Security

- **Password Hashing**: bcrypt
- **JWT Tokens**: Expiry time configurable
- **CORS**: Configured for frontend origins
- **SQL Injection**: Protected via SQLAlchemy ORM
- **Role-Based Access Control**: Admin, Manager, Developer, Viewer

---

## 📦 Tech Stack

- **Flask 3.0** - Web framework
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL** - Database
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - CORS handling
- **Flask-Migrate** - Database migrations
- **bcrypt** - Password hashing

---

## 🐛 Troubleshooting

### Database connection error

- Check PostgreSQL is running
- Verify credentials in `.env`
- Check DATABASE_URL format

### Port already in use

```bash
# Find process on port 5000
netstat -ano | findstr :5000

# Kill process
taskkill /PID <process_id> /F
```

### CORS errors

- Check CORS_ORIGINS in `.env`
- Ensure frontend URL matches exactly

---

## 📝 License

MIT License - Diplomová práca 2024
