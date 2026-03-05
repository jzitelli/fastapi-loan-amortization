const BASE_URL = "http://localhost:8000";

export async function apiLogin(
  email: string,
  password: string
): Promise<{ access_token: string; token_type: string }> {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${BASE_URL}/api/v1/login/access-token`, {
    method: "POST",
    body,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail ?? `Login failed (${res.status})`);
  }
  return res.json();
}

async function authFetch(
  path: string,
  token: string,
  init?: RequestInit
): Promise<Response> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(init?.headers as Record<string, string>),
    },
  });
  return res;
}

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  full_name: string | null;
}

export interface LoanPublic {
  id: number;
  amount: string;
  annual_interest_rate: string;
  loan_term: number;
  owner_id: number;
}

export interface ScheduleRow {
  month: number;
  monthly_payment: string;
  remaining_balance: string;
}

export interface LoanSummary {
  remaining_balance: string;
  aggregate_interest_paid: string;
  aggregate_principal_paid: string;
}

export async function testToken(token: string): Promise<User> {
  const res = await authFetch("/api/v1/login/test-token", token, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Invalid token");
  return res.json();
}

export async function fetchLoans(
  token: string
): Promise<{ data: LoanPublic[]; count: number }> {
  const res = await authFetch("/api/v1/loans/", token);
  if (!res.ok) throw new Error("Failed to fetch loans");
  return res.json();
}

export async function createLoan(
  token: string,
  loan: { amount: number; annual_interest_rate: number; loan_term: number }
): Promise<LoanPublic> {
  const res = await authFetch("/api/v1/loans/", token, {
    method: "POST",
    body: JSON.stringify(loan),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail ?? `Failed to create loan (${res.status})`);
  }
  return res.json();
}

export async function fetchSchedule(
  token: string,
  loanId: number
): Promise<ScheduleRow[]> {
  const res = await authFetch(`/api/v1/loans/${loanId}/schedule`, token);
  if (!res.ok) throw new Error("Failed to fetch schedule");
  return res.json();
}

export async function fetchSummary(
  token: string,
  loanId: number,
  month: number
): Promise<LoanSummary> {
  const res = await authFetch(
    `/api/v1/loans/${loanId}/summary?month=${month}`,
    token
  );
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail ?? `Failed to fetch summary (${res.status})`);
  }
  return res.json();
}

export async function shareLoan(
  token: string,
  loanId: number,
  email: string
): Promise<void> {
  const res = await authFetch(
    `/api/v1/loans/${loanId}/share?email=${encodeURIComponent(email)}`,
    token,
    { method: "PUT" }
  );
  if (!res.ok) throw new Error("Failed to share loan");
}

export async function createUser(
  token: string,
  user: {
    email: string;
    password: string;
    full_name?: string;
    is_superuser?: boolean;
  }
): Promise<User> {
  const res = await authFetch("/api/v1/users/", token, {
    method: "POST",
    body: JSON.stringify(user),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail ?? `Failed to create user (${res.status})`);
  }
  return res.json();
}
