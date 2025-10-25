"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import type { ProjectResponse, LaunchChannel } from "@/lib/types";

export default function Launch() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get("projectId") || localStorage.getItem("currentProjectId");

  const [project, setProject] = useState<ProjectResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [matches, setMatches] = useState<Array<{ name: string; compatibility: number; reason: string; skills?: string[]; experienceLevel?: string }>>([]);
  const [loadingMatches, setLoadingMatches] = useState<boolean>(false);

  // Fetch project data from backend
  useEffect(() => {
    if (!projectId) {
      setError("No project ID found. Please complete generation first.");
      setLoading(false);
      return;
    }

    async function fetchProject() {
      try {
        const data = await api.getProject(projectId!);
        setProject(data);
      } catch (err) {
        console.error("Failed to fetch project:", err);
        setError("Failed to load project. Please try again.");
      } finally {
        setLoading(false);
      }
    }

    fetchProject();
  }, [projectId]);

  // Build a lightweight founder profile from stored prompt + roles and fetch matches
  useEffect(() => {
    async function fetchMatches() {
      try {
        const promptText = localStorage.getItem("startupPrompt") || "";
        const verified = localStorage.getItem("isVerified") === "true";
        let desiredRoles: string[] = [];
        try {
          desiredRoles = JSON.parse(localStorage.getItem("desiredRoles") || "[]");
        } catch {}

        const lower = promptText.toLowerCase();
        const skills = new Set<string>(["Product", "Go-To-Market"]);
        if (lower.includes("ai") || lower.includes("machine")) { skills.add("AI"); skills.add("ML"); }
        if (lower.includes("health") || lower.includes("med")) { skills.add("Healthcare"); skills.add("Compliance"); }
        if (lower.includes("fintech") || lower.includes("finance") || lower.includes("payments")) { skills.add("Fintech"); skills.add("Risk"); }
        if (lower.includes("web3") || lower.includes("blockchain")) { skills.add("Blockchain"); skills.add("Smart Contracts"); }
        if (lower.includes("education") || lower.includes("edtech")) { skills.add("Education"); skills.add("Curriculum Design"); }
        if (lower.includes("saas") || lower.includes("platform")) { skills.add("SaaS"); skills.add("Platform Engineering"); }
        if (lower.includes("mobile")) { skills.add("Mobile"); skills.add("UX"); }

        const ROLE_SKILL_MAP: Record<string, string[]> = {
          CMO: ["Marketing", "Growth", "SEO", "Brand", "Content"],
          CTO: ["Full-Stack", "DevOps", "Cloud Architecture", "Node.js"],
          "Tech Lead": ["Engineering Leadership", "Architecture", "TypeScript"],
          Designer: ["Design", "Figma", "UX", "UI/UX"],
          "Sales Lead": ["Sales", "BD", "Partnerships"],
          COO: ["Operations", "Finance", "Analytics"],
          "Data Scientist": ["ML", "Data Science", "Python"],
          "iOS Engineer": ["iOS", "Swift", "Mobile"],
        };
        desiredRoles.forEach((r) => (ROLE_SKILL_MAP[r] || []).forEach((s) => skills.add(s)));

        const body = {
          name: "Prospective Founder",
          skills: Array.from(skills).join(", "),
          goals: promptText || (project?.project_name ? `Launch ${project.project_name}` : "Launch startup"),
          personality: verified ? "Trusted, execution-focused" : "Curious, collaborative",
          experienceLevel: verified ? "Senior" : "Mid-Level",
        };

        setLoadingMatches(true);
        const res = await fetch("/api/findCofounder", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error("match request failed");
        const data = await res.json();
        setMatches(data.matches || []);
      } catch (e) {
        console.warn("cofounder match request failed", e);
        setMatches([]);
      } finally {
        setLoadingMatches(false);
      }
    }

    // Only trigger after project has loaded or when projectId exists
    if (projectId) {
      fetchMatches();
    }
  }, [projectId, project]);

  const handleRerun = () => {
    router.push("/");
  };

  const handleDownloadPlan = () => {
    // TODO: Export to Notion or download as markdown
    console.log("Downloading launch plan...");
  };

  // Show loading state
  if (loading) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 text-center">
          <p className="text-gray-600">Loading project details...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error || !project) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-red-50 rounded-lg border border-red-200 shadow-sm p-6">
          <p className="text-red-700 mb-4">
            {error || "Project not found"}
          </p>
          <button
            onClick={() => router.push("/")}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Startup overview */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-2">
          Your Startup: {project.project_name}
        </h2>
        <p className="text-gray-600 mb-4">
          {project.tagline}
        </p>

        <div className="flex flex-wrap gap-2 mb-4">
          {project.stack.map((tech, idx) => (
            <span key={idx} className="px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-700">
              {tech}
            </span>
          ))}
        </div>

        {project.verified && (
          <div className="inline-flex items-center gap-2 bg-green-50 px-3 py-1 rounded-full border border-green-200">
            <span className="text-sm">✅</span>
            <span className="text-xs font-medium text-green-800">
              Concordium verified
            </span>
          </div>
        )}
      </div>

      {/* Lovable Build Section */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200 shadow-sm p-6">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
            <span className="text-2xl">🚀</span>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Build Your App on Lovable
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Click below to open Lovable and automatically build your app.
              The AI will create a complete, production-ready website based on your idea.
            </p>
            <div className="bg-white rounded-lg border border-gray-300 p-3 mb-4">
              <p className="text-xs font-medium text-gray-600 mb-1">Your Lovable Build URL:</p>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={project.lovable_url}
                  readOnly
                  className="flex-1 text-xs font-mono bg-gray-50 px-2 py-1 rounded border border-gray-200"
                />
                <button
                  onClick={() => navigator.clipboard.writeText(project.lovable_url)}
                  className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded border border-gray-300"
                >
                  Copy
                </button>
              </div>
            </div>
            <a
              href={project.lovable_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm"
            >
              🚀 Build on Lovable →
            </a>
            <p className="text-xs text-gray-500 mt-3">
              Opens in new tab • Auto-builds your app • Free to use
            </p>
          </div>
        </div>
      </div>

      {/* GPT-5 Analysis */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">AI Analysis</h3>

        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Market Information</h4>
            <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
              {project.analysis.information}
            </p>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Recommended Structure</h4>
            <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3 whitespace-pre-wrap">
              {project.analysis.structure}
            </p>
          </div>
        </div>
      </div>

      {/* Marketing assets */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Marketing Assets</h3>
        <p className="text-sm text-gray-600 mb-4">
          Auto-generated pitch materials using Livepeer Daydream
        </p>

        <div className="space-y-3">
          {/* Video pitch */}
          <div className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl">🎬</span>
                  <h4 className="font-medium">Pitch Video</h4>
                </div>
                <p className="text-sm text-gray-600">
                  30-second promotional video
                </p>
              </div>
              <button className="px-3 py-1 text-sm font-medium text-gray-700 border border-gray-300 rounded hover:bg-gray-50 transition-colors">
                View
              </button>
            </div>
          </div>

          {/* Pitch deck */}
          <div className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl">📊</span>
                  <h4 className="font-medium">Pitch Deck</h4>
                </div>
                <p className="text-sm text-gray-600">
                  5-slide investor overview
                </p>
              </div>
              <button className="px-3 py-1 text-sm font-medium text-gray-700 border border-gray-300 rounded hover:bg-gray-50 transition-colors">
                Download
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Launch channels */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Recommended Launch Channels</h3>
          <button
            onClick={handleDownloadPlan}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Export Plan
          </button>
        </div>

        <div className="space-y-2">
          {project.launch_channels.map((channel, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-2 h-2 rounded-full ${channel.priority === "high"
                      ? "bg-red-500"
                      : channel.priority === "medium"
                        ? "bg-yellow-500"
                        : "bg-green-500"
                    }`}
                />
                <div>
                  <h4 className="font-medium text-sm">{channel.name}</h4>
                  <p className="text-xs text-gray-600">
                    {channel.description}
                  </p>
                </div>
              </div>
              <span
                className={`text-xs font-medium px-2 py-1 rounded ${channel.priority === "high"
                    ? "bg-red-50 text-red-700"
                    : channel.priority === "medium"
                      ? "bg-yellow-50 text-yellow-700"
                      : "bg-green-50 text-green-700"
                  }`}
              >
                {channel.priority}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Cofounder Suggestions */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold">Cofounder Suggestions</h3>
          <span className="text-xs text-gray-500">Demo recommendations</span>
        </div>
        <div className="space-y-3">
          {loadingMatches && (
            <>
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={`sk-${i}`} className="flex items-start gap-4 p-3 border border-gray-200 rounded-lg animate-pulse">
                  <div className="w-10 h-10 rounded bg-gray-200" />
                  <div className="flex-1 space-y-2">
                    <div className="h-3 w-32 bg-gray-200 rounded" />
                    <div className="h-3 w-48 bg-gray-200 rounded" />
                  </div>
                </div>
              ))}
            </>
          )}
          {!loadingMatches && matches.length === 0 && (
            <p className="text-sm text-gray-600">No suggestions yet. Try adjusting roles on the home prompt.</p>
          )}
          {!loadingMatches && matches.length > 0 && matches.map((m, idx) => (
            <div key={`${m.name}-${idx}`} className="flex items-start gap-4 p-3 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
              <div className="w-10 h-10 rounded bg-gray-900 text-white flex items-center justify-center text-xs font-semibold">
                {m.name.split(' ').map(s=>s[0]).slice(0,2).join('').toUpperCase()}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900">{m.name}</div>
                    {m.experienceLevel && (<div className="text-xs text-gray-500">{m.experienceLevel}</div>)}
                  </div>
                  <span className="text-xs font-medium px-2 py-1 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">{m.compatibility}% match</span>
                </div>
                <div className="text-sm text-gray-700 mt-1">{m.reason}</div>
                {m.skills && m.skills.length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {m.skills.slice(0,4).map((s,i)=>(
                      <span key={`${s}-${i}`} className="px-2 py-0.5 rounded-full border text-xs bg-white">{s}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Next steps */}
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-6">
        <h3 className="font-semibold mb-3">Next Steps</h3>
        <ol className="space-y-2 text-sm text-gray-700">
          <li className="flex gap-2">
            <span className="font-medium">1.</span>
            <span>Customize your generated app with branding and content</span>
          </li>
          <li className="flex gap-2">
            <span className="font-medium">2.</span>
            <span>Deploy to Vercel or your preferred hosting platform</span>
          </li>
          <li className="flex gap-2">
            <span className="font-medium">3.</span>
            <span>Share marketing materials on recommended channels</span>
          </li>
          <li className="flex gap-2">
            <span className="font-medium">4.</span>
            <span>Collect early user feedback and iterate</span>
          </li>
        </ol>

        <button
          onClick={handleRerun}
          className="w-full mt-6 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          ← Build Another Startup
        </button>
      </div>
    </div>
  );
}
