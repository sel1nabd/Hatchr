import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { PromptPage } from "./components/PromptPage";
import { ProgressPage } from "./components/ProgressPage";
import { LaunchPage } from "./components/LaunchPage";
import CofounderFinderPage from "./components/CofounderFinderPage";
import CofounderProfilePage from "./components/CofounderProfilePage";
import HeaderNav from "./components/HeaderNav";
import ScrollToTop from "./components/ScrollToTop";
import NotFoundPage from "./components/NotFoundPage";

export default function App() {
  return (
    <BrowserRouter>
      <HeaderNav />
      <ScrollToTop />
      <div className="pt-16">
        <Routes>
          <Route path="/" element={<PromptPage />} />
          <Route path="/generate" element={<ProgressPage />} />
          <Route path="/launch" element={<LaunchPage />} />
          <Route path="/cofounder" element={<CofounderFinderPage />} />
          <Route path="/cofounder/profile" element={<CofounderProfilePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
