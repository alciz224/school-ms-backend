---
name: frontend-contract-sync
description: Ensures that backend API requests and responses strictly adhere to the data formats expected by the frontend. The frontend development is ahead of the backend, so its types act as the source of truth for all API contracts.
---

# Frontend Contract Synchronization

The frontend development is ahead of the backend. Therefore, the frontend's TypeScript interfaces are the **absolute source of truth** for all API data structures, including request payloads and response formats.

## When to Use

- Creating new Django models, views, or serializers.
- Modifying existing backend API endpoints.
- Debugging serialization or data format errors between frontend and backend.
- Writing tests for backend API responses.

## Core Mandates

1. **Frontend as Source of Truth**: Before creating or modifying any backend API endpoint, you MUST inspect the corresponding frontend types.
2. **Path to Frontend**: The frontend repository is located at:
   `C:\Users\Daniela\Desktop\School Management System\frontent\my-tanstack-app\my-tanstack-app`
3. **Locating Types**: Frontend types are typically located in the data layer:
   `src/server/data/{domain}/types.ts`
4. **Exact Match**: The JSON payload produced by the backend MUST exactly match the structure, naming conventions (e.g., camelCase vs snake_case), and data types (e.g., strings vs integers for IDs, ISO 8601 for dates) defined in the frontend interfaces.
5. **No Guessing**: Do not assume the shape of the data based on backend models. Always read the frontend `types.ts` file for the specific domain you are working on.

## Workflow

1. Identify the domain you are working on in the backend (e.g., `users`, `academics`, `portal`).
2. Read the frontend types for that domain (e.g., `C:\Users\Daniela\Desktop\School Management System\frontent\my-tanstack-app\my-tanstack-app\src\server\data\{domain}\types.ts`).
3. Note the exact field names, nested structures, and data types expected by the frontend.
4. Implement the backend Django REST Framework serializers to produce exactly that JSON format.
   - If the frontend expects `camelCase` and the backend uses `snake_case`, ensure proper conversion is configured (e.g., using `djangorestframework-camel-case` or explicit serializer field names like `firstName = serializers.CharField(source='first_name')`).
5. Verify your backend responses against the frontend interfaces.
