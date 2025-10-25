"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import ConcordiumVerify from "@/components/ConcordiumVerify";
import { api } from "@/lib/api";
import type { BuildStep, LogEntry } from "@/lib/types";

export default function Generate() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const jobId = searchParams.get("jobId") || localStorage.getItem("currentJobId");

  const [steps, setSteps] = useState<BuildStep[]>([
    { id: 1, title: "Finding competitors", status: "pending" },
    { id: 2, title: "Building MVP", status: "pending" },
    { id: 3, title: "Packaging startup", status: "pending" },
  ]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const [progress, setProgress] = useState(0);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [projectName, setProjectName] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  // Poll job status from backend
  useEffect(() => {
    if (!jobId) {
      setError("No job ID found. Please start from the home page.");
      return;
    }

    console.log(`[Generate] Starting polling for job: ${jobId}`);

    const interval = setInterval(async () => {
      try {
        const status = await api.getStatus(jobId);

        // Update state from API response
        setSteps(status.steps);
        setLogs(status.logs);
        setProgress(status.progress);

        if (status.project_name) {
          setProjectName(status.project_name);
        }

        // Check if completed or failed
        if (status.status === "completed") {
          clearInterval(interval);
          setIsComplete(true);
          if (status.project_id) {
            setProjectId(status.project_id);
            localStorage.setItem("currentProjectId", status.project_id);
          }
        } else if (status.status === "failed") {
          clearInterval(interval);
          setError("Generation failed. Please try again.");
        }
      } catch (err) {
        console.error("Polling error:", err);
        setError("Failed to check status. Retrying...");
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [jobId]);

  const handleBuildOnLovable = async () => {
    if (!projectId) return;
    try {
      const result = await api.getLovableUrl(projectId);
      window.open(result.lovable_url, "_blank");
    } catch (err) {
      console.error("Failed to get Lovable URL:", err);
      alert("Failed to get Lovable URL. Please try again.");
    }
  };

  const handleViewLaunch = () => {
    if (projectId) {
      router.push(`/launch?projectId=${projectId}`);
    }
  };

  // Show error if no job ID
  if (!jobId) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-red-50 rounded-lg border border-red-200 shadow-sm p-6">
          <p className="text-red-700">
            No generation in progress. Please start from the home page.
          </p>
          <button
            onClick={() => router.push("/")}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Progress header */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Building Your Startup</h2>

        {/* Progress bar */}
        <div className="mb-6">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gray-900 h-2 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {Math.round(progress)}% complete
          </p>
        </div>

        {/* Build steps */}
        <div className="space-y-3">
          {steps.map((step) => (
            <div key={step.id} className="flex items-center gap-3">
              <div
                className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${step.status === "completed"
                  ? "bg-green-100 text-green-700"
                  : step.status === "in_progress"
                    ? "bg-blue-100 text-blue-700 animate-pulse"
                    : "bg-gray-100 text-gray-500"
                  }`}
              >
                {step.status === "completed" ? "✓" : step.id}
              </div>
              <span
                className={`text-sm ${step.status === "completed"
                  ? "text-gray-900 font-medium"
                  : step.status === "in_progress"
                    ? "text-gray-900"
                    : "text-gray-500"
                  }`}
              >
                {step.title}
              </span>
            </div>
          ))}
        </div>

        {/* Error display */}
        {error && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Console logs */}
      <div className="bg-gray-900 rounded-lg p-4 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-gray-300">Build Logs</h3>
          <span className="text-xs text-gray-500">Live output</span>
        </div>
        <div className="bg-black rounded p-3 h-64 overflow-y-auto font-mono text-xs space-y-1">
          {logs.map((log, idx) => (
            <div
              key={idx}
              className={`${log.type === "success"
                ? "text-green-400"
                : log.type === "error"
                  ? "text-red-400"
                  : "text-gray-300"
                }`}
            >
              <span className="text-gray-600">[{log.timestamp}]</span>{" "}
              {log.message}
            </div>
          ))}
        </div>
      </div>

      {/* Completion card */}
      {isComplete && projectId && (
        <div className="bg-green-50 rounded-lg border border-green-200 shadow-sm p-6">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-700 text-lg">✓</span>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-green-900 mb-1">
                Startup Generated: {projectName || "Your Startup"}
              </h3>
              <p className="text-sm text-green-800 mb-4">
                Your full-stack application is ready to deploy
              </p>

              {/* Concordium badge */}
              <div className="inline-flex items-center gap-2 bg-white px-3 py-1 rounded-full border border-green-200 mb-4">
                <span className="text-sm">✅</span>
                <span className="text-xs font-medium text-gray-700">
                  Concordium verified founder
                </span>
              </div>

              {/* Action buttons */}
              <div className="flex gap-3">
                <button
                  onClick={handleBuildOnLovable}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
                >
                  🚀 Build on Lovable →
                </button>
                <button
                  onClick={handleViewLaunch}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
                >
                  View Details →
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
