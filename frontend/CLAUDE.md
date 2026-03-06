# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
npm install

# Run dev server (http://localhost:5173)
npm run dev

# Type-check and build for production
npm run build

# Lint
npm run lint

# Preview production build
npm run preview
```

## Architecture

React SPA (Vite + TypeScript) that consumes the FastAPI backend at `http://localhost:8000`. No component library — plain HTML elements with custom CSS in `src/App.css`.

### Key modules

- **`src/api.ts`** — All backend API calls. Exports typed functions (`fetchLoans`, `createLoan`, `fetchSchedule`, `fetchSummary`, `shareLoan`, `createUser`, `apiLogin`, `testToken`) and shared TypeScript interfaces (`User`, `LoanPublic`, `ScheduleRow`, `LoanSummary`). Uses a `BASE_URL` constant and an internal `authFetch` helper that attaches the Bearer token.
- **`src/auth.ts`** — `AuthProvider` context and `useAuth` hook. Manages JWT token in `localStorage`, validates on mount via `testToken`, exposes `token`, `user`, `loading`, `login`, `logout`.
- **`src/components/ProtectedRoute.tsx`** — Redirects unauthenticated users to `/login`.
- **`src/components/Navbar.tsx`** — Nav bar; conditionally shows "Users" link for superusers.
- **`src/App.tsx`** — Router setup with `react-router-dom`. All authenticated routes wrapped in `ProtectedRoute` + `Layout`.

### Pages

- **`LoginPage`** — `/login` — email/password form
- **`LoansPage`** — `/` — lists user's loans in a table
- **`CreateLoanPage`** — `/loans/new` — form to create a loan (rate entered as %, converted to decimal before API call)
- **`LoanDetailPage`** — `/loans/:id` — amortization schedule table, month summary lookup, share-with-user form
- **`UsersPage`** — `/users` — create user form (superuser only, guarded in Navbar)

### Patterns

- Auth token is threaded through API calls explicitly (not via interceptors). Every API function takes `token` as its first argument.
- No state management library — local `useState`/`useEffect` per page, auth state in context.
- The backend must be running with CORS enabled (configured in `app/main.py`) for the frontend to work. Default superuser credentials: `admin@example.com` / `ok`.
