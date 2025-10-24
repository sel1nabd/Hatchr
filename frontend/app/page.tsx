"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [verified, setVerified] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setError(null);

    try {
      const response = await api.generateStartup({ prompt, verified });

      // Store job_id in localStorage and navigate
      localStorage.setItem("currentJobId", response.job_id);
      router.push(`/generate?jobId=${response.job_id}`);
    } catch (err) {
      console.error("Failed to start generation:", err);
      setError("Failed to start generation. Please try again.");
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="space-y-8">
        {/* Main prompt section */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-8">
          <h2 className="text-lg font-semibold mb-4">
            What do you want to build?
          </h2>

          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your startup idea..."
            className="w-full h-40 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent resize-none"
            disabled={isGenerating}
          />

          <p className="text-sm text-gray-500 mt-2">
            e.g., "Airbnb for pets" or "AI scheduling tool for freelancers"
          </p>

          <p>
            Guiding questions you should answer in the prompt:
          </p>
          <ul>
            <li>
              What problem does your startup solve, and why does it matter right now?
            </li>
            <li>  How does your solution work in the simplest terms what makes it different or better?
            </li>
            <li>
              Who are your target users or customers, and what transformation do they experience?
            </li>
            <li>        What’s the vision—where do you see this startup in the next year or five years?
            </li>
            <li>
              If viewers remember one thing about your startup after watching, what should it be?
            </li>
          </ul>

        </div>

        {/* Verification toggle */}
        <div className="mt-6 flex items-center">
          <input
            type="checkbox"
            id="verified"
            checked={verified}
            onChange={(e) => setVerified(e.target.checked)}
            className="w-4 h-4 text-gray-900 border-gray-300 rounded focus:ring-gray-400"
            disabled={isGenerating}
          />
          <label htmlFor="verified" className="ml-2 text-sm text-gray-700">
            Mark as verified founder{" "}
            <span className="text-gray-500">(uses Concordium)</span>
          </label>
        </div>

        {/* Error message */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Generate button */}
        <button
          onClick={handleGenerate}
          disabled={!prompt.trim() || isGenerating}
          className="w-full mt-6 px-6 py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isGenerating ? "Generating..." : "Generate Startup"}
        </button>

        {/* Info cards */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="text-2xl font-bold text-gray-900">1</div>
            <div className="text-sm text-gray-600 mt-1">Discover</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="text-2xl font-bold text-gray-900">2</div>
            <div className="text-sm text-gray-600 mt-1">Rebuild</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="text-2xl font-bold text-gray-900">3</div>
            <div className="text-sm text-gray-600 mt-1">Ship</div>
          </div>
        </div>
      </div>
    </div>
  );
}
