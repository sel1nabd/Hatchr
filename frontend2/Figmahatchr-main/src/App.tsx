import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { PromptPage } from "./components/PromptPage";
import { ProgressPage } from "./components/ProgressPage";
import { LaunchPage } from "./components/LaunchPage";
import CofounderFinderPage from "./components/CofounderFinderPage";
import { SignupPage } from "./components/SignupPage";
import HeaderNav from "./components/HeaderNav";
import ScrollToTop from "./components/ScrollToTop";
import NotFoundPage from "./components/NotFoundPage";
import { apiService } from "./services/api";

// Protected route wrapper - redirects to signup if not authenticated
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const [isChecking, setIsChecking] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      const user = await apiService.getCurrentUser();
      setIsAuthenticated(!!user);
      setIsChecking(false);

      if (!user) {
        navigate("/signup");
      }
    };

    checkAuth();
  }, [navigate]);

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? <>{children}</> : null;
}

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Routes>
        {/* Public route - signup/login with Concordium wallet */}
        <Route path="/signup" element={<SignupPage />} />

        {/* Protected routes - require Concordium wallet authentication */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HeaderNav />
              <div className="pt-16">
                <PromptPage />
              </div>
            </ProtectedRoute>
          }
        />
        <Route
          path="/generate"
          element={
            <ProtectedRoute>
              <HeaderNav />
              <div className="pt-16">
                <ProgressPage />
              </div>
            </ProtectedRoute>
          }
        />
        <Route
          path="/launch"
          element={
            <ProtectedRoute>
              <HeaderNav />
              <div className="pt-16">
                <LaunchPage />
              </div>
            </ProtectedRoute>
          }
        />
        <Route
          path="/cofounder"
          element={
            <ProtectedRoute>
              <HeaderNav />
              <div className="pt-16">
                <CofounderFinderPage />
              </div>
            </ProtectedRoute>
          }
        />

        {/* 404 Page */}
        <Route
          path="/404"
          element={
            <>
              <HeaderNav />
              <div className="pt-16">
                <NotFoundPage />
              </div>
            </>
          }
        />

        {/* Redirect all other routes to signup if not authenticated */}
        <Route path="*" element={<Navigate to="/signup" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
