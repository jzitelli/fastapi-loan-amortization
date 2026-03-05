import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth";
import { fetchLoans, type LoanPublic } from "../api";

export default function LoansPage() {
  const { token } = useAuth();
  const [loans, setLoans] = useState<LoanPublic[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    fetchLoans(token).then((r) => setLoans(r.data)).catch((e) => setError(e.message));
  }, [token]);

  return (
    <div>
      <h1>Your Loans</h1>
      {error && <p className="error">{error}</p>}
      {loans.length === 0 ? (
        <p>
          No loans yet. <Link to="/loans/new">Create one</Link>
        </p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Amount</th>
              <th>Rate</th>
              <th>Term (months)</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {loans.map((loan) => (
              <tr key={loan.id}>
                <td>{loan.id}</td>
                <td>${Number(loan.amount).toLocaleString()}</td>
                <td>{(Number(loan.annual_interest_rate) * 100).toFixed(2)}%</td>
                <td>{loan.loan_term}</td>
                <td>
                  <Link to={`/loans/${loan.id}`}>View</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
