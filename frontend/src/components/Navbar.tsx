import { Link } from "react-router-dom";
import { useAuth } from "../auth";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="nav-links">
        <Link to="/">Loans</Link>
        <Link to="/loans/new">New Loan</Link>
        {user?.is_superuser && <Link to="/users">Users</Link>}
      </div>
      <div className="nav-right">
        <span>{user?.email}</span>
        <button onClick={logout}>Logout</button>
      </div>
    </nav>
  );
}
