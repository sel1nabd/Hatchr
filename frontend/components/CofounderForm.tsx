"use client";

import React, { FormEvent, useState } from "react";

export type CofounderMatch = {
  name: string;
  compatibility: number;
  reason: string;
  skills?: string[];
  goals?: string;
  personality?: string;
  experienceLevel?: string;
};

export type CofounderFormValues = {
  name: string;
  skills: string;
  goals: string;
  experienceLevel: string;
  personality: string;
};

const emptyForm: CofounderFormValues = {
  name: "",
  skills: "",
  goals: "",
  experienceLevel: "Mid-Level",
  personality: "",
};

function ProfileModal({ open, onClose, match }: { open: boolean; onClose: () => void; match: CofounderMatch | null }) {
  if (!open || !match) return null;
  return (
    <div className="fixed inset-0 flex items-center justify-center z-30 bg-black bg-opacity-30">
      <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-lg w-full relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 focus:outline-none text-2xl">×</button>
        <div className="flex gap-6 items-center border-b pb-4">
          <img src={`https://ui-avatars.com/api/?background=0D8ABC&color=fff&name=${encodeURIComponent(match.name || "Co-Founder")}`}
            alt={match.name}
            className="w-20 h-20 rounded-full border-2 border-gray-200 shadow-sm" />
          <div>
            <h3 className="text-2xl font-semibold mb-1">{match.name}</h3>
            <span className="inline-block mt-1 px-2 py-0.5 bg-green-100 text-green-800 rounded text-xs font-medium">{match.experienceLevel || "Verified Founder"}</span>
            <div className="mt-2 flex flex-wrap gap-2">
              {match.skills && match.skills.map((skill, i) => (
                <span key={i} className="bg-gray-100 text-blue-800 px-2 py-0.5 rounded-full text-xs font-medium border">{skill}</span>
              ))}
            </div>
          </div>
        </div>
        <div className="mt-6 space-y-4">
          <div>
            <span className="font-semibold text-gray-700">Startup Goals:</span>
            <p className="mt-1 text-gray-900">{match.goals}</p>
          </div>
          <div>
            <span className="font-semibold text-gray-700">Personality:</span>
            <p className="mt-1 text-gray-900">{match.personality}</p>
          </div>
          <div>
            <span className="font-semibold text-gray-700">Compatibility Score:</span>
            <span className="inline-block ml-2 px-3 py-1 rounded-lg bg-blue-600 text-white font-bold text-lg">{match.compatibility}%</span>
            <div className="mt-1 text-gray-600 text-sm">{match.reason}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function CofounderForm() {
  const [formValues, setFormValues] = useState<CofounderFormValues>(emptyForm);
  const [isLoading, setIsLoading] = useState(false);
  const [matches, setMatches] = useState<CofounderMatch[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [modalMatch, setModalMatch] = useState<CofounderMatch | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const handleChange = (
    field: keyof CofounderFormValues,
    value: string,
  ) => setFormValues((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true); setError(null);
    try {
      const response = await fetch("/api/findCofounder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formValues),
      });
      if (!response.ok) {
        const errorPayload = await response.json().catch(() => null);
        throw new Error(errorPayload?.error ?? "Something went wrong");
      }
      const data = await response.json();
      // Try to fetch more info from DB for richer profiles
      let enriched = data.matches;
      try {
        const res = await fetch("/data/mockFounders.json");
        if (res.ok) {
          const db = await res.json();
          enriched = data.matches.map((match: CofounderMatch) => {
            const profile = db.find((p: any) => p.name === match.name);
            return profile ? { ...match, ...profile } : match;
          });
        }
      } catch {}
      setMatches(enriched);
      setFormValues(emptyForm);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to find co-founder matches");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white border border-gray-200 shadow-md rounded-2xl p-8 space-y-8 max-w-xl mx-auto">
      <div className="space-y-2 text-center">
        <h2 className="text-3xl font-bold tracking-tight">AI Co-Founder Finder</h2>
        <p className="text-sm text-gray-500">Verified via Concordium ID</p>
        <p className="text-md text-gray-700">Find your ideal startup partner. Share your profile to get instant AI matches.</p>
      </div>
      <form className="space-y-6" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label className="text-base font-semibold text-gray-800" htmlFor="name">Your Name</label>
          <input id="name" type="text" value={formValues.name} onChange={e => handleChange("name", e.target.value)} placeholder="Alex Founder" className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent" required />
        </div>
        <div className="space-y-2">
          <label className="text-base font-semibold text-gray-800" htmlFor="skills">Skills</label>
          <textarea id="skills" value={formValues.skills} onChange={e => handleChange("skills", e.target.value)} placeholder="AI, Product, Finance" className="w-full h-16 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent resize-none" required />
        </div>
        <div className="space-y-2">
          <label className="text-base font-semibold text-gray-800" htmlFor="goals">Startup Goals</label>
          <textarea id="goals" value={formValues.goals} onChange={e => handleChange("goals", e.target.value)} placeholder="Launch an AI-powered automation platform for SMBs" className="w-full h-20 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent resize-none" required />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-base font-semibold text-gray-800" htmlFor="experienceLevel">Experience Level</label>
            <select id="experienceLevel" value={formValues.experienceLevel} onChange={e => handleChange("experienceLevel", e.target.value)} className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent">
              <option value="Entry">Entry</option>
              <option value="Mid-Level">Mid-Level</option>
              <option value="Senior">Senior</option>
              <option value="Serial Founder">Serial Founder</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-base font-semibold text-gray-800" htmlFor="personality">Personality & Working Style</label>
            <textarea id="personality" value={formValues.personality} onChange={e => handleChange("personality", e.target.value)} placeholder="Collaborative, fast-paced, data-informed" className="w-full h-20 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent resize-none" required />
          </div>
        </div>
        <button type="submit" disabled={isLoading} className="w-full px-6 py-3 bg-blue-700 text-white rounded-lg font-bold hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 disabled:opacity-60 transition-colors">
          {isLoading ? "Finding Matches..." : "Find My Co-Founder"}
        </button>
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}
      </form>
      {matches && (
        <div className="space-y-6">
          <h3 className="text-xl font-bold text-gray-800">Recommended Matches</h3>
          {matches.length === 0 && (<p className="text-md text-gray-600">No matches yet. Try refining your skills or goals.</p>)}
          {matches.map((match, idx) => (
            <div key={match.name + idx}
              className="flex items-center gap-6 bg-gradient-to-br from-white to-blue-50 border border-gray-200 rounded-xl p-5 shadow-md hover:shadow-lg transition-shadow cursor-pointer hover:scale-[1.012]"
              onClick={() => { setModalMatch(match); setModalOpen(true); }}
              tabIndex={0}
            >
              <img src={`https://ui-avatars.com/api/?background=87cefa&color=222&bold=true&name=${encodeURIComponent(match.name || "CoFounder")}`}
                  alt={match.name}
                  className="w-14 h-14 rounded-full border-2 border-blue-200 shadow-sm"/>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-lg text-blue-900 line-clamp-1">{match.name}</span>
                  <span className="ml-2 px-2 py-0.5 bg-green-100 text-green-800 rounded text-xs font-medium">{match.experienceLevel || "Verified Founder"}</span>
                </div>
                <div className="mt-1 flex flex-wrap gap-1">
                  {match.skills && match.skills.map((skill, i) => (
                    <span key={i} className="bg-gray-100 text-blue-800 px-2 py-0.5 rounded-full text-xs font-medium border">{skill}</span>
                  ))}
                </div>
                <div className="mt-2 text-gray-800"><span className="font-medium">Startup goal:</span> <span className="text-gray-700">{match.goals}</span></div>
              </div>
              <div className="text-center min-w-[90px]">
                <div className="text-2xl font-extrabold text-blue-900">{match.compatibility}%</div>
                <div className="text-xs text-gray-500">Compatibility</div>
                <button className="mt-2 w-full bg-white border border-blue-300 rounded-lg text-blue-700 px-3 py-1 font-semibold hover:bg-blue-50 transition-colors"
                    tabIndex={0}
                    onClick={e => { e.stopPropagation(); setModalMatch(match); setModalOpen(true); }}>
                  View Profile
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      <ProfileModal open={modalOpen} match={modalMatch} onClose={() => setModalOpen(false)} />
    </div>
  );
}
