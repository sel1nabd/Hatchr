"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

type Match = {
  name: string;
  compatibility: number;
  reason: string;
  skills?: string[];
  experienceLevel?: string;
};

const GRADIENTS = [
  "from-indigo-500 to-purple-500",
  "from-blue-500 to-cyan-500",
  "from-teal-500 to-emerald-500",
  "from-orange-500 to-pink-500",
];

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

export default function PromptV2() {
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const [verified, setVerified] = useState(false);
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [rolesOpen, setRolesOpen] = useState(false);
  const rolesRef = useRef<HTMLDivElement | null>(null);

  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Inline cofounder quick suggestions
  const [loadingMatches, setLoadingMatches] = useState(false);
  const [matchError, setMatchError] = useState<string | null>(null);
  const [matches, setMatches] = useState<Match[] | null>(null);

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (rolesRef.current && !rolesRef.current.contains(e.target as Node)) {
        setRolesOpen(false);
      }
    }
    document.addEventListener("click", onDocClick);
    return () => document.removeEventListener("click", onDocClick);
  }, []);

  const founderProfile = useMemo(() => {
    const skills = new Set<string>(["Product", "Go-To-Market"]);
    const p = prompt.toLowerCase();
    if (p.includes("ai") || p.includes("machine")) { skills.add("AI"); skills.add("ML"); }
    if (p.includes("health") || p.includes("med")) { skills.add("Healthcare"); skills.add("Compliance"); }
    if (p.includes("fintech") || p.includes("finance") || p.includes("payments")) { skills.add("Fintech"); skills.add("Risk"); }
    if (p.includes("web3") || p.includes("blockchain")) { skills.add("Blockchain"); skills.add("Smart Contracts"); }
    if (p.includes("education") || p.includes("edtech")) { skills.add("Education"); skills.add("Curriculum Design"); }
    if (p.includes("saas") || p.includes("platform")) { skills.add("SaaS"); skills.add("Platform Engineering"); }
    if (p.includes("mobile")) { skills.add("Mobile"); skills.add("UX"); }
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
    const experienceLevel = verified ? "Senior" : "Mid-Level";
    return {
      name: "Prospective Founder",
      skills: Array.from(skills).join(", "),
      goals: prompt.trim() || "Launch a new startup",
      personality: verified ? "Trusted, execution-focused" : "Curious, collaborative",
      experienceLevel,
    };
  }, [prompt, verified, selectedRoles]);

  async function handleGenerate() {
    if (!prompt.trim()) return;
    setIsGenerating(true);
    setError(null);
    try {
      // Persist metadata for downstream pages
      localStorage.setItem("startupPrompt", prompt);
      localStorage.setItem("isVerified", String(verified));
      localStorage.setItem("desiredRoles", JSON.stringify(selectedRoles));
      const res = await api.generateStartup({ prompt, verified });
      localStorage.setItem("currentJobId", res.job_id);
      router.push(`/generate?jobId=${res.job_id}`);
    } catch (e) {
      setError("Failed to start generation. Please try again.");
      setIsGenerating(false);
    }
  }

  async function handleFindCofounders() {
    if (!prompt.trim()) return;
    setLoadingMatches(true);
    setMatchError(null);
    try {
      const res = await fetch("/api/findCofounder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(founderProfile),
      });
      if (!res.ok) throw new Error("request failed");
      const data = await res.json();
      setMatches(data.matches || []);
    } catch (e: any) {
      setMatchError(e?.message || "Unable to fetch matches");
      setMatches([]);
    } finally {
      setLoadingMatches(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex flex-col relative overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000" />
      </div>

      {/* Header */}
      <header className="w-full py-8 px-6 relative z-10">
        <div className="max-w-[700px] mx-auto">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-gradient-to-br from-indigo-600 to-purple-600 p-2 rounded-xl shadow-lg">
              <svg viewBox="0 0 24 24" className="w-6 h-6 text-white"><circle cx="12" cy="12" r="10" fill="currentColor" /></svg>
            </div>
            <h1 className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">HatchR</h1>
          </div>
          <p className="text-slate-700">Build a startup from a single idea.</p>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 px-6 py-12 relative z-10">
        <div className="max-w-[700px] mx-auto space-y-8">
          {/* Main Card */}
          <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/20 p-8 space-y-6">
            {/* Prompt */}
            <div className="space-y-2">
              <label className="text-slate-900 text-sm font-medium">Describe what you want to build</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g., 'Airbnb for pets'"
                className="min-h-[180px] w-full resize-none text-lg bg-white/50 border border-slate-200 focus:border-indigo-400 focus:ring-indigo-400/20 rounded-xl px-4 py-3 outline-none"
              />
              <p className="text-slate-500 text-sm">Be as specific or creative as you'd like</p>
            </div>

            {/* Roles */}
            <div className="flex items-start justify-between p-4 rounded-xl bg-gradient-to-r from-purple-50 to-pink-50 border border-pink-100" ref={rolesRef}>
              <div className="flex-1 min-w-0">
                <div className="text-slate-900 font-medium">Looking for cofounders</div>
                <p className="text-slate-600 text-sm">Pick one or more roles you want to find</p>
                {selectedRoles.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {selectedRoles.map((r) => (
                      <span key={r} className="inline-flex items-center px-2 py-0.5 rounded-full border text-xs bg-white/70">{r}</span>
                    ))}
                  </div>
                )}
              </div>
              <button
                type="button"
                onClick={() => setRolesOpen((o) => !o)}
                className="ml-3 px-3 py-2 border border-slate-300 rounded-md text-sm bg-white hover:bg-slate-50"
              >
                Select Roles ▾
              </button>
            </div>
            {rolesOpen && (
              <div className="-mt-3 rounded-xl border border-slate-200 bg-white p-3 grid grid-cols-2 gap-2">
                {ROLES.map((role) => {
                  const checked = selectedRoles.includes(role);
                  return (
                    <label key={role} className="flex items-center gap-2 text-sm text-slate-800">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={(e) =>
                          setSelectedRoles((prev) => (e.target.checked ? Array.from(new Set([...prev, role])) : prev.filter((r) => r !== role)))
                        }
                        className="w-4 h-4"
                      />
                      <span>{role}</span>
                    </label>
                  );
                })}
              </div>
            )}

            {/* Verified toggle */}
            <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100">
              <div className="flex items-center gap-3">
                <div className="bg-white p-2 rounded-lg shadow-sm">
                  <svg viewBox="0 0 24 24" className="w-5 h-5 text-indigo-600"><circle cx="12" cy="12" r="10" fill="currentColor" /></svg>
                </div>
                <div>
                  <label className="text-slate-900 font-medium">Verified Founder</label>
                  <p className="text-slate-600 text-sm">Uses Concordium blockchain</p>
                </div>
              </div>
              <input type="checkbox" checked={verified} onChange={(e) => setVerified(e.target.checked)} className="w-5 h-5" />
            </div>

            {/* Actions */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                onClick={handleGenerate}
                disabled={!prompt.trim() || isGenerating}
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-lg py-3 font-semibold shadow-lg"
              >
                {isGenerating ? "Generating..." : "Generate Startup"}
              </button>
              <button
                onClick={handleFindCofounders}
                disabled={!prompt.trim()}
                className="w-full border border-slate-300 hover:border-indigo-300 bg-white rounded-lg py-3 font-semibold"
              >
                Find Cofounders Now
              </button>
            </div>

            {error && (
              <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded p-3">{error}</div>
            )}
          </div>

          {/* Feature Pills */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 text-center border border-white/40 hover:bg-white/80 transition-all duration-200">
              <div className="bg-gradient-to-br from-blue-500 to-cyan-500 w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-2" />
              <p className="text-slate-700">Market Analysis</p>
            </div>
            <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 text-center border border-white/40 hover:bg-white/80 transition-all duration-200">
              <div className="bg-gradient-to-br from-purple-500 to-pink-500 w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-2" />
              <p className="text-slate-700">MVP Builder</p>
            </div>
            <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 text-center border border-white/40 hover:bg-white/80 transition-all duration-200">
              <div className="bg-gradient-to-br from-orange-500 to-red-500 w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-2" />
              <p className="text-slate-700">AI Powered</p>
            </div>
          </div>
        </div>
      </main>

      {/* Cofounder Suggestions (inline) */}
      {(loadingMatches || matchError || matches) && (
        <section className="px-6 pb-12 relative z-10">
          <div className="max-w-[700px] mx-auto">
            <div className="bg-white/80 backdrop-blur-xl border border-white/20 shadow-xl rounded-2xl p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-slate-900 font-semibold">Cofounder Suggestions</h3>
                <span className="text-xs text-slate-500">Demo recommendations</span>
              </div>
              <div className="space-y-3">
                {loadingMatches && (
                  <>
                    {Array.from({ length: 3 }).map((_, i) => (
                      <div key={`sk-${i}`} className="flex items-start gap-4 p-4 rounded-xl border border-slate-200 bg-white/60 animate-pulse">
                        <div className="w-12 h-12 rounded-xl bg-slate-200" />
                        <div className="flex-1 space-y-2">
                          <div className="h-3 w-32 bg-slate-200 rounded" />
                          <div className="h-3 w-48 bg-slate-200 rounded" />
                        </div>
                      </div>
                    ))}
                  </>
                )}
                {!loadingMatches && matchError && (
                  <div className="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded p-3">{matchError}</div>
                )}
                {!loadingMatches && !matchError && matches && matches.length === 0 && (
                  <p className="text-sm text-slate-600">No suggestions yet. Try adjusting roles or prompt.</p>
                )}
                {!loadingMatches && !matchError && matches && matches.length > 0 && matches.map((m, idx) => (
                  <div key={`${m.name}-${idx}`} className="flex items-start gap-4 p-4 rounded-xl bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200 hover:border-indigo-300 hover:shadow-md transition-all duration-200">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${GRADIENTS[idx % GRADIENTS.length]} flex items-center justify-center text-white font-semibold`}>
                      {m.name.split(' ').map(s=>s[0]).slice(0,2).join('').toUpperCase()}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-slate-900 font-medium">{m.name}</div>
                          {m.experienceLevel && (<div className="text-xs text-slate-500">{m.experienceLevel}</div>)}
                        </div>
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">{m.compatibility}% match</span>
                      </div>
                      <div className="text-slate-700 text-sm mt-1">{m.reason}</div>
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
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="w-full py-6 px-6 border-t border-white/30 relative z-10 bg-white/20 backdrop-blur-sm">
        <div className="max-w-[700px] mx-auto text-center text-slate-600">
          <p>Privacy · © 2025 HatchR</p>
        </div>
      </footer>

      <style>{`
        @keyframes blob { 0%, 100% { transform: translate(0,0) scale(1);} 33% { transform: translate(30px,-50px) scale(1.1);} 66% { transform: translate(-20px,20px) scale(0.9);} }
        .animate-blob { animation: blob 7s infinite; }
        .animation-delay-2000 { animation-delay: 2s; }
        .animation-delay-4000 { animation-delay: 4s; }
      `}</style>
    </div>
  );
}

