# Authentication API Endpoints Reference

**Version:** 1.0  
**Base URL:** `/api/auth/`  
**Last Updated:** 2026-01-25

This document provides a complete reference of all API endpoints used by the frontend application for backend developers to implement.

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [Token Management](#2-token-management)
3. [User Profile](#3-user-profile)
4. [Password Management](#4-password-management)
5. [Verification](#5-verification)
6. [Security Questions](#6-security-questions)
7. [System](#7-system)
8. [Response Format](#8-response-format)
9. [Error Codes](#9-error-codes)
10. [Rate Limiting](#10-rate-limiting)

---

## 1. Authentication

### 1.1 POST `/api/auth/login/`

**Description:** User login - authenticates user and issues JWT tokens

**Auth Required:** No  
**Rate Limit:** 5 requests/minute per IP

**Request:**
```json
{
  "identifier": "string",  // Email OR phone number
  "password": "string"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Connexion réussie",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "phone": "+224620123456",
      "first_name": "Mamadou",
      "last_name": "Diallo",
      "full_name": "Mamadou Diallo",
      "is_verified": true,
      "verified_at": "2024-01-15T10:30:00Z",
      "security": {
        "score": 75,
        "level": "high",
        "has_security_questions": true,
        "has_backup_phone": true
      },
      "profiles": {
        "has_student": true,
        "has_teacher": false,
        "has_school_admin": false
      }
    },
    "tokens": {
      "access": "eyJ...",
      "refresh": "eyJ..."
    },
    "requires_verification": false
  }
}
```

**Success Response - Requires Verification (200):**
```json
{
  "success": true,
  "message": "Vérification requise",
  "data": {
    "user": { "..." },
    "tokens": { "access": "...", "refresh": "..." },
    "requires_verification": true,
    "verification_options": ["email", "phone"]
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "message": "Identifiants incorrects",
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "details": null
  }
}
```

**Error Response - Account Locked (423):**
```json
{
  "success": false,
  "message": "Compte temporairement verrouillé",
  "error": {
    "code": "AUTH_ACCOUNT_LOCKED",
    "details": {
      "locked_until": "2024-01-15T11:00:00Z",
      "remaining_minutes": 25
    }
  }
}
```

---

### 1.2 POST `/api/auth/register/`

**Description:** Register a new user account

**Auth Required:** No  
**Rate Limit:** 5 requests/hour per IP

**Request:**
```json
{
  "email": "string | null",       // Required if phone not provided
  "phone": "string | null",       // Required if email not provided (format: +224620123456)
  "password": "string",           // Min 8 chars, 1 uppercase, 1 lowercase, 1 digit
  "password_confirm": "string",   // Must match password
  "first_name": "string",         // 2-50 characters
  "last_name": "string"           // 2-50 characters
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Compte créé avec succès",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "phone": "+224620123456",
      "first_name": "Mamadou",
      "last_name": "Diallo",
      "full_name": "Mamadou Diallo",
      "is_verified": false,
      "security": {
        "score": 25,
        "level": "low"
      }
    },
    "tokens": {
      "access": "eyJ...",
      "refresh": "eyJ..."
    },
    "requires_verification": true,
    "verification_sent_to": "email"  // or "phone" or null
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Erreur de validation",
  "error": {
    "code": "VALIDATION_ERROR",
    "details": {
      "email": ["Cet email est déjà utilisé"],
      "password": ["Le mot de passe doit contenir au moins 8 caractères"]
    }
  }
}
```

---

### 1.3 POST `/api/auth/logout/`

**Description:** Logout user and blacklist the refresh token

**Auth Required:** Yes

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh": "string"  // Refresh token to blacklist
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Déconnexion réussie",
  "data": null
}
```

---

## 2. Token Management

### 2.1 POST `/api/auth/refresh/`

**Description:** Refresh the access token using refresh token (with token rotation)

**Auth Required:** No

**Request:**
```json
{
  "refresh": "string"  // Current refresh token
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Token rafraîchi",
  "data": {
    "access": "eyJ...",
    "refresh": "eyJ..."  // New refresh token (rotation)
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "message": "Token invalide ou expiré",
  "error": {
    "code": "AUTH_TOKEN_INVALID",
    "details": null
  }
}
```

**Implementation Notes:**
- Token rotation is enabled - each refresh invalidates the old refresh token
- 30-second grace period to handle race conditions (multiple tabs)
- If old token used after grace period → return `AUTH_TOKEN_REUSE_DETECTED` error

---

## 3. User Profile

### 3.1 GET `/api/auth/me/`

**Description:** Get current authenticated user's profile

**Auth Required:** Yes

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "success": true,
  "message": null,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "email_masked": "u***@example.com",
    "phone": "+224620123456",
    "phone_masked": "+224 6XX-XXX-456",
    "first_name": "Mamadou",
    "last_name": "Diallo",
    "full_name": "Mamadou Diallo",
    "backup_phone": "+224621000000",
    "backup_phone_owner": "Papa",
    
    "verification": {
      "is_verified": true,
      "email_verified": true,
      "email_verified_at": "2024-01-15T10:30:00Z",
      "phone_verified": false,
      "phone_verified_at": null
    },
    
    "security": {
      "score": 65,
      "level": "medium",
      "has_security_questions": true,
      "security_questions_count": 2,
      "has_backup_phone": true,
      "suggestions": [
        "Vérifiez votre numéro de téléphone",
        "Ajoutez une 3ème question de sécurité"
      ]
    },
    
    "profiles": {
      "has_student": true,
      "has_teacher": false,
      "has_school_admin": false
    },
    
    "date_joined": "2024-01-10T08:00:00Z",
    "last_login": "2024-01-20T14:30:00Z"
  }
}
```

---

### 3.2 PATCH `/api/auth/me/`

**Description:** Update current user's profile

**Auth Required:** Yes

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:** (all fields optional)
```json
{
  "first_name": "string",
  "last_name": "string",
  "backup_phone": "string",
  "backup_phone_owner": "string"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Profil mis à jour",
  "data": { /* Same structure as GET /me/ */ }
}
```

---

### 3.3 POST `/api/auth/me/email/`

**Description:** Add or change user's email address

**Auth Required:** Yes

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": "string",
  "current_password": "string"  // Required for security
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Email modifié. Vérification requise.",
  "data": {
    "email": "new@example.com",
    "email_verified": false,
    "verification_sent": true
  }
}
```

---

### 3.4 POST `/api/auth/me/phone/`

**Description:** Add or change user's phone number

**Auth Required:** Yes

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "phone": "string",
  "current_password": "string"  // Required for security
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Téléphone modifié. Vérification requise.",
  "data": {
    "phone": "+224620999999",
    "phone_verified": false,
    "verification_sent": true
  }
}
```

---

## 4. Password Management

### 4.1 POST `/api/auth/password/change/`

**Description:** Change password for authenticated user

**Auth Required:** Yes

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string",
  "new_password_confirm": "string"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Mot de passe modifié",
  "data": {
    "tokens": {
      "access": "eyJ...",
      "refresh": "eyJ..."
    }
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Mot de passe actuel incorrect",
  "error": {
    "code": "PASSWORD_INVALID_CURRENT",
    "details": null
  }
}
```

---

### 4.2 POST `/api/auth/password/reset/`

**Description:** Request password reset (send code via email/SMS)

**Auth Required:** No  
**Rate Limit:** 3 requests/hour per IP

**Request Body:**
```json
{
  "identifier": "string"  // Email OR phone number
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Si un compte existe avec cet identifiant, vous recevrez un code",
  "data": {
    "expires_in": 600,
    "next_step": "check_email_or_phone"
  }
}
```

**Note:** Always returns success to prevent user enumeration attacks

---

### 4.3 POST `/api/auth/password/reset/confirm/`

**Description:** Confirm password reset with verification code

**Auth Required:** No

**Request Body:**
```json
{
  "identifier": "string",
  "code": "string",
  "new_password": "string",
  "new_password_confirm": "string"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Mot de passe modifié avec succès",
  "data": {
    "can_login": true
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Code invalide ou expiré",
  "error": {
    "code": "PASSWORD_RESET_INVALID",
    "details": null
  }
}
```

---

## 5. Verification

### 5.1 GET `/api/auth/verify/status/`

**Description:** Get account verification status

**Auth Required:** Yes

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "success": true,
  "message": null,
  "data": {
    "is_verified": true,
    "email": {
      "exists": true,
      "value_masked": "u***@example.com",
      "verified": true,
      "verified_at": "2024-01-15T10:30:00Z"
    },
    "phone": {
      "exists": true,
      "value_masked": "+224 6XX-XXX-456",
      "verified": false,
      "verified_at": null
    }
  }
}
```

---

### 5.2 POST `/api/auth/verify/send/`

**Description:** Send a verification code

**Auth Required:** Yes  
**Rate Limit:** 3 requests/minute, 5 requests/day

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "type": "email | phone"  // Which contact to verify
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Code envoyé",
  "data": {
    "sent_to": "user@example.com",
    "masked": "u***@example.com",
    "expires_in": 600,
    "can_resend_in": 60,
    "dev_code": "123456"  // DEV ONLY - if SMS_SHOW_CODE_IN_RESPONSE=True
  }
}
```

**Error Response - No Contact (400):**
```json
{
  "success": false,
  "message": "Aucun email configuré",
  "error": {
    "code": "VERIFY_NO_CONTACT",
    "details": null
  }
}
```

**Error Response - Rate Limited (429):**
```json
{
  "success": false,
  "message": "Veuillez attendre avant de renvoyer",
  "error": {
    "code": "VERIFY_COOLDOWN",
    "details": {
      "retry_after": 45
    }
  }
}
```

---

### 5.3 POST `/api/auth/verify/confirm/`

**Description:** Confirm verification with code

**Auth Required:** Yes

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "type": "email | phone",
  "code": "string"  // 6-digit code
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Vérification réussie",
  "data": {
    "type": "email",
    "verified_at": "2024-01-15T10:30:00Z",
    "is_fully_verified": true,
    "security": {
      "score": 50,
      "level": "medium"
    }
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Code incorrect",
  "error": {
    "code": "VERIFY_CODE_INVALID",
    "details": {
      "attempts_remaining": 2
    }
  }
}
```

---

## 6. Security Questions

### 6.1 GET `/api/auth/security-questions/`

**Description:** Get list of predefined security questions

**Auth Required:** No

**Success Response (200):**
```json
{
  "success": true,
  "message": null,
  "data": {
    "predefined_questions": [
      "Quel est le nom de votre école primaire ?",
      "Quel est le nom de votre professeur préféré ?",
      "Dans quelle ville avez-vous passé le CEE ?",
      "Quel est le prénom de votre mère ?"
    ],
    "min_required": 2,
    "max_allowed": 3,
    "allow_custom": true
  }
}
```

---

### 6.2 GET `/api/auth/security-questions/mine/`

**Description:** Get user's configured security questions (without answers)

**Auth Required:** Yes

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "success": true,
  "message": null,
  "data": {
    "configured_count": 2,
    "questions": [
      {
        "order": 1,
        "question": "Quel est le nom de votre école primaire ?"
      },
      {
        "order": 2,
        "question": "Quel est le prénom de votre mère ?"
      }
    ]
  }
}
```

---

### 6.3 POST `/api/auth/security-questions/setup/`

**Description:** Configure user's security questions

**Auth Required:** Yes

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "questions": [
    {
      "question": "string",
      "answer": "string"
    },
    {
      "question": "string",
      "answer": "string"
    },
    {
      "question": "string",  // Optional 3rd question
      "answer": "string"
    }
  ]
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Questions de sécurité configurées",
  "data": {
    "configured_count": 3,
    "security": {
      "score": 85,
      "level": "high"
    }
  }
}
```

---

### 6.4 POST `/api/auth/security-questions/verify/`

**Description:** Verify security question answers (for account recovery)

**Auth Required:** No

**Request Body:**
```json
{
  "identifier": "string",  // Email or phone
  "answers": [
    {
      "order": 1,
      "answer": "string"
    },
    {
      "order": 2,
      "answer": "string"
    }
  ]
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Vérification réussie",
  "data": {
    "reset_token": "temporary-token-for-password-reset",
    "expires_in": 600
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Réponses incorrectes",
  "error": {
    "code": "SECURITY_ANSWERS_INVALID",
    "details": {
      "attempts_remaining": 2
    }
  }
}
```

---

## 7. System

### 7.1 GET `/api/health/`

**Description:** Health check endpoint for monitoring

**Auth Required:** No

**Success Response (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-25T15:26:27Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "email": "available"
  }
}
```

**Error Response (503):**
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "timestamp": "2026-01-25T15:26:27Z",
  "services": {
    "database": "disconnected",
    "redis": "connected",
    "email": "unavailable"
  }
}
```

---

## 8. Response Format

All endpoints follow a consistent response format:

### Success Response
```json
{
  "success": true,
  "message": "string | null",
  "data": { /* endpoint-specific data */ }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Human-readable error message",
  "error": {
    "code": "ERROR_CODE",
    "details": { /* additional error info */ } | null
  }
}
```

---

## 9. Error Codes

| Code | HTTP Status | Description | Frontend Action |
|------|-------------|-------------|-----------------|
| `AUTH_INVALID_CREDENTIALS` | 401 | Wrong email/password | Show error message |
| `AUTH_TOKEN_INVALID` | 401 | JWT invalid/expired | Try refresh, then logout |
| `AUTH_TOKEN_REUSE_DETECTED` | 401 | Security violation | Force logout immediately |
| `AUTH_ACCOUNT_LOCKED` | 423 | Too many failed attempts | Show lockout message with timer |
| `AUTH_ACCOUNT_INACTIVE` | 403 | Account disabled | Show contact admin message |
| `VALIDATION_ERROR` | 400 | Input validation failed | Show field-specific errors |
| `PASSWORD_INVALID_CURRENT` | 400 | Current password wrong | Show error on current password field |
| `PASSWORD_RESET_INVALID` | 400 | Reset code invalid/expired | Show error, offer resend |
| `VERIFY_NO_CONTACT` | 400 | No email/phone configured | Prompt to add contact |
| `VERIFY_COOLDOWN` | 429 | Resend too soon | Show countdown timer |
| `VERIFY_CODE_INVALID` | 400 | Wrong verification code | Show attempts remaining |
| `SECURITY_ANSWERS_INVALID` | 400 | Wrong security answers | Show attempts remaining |
| `SERVER_ERROR` | 500 | Internal server error | Show generic error |

---

## 10. Rate Limiting

| Endpoint | Limit | Scope |
|----------|-------|-------|
| `POST /api/auth/login/` | 5/minute | Per IP |
| `POST /api/auth/register/` | 5/hour | Per IP |
| `POST /api/auth/password/reset/` | 3/hour | Per IP |
| `POST /api/auth/password/reset/confirm/` | 5/hour | Per token |
| `POST /api/auth/password/change/` | 5/hour | Per user |
| `POST /api/auth/verify/send/` | 3/minute, 5/day | Per user |
| `POST /api/auth/refresh/` | 30/15min | Per user |
| `POST /api/auth/logout/` | 10/15min | Per user |

### Account Lockout
- After 10 failed login attempts: Lock account for **30 minutes**
- Send email notification to user
- Admin portal can unlock accounts early

---

## Endpoint Summary Table

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/login/` | No | User login |
| POST | `/api/auth/register/` | No | User registration |
| POST | `/api/auth/logout/` | Yes | User logout |
| POST | `/api/auth/refresh/` | No | Refresh access token |
| GET | `/api/auth/me/` | Yes | Get user profile |
| PATCH | `/api/auth/me/` | Yes | Update user profile |
| POST | `/api/auth/me/email/` | Yes | Change email |
| POST | `/api/auth/me/phone/` | Yes | Change phone |
| POST | `/api/auth/password/change/` | Yes | Change password |
| POST | `/api/auth/password/reset/` | No | Request password reset |
| POST | `/api/auth/password/reset/confirm/` | No | Confirm password reset |
| GET | `/api/auth/verify/status/` | Yes | Get verification status |
| POST | `/api/auth/verify/send/` | Yes | Send verification code |
| POST | `/api/auth/verify/confirm/` | Yes | Confirm verification |
| GET | `/api/auth/security-questions/` | No | Get predefined questions |
| GET | `/api/auth/security-questions/mine/` | Yes | Get user's questions |
| POST | `/api/auth/security-questions/setup/` | Yes | Setup security questions |
| POST | `/api/auth/security-questions/verify/` | No | Verify answers for recovery |
| GET | `/api/health/` | No | Health check |

---

## Token Configuration

| Token Type | Lifetime | Notes |
|------------|----------|-------|
| Access Token | 15 minutes | Short-lived, stored in memory |
| Refresh Token (Student/Teacher) | 14 days | HTTP-only cookie |
| Refresh Token (Parent) | 7 days | Less frequent access |
| Refresh Token (Admin) | 24 hours | Higher security |
| Password Reset Code | 10 minutes | Sent via email/SMS |
| Verification Code | 10 minutes | 6-digit code |
| Security Question Reset Token | 10 minutes | After successful verification |

---

## CORS Configuration

**Allowed Origins (Production):**
```
https://app.school.edu
https://www.school.edu
```

**Required Headers:**
```
Access-Control-Allow-Credentials: true
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Allow-Methods: GET, POST, PATCH, DELETE, OPTIONS
```

---

## Notes for Backend Implementation

1. **Password Requirements:**
   - Minimum 8 characters
   - At least 1 uppercase letter
   - At least 1 lowercase letter
   - At least 1 digit

2. **Phone Format:**
   - International format: `+224620123456`
   - Validate country code

3. **Security Score Calculation:**
   - Base: 25 points
   - Email verified: +25 points
   - Phone verified: +25 points
   - Security questions (2): +15 points
   - Security questions (3): +25 points
   - Backup phone: +10 points

4. **Security Levels:**
   - `low`: 0-40 points
   - `medium`: 41-70 points
   - `high`: 71-100 points

5. **Token Rotation:**
   - Enable 30-second grace period for handling concurrent requests from multiple tabs
   - If old refresh token used after grace period, invalidate all user sessions
