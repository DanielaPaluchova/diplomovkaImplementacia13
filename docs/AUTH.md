# 🔐 Authentication System

Kompletný authentication systém pripravený na backend integráciu.

## 📋 Obsah

- [Funkcie](#funkcie)
- [Demo účty](#demo-účty)
- [Stránky](#stránky)
- [API Ready](#api-ready)
- [Použitie](#použitie)
- [Backend Integration](#backend-integration)

---

## ✨ Funkcie

### ✅ Implementované

1. **Login/Logout**
   - Email + password authentication
   - "Remember me" funkcia
   - Session management (localStorage/sessionStorage)
   - Demo účty pre testing

2. **Registration**
   - User registration s validáciou
   - Password strength check
   - Email format validation
   - Terms of Service checkbox

3. **User Profile**
   - Zobrazenie user informácií
   - Úprava profilu
   - Role badge
   - Avatar support
   - Change password (UI ready)

4. **Route Guards**
   - Protected routes (vyžadujú prihlásenie)
   - Redirect na login pre neprihlásených
   - Redirect na homepage pre prihlásených (ak idú na /login)
   - Query parameter `?redirect=` pre return URL

5. **Auth State Management (Pinia)**
   - Centralizovaný auth state
   - JWT token handling
   - User permissions
   - Role hierarchy

6. **User Roles**
   - **Admin** - Plný prístup
   - **Manager** - Project management
   - **Developer** - Development tasks
   - **Viewer** - Read-only access

---

## 👥 Demo Účty

Pre testovanie aplikácie bez backendu:

### Admin

```
Email: admin@example.com
Password: admin123
```

### Manager

```
Email: manager@example.com
Password: manager123
```

### Developer

```
Email: developer@example.com
Password: dev123
```

**Tip:** Na login stránke je "Demo Accounts" expansion panel s quick login buttonmi.

---

## 📄 Stránky

### Login Page (`/login`)

- Email/password formulár
- Remember me checkbox
- Demo accounts quick access
- Link na registráciu
- Validácia input fields
- Loading states

### Register Page (`/register`)

- Full name, email, password
- Password confirmation
- Password strength indicator
- Terms of Service checkbox
- Validácia všetkých polí
- Automatické prihlásenie po registrácii

### Profile Page (`/profile`)

- User informácie (name, email, role, avatar)
- Úprava profilu
- Role badge
- Change password dialog
- Logout button
- Member since date

---

## 🔌 API Ready

Systém je **pripravený na backend integráciu**. Všetky mock funkcie majú komentáre s príkladmi pre real API calls.

### Auth Store (`src/stores/auth-store.ts`)

```typescript
// MOCK (aktuálne)
const mockUsers = [...];
const mockToken = `mock_jwt_${userId}_${timestamp}`;

// READY FOR BACKEND (zakomentované)
/*
const response = await api.post('/auth/login', {
  email: credentials.email,
  password: credentials.password,
});

user.value = response.data.user;
token.value = response.data.token;
*/
```

### API Client (`src/services/api.ts`)

Pripravený axios client s interceptormi:

```typescript
import { api } from 'src/services/api';

// GET request
const users = await api.get('/users');

// POST request
const newProject = await api.post('/projects', { name: 'New Project' });

// PUT request
await api.put('/users/1', { name: 'Updated Name' });

// DELETE request
await api.delete('/projects/1');
```

**Funkcie:**

- ✅ Automatic token injection (Authorization header)
- ✅ 401 Unauthorized handling (redirect to login)
- ✅ 403 Forbidden handling
- ✅ 500 Server Error handling
- ✅ Request/Response interceptors

---

## 📖 Použitie

### 1. Prístup k Auth Store

```typescript
import { useAuthStore } from 'src/stores/auth-store';

const authStore = useAuthStore();

// Check if authenticated
if (authStore.isAuthenticated) {
  console.log('User is logged in');
}

// Get user info
console.log(authStore.userName); // "Admin User"
console.log(authStore.user?.email); // "admin@example.com"
console.log(authStore.user?.role); // "admin"

// Check permissions
if (authStore.isAdmin) {
  // Admin only actions
}

if (authStore.hasRole('manager')) {
  // Manager actions
}

if (authStore.hasPermission('developer')) {
  // Developer or higher (manager, admin)
}
```

### 2. Protected Routes

```typescript
// src/router/routes.ts
{
  path: '/admin',
  component: () => import('pages/AdminPage.vue'),
  meta: { requiresAuth: true }, // <-- Vyžaduje prihlásenie
}
```

### 3. Role-Based Access

```vue
<template>
  <!-- Show only for admins -->
  <q-btn v-if="authStore.isAdmin" label="Admin Panel" />

  <!-- Show for managers and admins -->
  <q-btn v-if="authStore.isManager" label="Manage Projects" />

  <!-- Show for specific role -->
  <q-btn v-if="authStore.hasRole('developer')" label="Development" />

  <!-- Show for role hierarchy (developer or higher) -->
  <q-btn v-if="authStore.hasPermission('developer')" label="Access Dev Tools" />
</template>

<script setup>
import { useAuthStore } from 'src/stores/auth-store';
const authStore = useAuthStore();
</script>
```

### 4. API Composable

```typescript
import { useApi } from 'src/composables/useApi';

const { data, loading, error, execute } = useApi();

// Execute API call with automatic loading & error handling
await execute(() => api.post('/projects', { name: 'New Project' }), {
  successMessage: 'Project created!',
  errorMessage: 'Failed to create project',
});

console.log(data.value); // API response
console.log(loading.value); // false
console.log(error.value); // null or error message
```

---

## 🚀 Backend Integration

Keď budeš mať backend hotový, stačí:

### 1. Update Auth Store

V `src/stores/auth-store.ts`:

```typescript
// Zakomentuj MOCK kód
/*
const mockUsers = [...];
const mockToken = `mock_jwt_${userId}`;
*/

// Odkomentuj REAL API kód
const response = await api.post('/auth/login', {
  email: credentials.email,
  password: credentials.password,
});

user.value = response.data.user;
token.value = response.data.token;
```

### 2. Update Environment

Vytvor `.env` súbor:

```bash
# Development
VITE_API_BASE_URL=http://localhost:5000/api
VITE_WS_BASE_URL=ws://localhost:5000/ws

# Production
VITE_API_BASE_URL=https://api.yourapp.com/api
VITE_WS_BASE_URL=wss://api.yourapp.com/ws
```

### 3. Backend API Endpoints

Potrebuješ tieto endpointy:

```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
POST   /api/auth/refresh
GET    /api/auth/me
PUT    /api/auth/profile
POST   /api/auth/change-password
```

#### **POST /api/auth/login**

Request:

```json
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
    "avatar": "https://...",
    "createdAt": "2024-01-01T00:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### **POST /api/auth/register**

Request:

```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "name": "New User"
}
```

Response: (same as login)

#### **GET /api/auth/me**

Headers:

```
Authorization: Bearer <token>
```

Response:

```json
{
  "id": 1,
  "email": "admin@example.com",
  "name": "Admin User",
  "role": "admin",
  "avatar": "https://...",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

---

## 🎯 Ďalšie kroky (po pridaní backendu)

1. **JWT Token Refresh**
   - Implementuj automatic token refresh
   - Pred expiráciou tokenu zavolaj `/auth/refresh`

2. **Forgot Password**
   - Email reset link
   - Token verification
   - Password reset form

3. **Email Verification**
   - Po registrácii poslať verification email
   - User musí kliknúť na link

4. **Two-Factor Authentication (2FA)**
   - Optional 2FA setup
   - QR code generation
   - Verification code input

5. **Session Timeout**
   - Automatic logout po inaktivite
   - Warning dialog pred timeout

6. **Audit Log**
   - Track user logins
   - Track user actions
   - Display v admin panel

---

## 📊 Súbory

```
src/
├── stores/
│   └── auth-store.ts              # Auth state management
├── pages/
│   └── auth/
│       ├── LoginPage.vue          # Login form
│       ├── RegisterPage.vue       # Registration form
│       └── ProfilePage.vue        # User profile
├── services/
│   └── api.ts                     # API client
├── composables/
│   └── useApi.ts                  # API composable
└── router/
    ├── routes.ts                  # Route definitions
    └── index.ts                   # Route guards
```

---

## 🔒 Security Features

1. **JWT Token Storage**
   - LocalStorage (remember me)
   - SessionStorage (default)

2. **Password Validation**
   - Minimum 6 characters
   - Confirmation required
   - Strength indicator

3. **Route Protection**
   - Navigation guards
   - Automatic redirect
   - Return URL support

4. **Role-Based Access**
   - Hierarchical permissions
   - Admin > Manager > Developer > Viewer

5. **API Security**
   - Automatic token injection
   - 401 Unauthorized handling
   - CORS configuration ready

---

## 🐛 Troubleshooting

### Cannot access route after login

- Check `requiresAuth` meta v routes
- Verify auth store initialization
- Check browser console for errors

### Token not persisting

- Check localStorage/sessionStorage
- Verify "Remember me" checkbox
- Clear browser cache

### Mock users not working

- Check email/password exactly
- Verify auth-store.ts mock data
- Check browser console for errors

---

## ✅ Checklist pre Backend Integration

- [ ] Backend API endpointy sú hotové
- [ ] CORS je nakonfigurovaný
- [ ] JWT token generation funguje
- [ ] Update `VITE_API_BASE_URL` v .env
- [ ] Odkomentuj REAL API kód v auth-store.ts
- [ ] Zakomentuj MOCK kód v auth-store.ts
- [ ] Testuj login/logout flow
- [ ] Testuj registration flow
- [ ] Testuj token refresh
- [ ] Testuj protected routes

---

**Pripravené na production!** 🚀
