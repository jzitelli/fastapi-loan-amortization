import { Navigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function ProtectedRoute({
  children,
}: {
  children: React.ReactNode;
}) {
  const { token, loading } = useAuth();
  if (loading) return <p>Loading...</p>;
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
