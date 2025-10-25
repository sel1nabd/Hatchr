"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [verified, setVerified] = useState(false);
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [rolesOpen, setRolesOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const [loadingMatches, setLoadingMatches] = useState(false);
  const [matchError, setMatchError] = useState<string | null>(null);
  const [matches, setMatches] = useState<Array<{ name: string; compatibility: number; reason: string; skills?: string[]; experienceLevel?: string }>>([]);

  const ROLES = [
    "CMO",
    "CTO",
    "Tech Lead",
    "Designer",
    "Sales Lead",
    "COO",
    "Data Scientist",
    "iOS Engineer",
  ];

  const rolesRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (rolesRef.current && !rolesRef.current.contains(e.target as Node)) {
        setRolesOpen(false);
      }
    }
    document.addEventListener("click", onDocClick);
    return () => document.removeEventListener("click", onDocClick);
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setError(null);

    try {
      // Persist prompt, verification and desired roles for downstream use (generate/launch pages)
      localStorage.setItem("startupPrompt", prompt);
      localStorage.setItem("isVerified", String(verified));
      localStorage.setItem("desiredRoles", JSON.stringify(selectedRoles));

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

  async function handleFindCofoundersNow() {
    if (!prompt.trim()) return;
    setLoadingMatches(true);
    setMatchError(null);
    setMatches([]);
    try {
      const verifiedFlag = verified;
      // Build a lightweight profile for the matcher
      const lower = prompt.toLowerCase();
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
      selectedRoles.forEach((r) => (ROLE_SKILL_MAP[r] || []).forEach((s) => skills.add(s)));

      const body = {
        name: "Prospective Founder",
        skills: Array.from(skills).join(", "),
        goals: prompt,
        personality: verifiedFlag ? "Trusted, execution-focused" : "Curious, collaborative",
        experienceLevel: verifiedFlag ? "Senior" : "Mid-Level",
      };
      const res = await fetch("/api/findCofounder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error("request failed");
      const data = await res.json();
      setMatches(data.matches || []);
    } catch (e: any) {
      setMatchError(e?.message || "Unable to fetch matches");
    } finally {
      setLoadingMatches(false);
    }
  }

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

        {/* Desired Cofounder Roles */}
        <div className="mt-4" ref={rolesRef}>
          <div className="flex items-start justify-between bg-gradient-to-r from-purple-50 to-pink-50 border border-pink-100 rounded-lg p-3">
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900">Looking for cofounders</div>
              <div className="text-xs text-gray-600">Pick one or more roles you want to find</div>
              {selectedRoles.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {selectedRoles.map((r) => (
                    <span key={r} className="px-2 py-0.5 rounded-full border text-xs bg-white">{r}</span>
                  ))}
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={() => setRolesOpen((o) => !o)}
              className="ml-3 px-3 py-1.5 border border-gray-300 rounded-md text-sm bg-white hover:bg-gray-50"
            >
              Select Roles ▾
            </button>
          </div>
          {rolesOpen && (
            <div className="mt-2 bg-white rounded-lg border border-gray-200 shadow-sm p-3 grid grid-cols-2 gap-2">
              {ROLES.map((role) => {
                const checked = selectedRoles.includes(role);
                return (
                  <label key={role} className="flex items-center gap-2 text-sm text-gray-800">
                    <input
                      type="checkbox"
                      className="w-4 h-4"
                      checked={checked}
                      onChange={(e) => {
                        setSelectedRoles((prev) => {
                          if (e.target.checked) return Array.from(new Set([...prev, role]));
                          return prev.filter((r) => r !== role);
                        });
                      }}
                    />
                    <span>{role}</span>
                  </label>
                );
              })}
            </div>
          )}
        </div>

        {/* Error message */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Actions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            onClick={handleGenerate}
            disabled={!prompt.trim() || isGenerating}
            className="w-full mt-6 px-6 py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isGenerating ? "Generating..." : "Generate Startup"}
          </button>
          <button
            onClick={handleFindCofoundersNow}
            disabled={!prompt.trim() || isGenerating}
            className="w-full mt-6 px-6 py-3 bg-white border border-gray-300 text-gray-900 rounded-lg font-medium hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Find Cofounders Now
          </button>
        </div>

        {(loadingMatches || matches.length > 0 || matchError) && (
          <div className="mt-6 bg-white rounded-lg border border-gray-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-gray-900">Cofounder Suggestions</h3>
              <span className="text-xs text-gray-500">Demo results</span>
            </div>
            <div className="space-y-2">
              {loadingMatches && (
                <>
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={`sk-${i}`} className="flex items-start gap-3 p-3 rounded border border-gray-200 animate-pulse">
                      <div className="w-9 h-9 rounded bg-gray-200" />
                      <div className="flex-1 space-y-2">
                        <div className="h-3 w-32 bg-gray-200 rounded" />
                        <div className="h-3 w-48 bg-gray-200 rounded" />
                      </div>
                    </div>
                  ))}
                </>
              )}
              {!loadingMatches && matchError && (
                <div className="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded p-2">{matchError}</div>
              )}
              {!loadingMatches && !matchError && matches.length === 0 && (
                <p className="text-sm text-gray-600">No suggestions yet. Try adjusting roles and prompt above.</p>
              )}
              {!loadingMatches && !matchError && matches.length > 0 && (
                <div className="space-y-2">
                  {matches.map((m, idx) => (
                    <div key={`${m.name}-${idx}`} className="flex items-start gap-3 p-3 rounded border border-gray-200 hover:border-gray-300">
                      <div className="w-9 h-9 rounded bg-gray-900 text-white flex items-center justify-center text-xs font-semibold">
                        {m.name.split(' ').map(s=>s[0]).slice(0,2).join('').toUpperCase()}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{m.name}</div>
                            {m.experienceLevel && <div className="text-xs text-gray-500">{m.experienceLevel}</div>}
                          </div>
                          <span className="text-xs font-medium px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">{m.compatibility}% match</span>
                        </div>
                        <div className="text-sm text-gray-700 mt-1">{m.reason}</div>
                        {m.skills && m.skills.length > 0 && (
                          <div className="mt-1 flex flex-wrap gap-1">
                            {m.skills.slice(0, 4).map((s, i) => (
                              <span key={`${s}-${i}`} className="px-2 py-0.5 rounded-full border text-xs bg-white">{s}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

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
