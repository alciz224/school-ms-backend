# TanStack Start Implementation Guide

> **Companion to FRONTEND_PLAN.md** - Technical implementation patterns for the Academic Management System

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Authentication Implementation](#2-authentication-implementation)
3. [API Client Setup](#3-api-client-setup)
4. [TanStack Query Patterns](#4-tanstack-query-patterns)
5. [File-Based Routing Structure](#5-file-based-routing-structure)
6. [Form Handling](#6-form-handling)
7. [Common Patterns](#7-common-patterns)

---

## 1. Architecture Overview

### 1.1 Tech Stack

- **Framework:** TanStack Start (React-based full-stack framework)
- **Backend API:** Django REST at `http://localhost:8000`
- **Router:** TanStack Router (file-based routing)
- **State Management:** TanStack Query (server state)
- **Forms:** TanStack Form (recommended)
- **Styling:** Your choice (Tailwind CSS recommended)

### 1.2 Key Concepts

**TanStack Start vs Next.js:**
- No Vinxi needed - TanStack Start handles server/client split automatically
- Server functions run on the server, client components on the browser
- Cookies are automatically forwarded between client → server function → Django backend

**Session + CSRF Flow:**
```
Client Component → Server Function → Django API
     ↓                    ↓               ↓
  (UI only)    (forwards cookies)  (validates session)
```

---

## 2. Authentication Implementation

### 2.1 Current Working Setup

✅ **What's Already Working:**
- Django backend configured for session cookies + CSRF
- CORS enabled for `http://localhost:3000`
- Session cookies are HTTP-only (secure)
- CSRF token readable by JavaScript for headers

### 2.2 Server Function: API Client

Create a shared API client that handles cookie forwarding and CSRF tokens:

```typescript
// app/lib/api-client.ts
import { getCookie } from 'vinxi/http';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<{ data: T; success: boolean; message?: string }> {
  const isServer = typeof window === 'undefined';
  
  if (!isServer) {
    throw new Error('apiClient must be called from server functions only');
  }

  // Get cookies from the incoming request (TanStack Start provides these)
  const sessionId = getCookie('sessionid');
  const csrfToken = getCookie('csrftoken');

  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');

  // Forward session cookie
  if (sessionId) {
    headers.append('Cookie', `sessionid=${sessionId}`);
  }

  // Add CSRF token for mutations
  if (csrfToken && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(options.method || 'GET')) {
    headers.set('X-CSRFToken', csrfToken);
    headers.append('Cookie', `csrftoken=${csrfToken}`);
  }

  const response = await fetch(`${BACKEND_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include', // Important for cookies
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || 'API request failed');
  }

  return data;
}
```

### 2.3 Authentication Server Functions

```typescript
// app/lib/auth.server.ts
import { apiClient } from './api-client';
import { setCookie } from 'vinxi/http';

export interface User {
  id: string;
  email: string;
  phone: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_verified: boolean;
  is_active: boolean;
  security: {
    score: number;
    level: 'low' | 'medium' | 'high';
  };
}

interface LoginResponse {
  user: User;
  csrf_token: string;
  requires_verification: boolean;
}

// Get CSRF token (call this before any mutations)
export async function getCsrfToken() {
  const response = await apiClient<{ csrf_token: string }>('/api/v2/auth/csrf/', {
    method: 'GET',
  });
  return response.data.csrf_token;
}

// Login
export async function login(identifier: string, password: string) {
  // Get CSRF first
  await getCsrfToken();

  const response = await apiClient<LoginResponse>('/api/v2/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ identifier, password }),
  });

  // Note: Django sets cookies automatically via Set-Cookie headers
  // TanStack Start will forward these to the client
  return response;
}

// Logout
export async function logout() {
  const response = await apiClient('/api/v2/auth/logout/', {
    method: 'POST',
  });
  return response;
}

// Check session status (for route guards)
export async function getSessionStatus() {
  try {
    const response = await apiClient<{ user: User; authenticated: boolean }>(
      '/api/v2/auth/status/',
      { method: 'GET' }
    );
    return response.data;
  } catch (error) {
    return null; // Not authenticated
  }
}

// Register
export async function register(data: {
  email?: string;
  phone?: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
}) {
  await getCsrfToken();

  const response = await apiClient<LoginResponse>('/api/v2/auth/register/', {
    method: 'POST',
    body: JSON.stringify(data),
  });

  return response;
}
```

Tool call argument 'initial_content' pruned from message history.
Tool call argument 'initial_content' pruned from message history.
Tool call argument 'initial_content' pruned from message history.
Tool call argument 'initial_content' pruned from message history.
Tool call argument 'initial_content' pruned from message history.
