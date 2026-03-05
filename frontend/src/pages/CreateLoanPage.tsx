import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { createLoan } from "../api";

export default function CreateLoanPage() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [amount, setAmount] = useState("200000");
  const [rate, setRate] = useState("6.47");
  const [term, setTerm] = useState("360");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await createLoan(token!, {
        amount: Number(amount),
        annual_interest_rate: Number(rate) / 100,
        loan_term: Number(term),
      });
      navigate("/");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create loan");
    }
  };

  return (
    <div>
      <h1>Create Loan</h1>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Amount ($)
          <input
            type="number"
            step="0.01"
            min="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
          />
        </label>
        <label>
          Annual Interest Rate (%)
          <input
            type="number"
            step="0.01"
            min="0"
            value={rate}
            onChange={(e) => setRate(e.target.value)}
            required
          />
        </label>
        <label>
          Loan Term (months)
          <input
            type="number"
            min="1"
            max="1200"
            value={term}
            onChange={(e) => setTerm(e.target.value)}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit">Create</button>
      </form>
    </div>
  );
}
