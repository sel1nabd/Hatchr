"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

type BuildStep = {
  id: number;
  title: string;
  status: "pending" | "in_progress" | "completed";
};

type LogEntry = {
  timestamp: string;
  message: string;
  type: "info" | "success" | "error";
};

export default function Generate() {
  const router = useRouter();
  const [steps, setSteps] = useState<BuildStep[]>([
    { id: 1, title: "Finding competitors", status: "in_progress" },
    { id: 2, title: "Building MVP", status: "pending" },
    { id: 3, title: "Packaging startup", status: "pending" },
  ]);
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      timestamp: new Date().toLocaleTimeString(),
      message: "Starting discovery process...",
      type: "info",
    },
  ]);
  const [isComplete, setIsComplete] = useState(false);
  const [progress, setProgress] = useState(0);

  // Simulate build progress
  useEffect(() => {
    // TODO: Replace with actual API polling
    // const interval = setInterval(async () => {
    //   const response = await fetch('/api/status/:jobId');
    //   const data = await response.json();
    //   setSteps(data.steps);
    //   setLogs(data.logs);
    //   setProgress(data.progress);
    // }, 1000);

    // Mock progress simulation
    const mockSteps = [
      { step: 0, delay: 2000, log: "Found 3 similar competitors" },
      { step: 1, delay: 4000, log: "Analyzing competitor features..." },
      { step: 1, delay: 6000, log: "Generating Next.js components..." },
      { step: 1, delay: 8000, log: "Setting up Supabase backend..." },
      { step: 2, delay: 10000, log: "Creating Dockerfile..." },
      { step: 2, delay: 11000, log: "Packaging project files..." },
      { step: 2, delay: 12000, log: "Startup generated successfully!" },
    ];

    mockSteps.forEach(({ step, delay, log }) => {
      setTimeout(() => {
        // Update step status
        setSteps((prev) =>
          prev.map((s, idx) => {
            if (idx < step) return { ...s, status: "completed" };
            if (idx === step) return { ...s, status: "in_progress" };
            return s;
          })
        );

        // Add log entry
        setLogs((prev) => [
          ...prev,
          {
            timestamp: new Date().toLocaleTimeString(),
            message: log,
            type: step === 2 && delay === 12000 ? "success" : "info",
          },
        ]);

        // Update progress
        setProgress((delay / 12000) * 100);

        // Mark complete
        if (delay === 12000) {
          setSteps((prev) =>
            prev.map((s) => ({ ...s, status: "completed" }))
          );
          setIsComplete(true);
        }
      }, delay);
    });
  }, []);

  const handleDownload = () => {
    // TODO: Implement download
    console.log("Downloading startup package...");
  };

  const handleDeploy = () => {
    // TODO: Implement Vercel deployment
    console.log("Deploying to Vercel...");
  };

  const handleViewLaunch = () => {
    router.push("/launch");
  };

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
                className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                  step.status === "completed"
                    ? "bg-green-100 text-green-700"
                    : step.status === "in_progress"
                    ? "bg-blue-100 text-blue-700 animate-pulse"
                    : "bg-gray-100 text-gray-500"
                }`}
              >
                {step.status === "completed" ? "✓" : step.id}
              </div>
              <span
                className={`text-sm ${
                  step.status === "completed"
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
              className={`${
                log.type === "success"
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
      {isComplete && (
        <div className="bg-green-50 rounded-lg border border-green-200 shadow-sm p-6">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-700 text-lg">✓</span>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-green-900 mb-1">
                Startup Generated: AI Scheduling Tool
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
                  onClick={handleDownload}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Download Folder
                </button>
                <button
                  onClick={handleDeploy}
                  className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors"
                >
                  Deploy to Vercel
                </button>
                <button
                  onClick={handleViewLaunch}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
                >
                  View Launch Guide →
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
