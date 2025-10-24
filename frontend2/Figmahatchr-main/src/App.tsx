import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { PromptPage } from "./components/PromptPage";
import { ProgressPage } from "./components/ProgressPage";
import { LaunchPage } from "./components/LaunchPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PromptPage />} />
        <Route path="/generate" element={<ProgressPage />} />
        <Route path="/launch" element={<LaunchPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
