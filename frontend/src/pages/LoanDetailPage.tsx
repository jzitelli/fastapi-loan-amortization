import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useAuth } from "../auth";
import {
  fetchSchedule,
  fetchSummary,
  shareLoan,
  type ScheduleRow,
  type LoanSummary,
} from "../api";

export default function LoanDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const loanId = Number(id);

  const [schedule, setSchedule] = useState<ScheduleRow[]>([]);
  const [error, setError] = useState("");

  const [summaryMonth, setSummaryMonth] = useState("");
  const [summary, setSummary] = useState<LoanSummary | null>(null);
  const [summaryError, setSummaryError] = useState("");

  const [shareEmail, setShareEmail] = useState("");
  const [shareMsg, setShareMsg] = useState("");

  useEffect(() => {
    if (!token) return;
    fetchSchedule(token, loanId)
      .then(setSchedule)
      .catch((e) => setError(e.message));
  }, [token, loanId]);

  const handleSummary = async (e: React.FormEvent) => {
    e.preventDefault();
    setSummaryError("");
    setSummary(null);
    try {
      const s = await fetchSummary(token!, loanId, Number(summaryMonth));
      setSummary(s);
    } catch (err: unknown) {
      setSummaryError(
        err instanceof Error ? err.message : "Failed to fetch summary"
      );
    }
  };

  const handleShare = async (e: React.FormEvent) => {
    e.preventDefault();
    setShareMsg("");
    try {
      await shareLoan(token!, loanId, shareEmail);
      setShareMsg(`Shared with ${shareEmail}`);
      setShareEmail("");
    } catch (err: unknown) {
      setShareMsg(
        err instanceof Error ? err.message : "Failed to share"
      );
    }
  };

  return (
    <div>
      <h1>Loan #{loanId}</h1>

      <section>
        <h2>Month Summary</h2>
        <form onSubmit={handleSummary} className="form-inline">
          <label>
            Month
            <input
              type="number"
              min="1"
              value={summaryMonth}
              onChange={(e) => setSummaryMonth(e.target.value)}
              required
            />
          </label>
          <button type="submit">Get Summary</button>
        </form>
        {summaryError && <p className="error">{summaryError}</p>}
        {summary && (
          <table>
            <thead>
              <tr>
                <th>Remaining Balance</th>
                <th>Aggregate Interest Paid</th>
                <th>Aggregate Principal Paid</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>${Number(summary.remaining_balance).toLocaleString()}</td>
                <td>
                  ${Number(summary.aggregate_interest_paid).toLocaleString()}
                </td>
                <td>
                  ${Number(summary.aggregate_principal_paid).toLocaleString()}
                </td>
              </tr>
            </tbody>
          </table>
        )}
      </section>

      <section>
        <h2>Share Loan</h2>
        <form onSubmit={handleShare} className="form-inline">
          <label>
            User email
            <input
              type="text"
              value={shareEmail}
              onChange={(e) => setShareEmail(e.target.value)}
              required
            />
          </label>
          <button type="submit">Share</button>
        </form>
        {shareMsg && <p>{shareMsg}</p>}
      </section>

      <section>
        <h2>Amortization Schedule</h2>
        {error && <p className="error">{error}</p>}
        {schedule.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Month</th>
                <th>Monthly Payment</th>
                <th>Remaining Balance</th>
              </tr>
            </thead>
            <tbody>
              {schedule.map((row) => (
                <tr key={row.month}>
                  <td>{row.month}</td>
                  <td>${Number(row.monthly_payment).toLocaleString()}</td>
                  <td>${Number(row.remaining_balance).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
