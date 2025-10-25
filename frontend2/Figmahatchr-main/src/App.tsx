import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { PromptPage } from "./components/PromptPage";
import { ProgressPage } from "./components/ProgressPage";
import { LaunchPage } from "./components/LaunchPage";
import FigmaPreviewPage from "./components/FigmaPreviewPage";
import CofounderFinderPage from "./components/CofounderFinderPage";
import CofounderExplorePage from "./components/CofounderExplorePage";
import CofounderProfilePage from "./components/CofounderProfilePage";
import HeaderNav from "./components/HeaderNav";

export default function App() {
  return (
    <BrowserRouter>
      <HeaderNav />
      <Routes>
        <Route path="/" element={<PromptPage />} />
        <Route path="/generate" element={<ProgressPage />} />
        <Route path="/launch" element={<LaunchPage />} />
        <Route path="/figma" element={<FigmaPreviewPage />} />
        <Route path="/cofounder" element={<CofounderFinderPage />} />
        <Route path="/cofounder/explore" element={<CofounderExplorePage />} />
        <Route path="/cofounder/profile" element={<CofounderProfilePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
