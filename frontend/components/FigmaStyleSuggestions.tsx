"use client";

import { useState } from "react";
import { ArrowRightIcon } from "@heroicons/react/24/outline";

type Match = {
  name: string;
  compatibility: number;
  reason: string;
  skills?: string[];
  goals?: string;
  personality?: string;
  experienceLevel?: string;
};

function getInitials(name: string) {
  return name
    .split(" ")
    .map((p) => p.trim()[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

const GRADIENTS = [
  "from-indigo-500 to-purple-500",
  "from-blue-500 to-cyan-500",
  "from-teal-500 to-emerald-500",
  "from-orange-500 to-pink-500",
];

export default function FigmaStyleSuggestions() {
  const [name, setName] = useState("");
  const [skills, setSkills] = useState("");
  const [goals, setGoals] = useState("");
  const [personality, setPersonality] = useState("");
  const [experienceLevel, setExperienceLevel] = useState("Mid-Level");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [matches, setMatches] = useState<Match[] | null>(null);

  const disabled = !skills.trim() || !goals.trim() || !personality.trim();

  async function handleFind() {
    try {
      setLoading(true);
      setError(null);
      setMatches(null);
      const payload = {
        name: name.trim() || "Prospective Founder",
        skills,
        goals,
        personality,
        experienceLevel,
      };
      const res = await fetch("/api/findCofounder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.error || `Request failed (${res.status})`);
      }
      const data = await res.json();
      setMatches(data.matches || []);
    } catch (e: any) {
      setError(e?.message || "Unable to fetch matches");
      setMatches([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200 p-6">
        <div className="grid md:grid-cols-4 gap-4">
          <div className="md:col-span-1">
            <label className="block text-sm font-medium text-gray-800">Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name (optional)"
              className="mt-1 w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <div className="md:col-span-1">
            <label className="block text-sm font-medium text-gray-800">Skills</label>
            <input
              value={skills}
              onChange={(e) => setSkills(e.target.value)}
              placeholder="e.g., AI, React, Growth"
              className="mt-1 w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-800">Goals</label>
            <input
              value={goals}
              onChange={(e) => setGoals(e.target.value)}
              placeholder="What do you want to build?"
              className="mt-1 w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
        </div>
        <div className="grid md:grid-cols-4 gap-4 mt-4">
          <div className="md:col-span-3">
            <label className="block text-sm font-medium text-gray-800">Personality & Working Style</label>
            <input
              value={personality}
              onChange={(e) => setPersonality(e.target.value)}
              placeholder="Collaborative, fast-paced, data-informed"
              className="mt-1 w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-800">Experience</label>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="mt-1 w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              <option>Entry</option>
              <option>Mid-Level</option>
              <option>Senior</option>
              <option>Serial Founder</option>
            </select>
          </div>
        </div>
        <div className="mt-4">
          <button
            onClick={handleFind}
            disabled={disabled || loading}
            className="w-full md:w-auto bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
          >
            Find Matches
            <ArrowRightIcon className="w-5 h-5" />
          </button>
          {error && (
            <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-800">
              {error}
            </div>
          )}
        </div>
      </div>

      {(loading || matches !== null) && (
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cofounder Suggestions</h3>
          <div className="space-y-3">
            {loading &&
              Array.from({ length: 3 }).map((_, i) => (
                <div key={`sk-${i}`} className="flex items-start gap-4 p-4 rounded-xl border border-gray-200 bg-white/60 animate-pulse">
                  <div className="w-12 h-12 rounded-xl bg-gray-200" />
                  <div className="flex-1 space-y-2">
                    <div className="h-3 w-32 bg-gray-200 rounded" />
                    <div className="h-3 w-48 bg-gray-200 rounded" />
                  </div>
                </div>
              ))}

            {!loading && matches && matches.length === 0 && (
              <p className="text-sm text-gray-600">No matches returned. Try broadening your skills or goals.</p>
            )}

            {!loading && matches && matches.length > 0 &&
              matches.map((m, idx) => (
                <div key={`${m.name}-${idx}`} className="flex items-start gap-4 p-4 rounded-xl bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all duration-200">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${GRADIENTS[idx % GRADIENTS.length]} flex items-center justify-center text-white font-semibold shadow-lg`}>
                    {getInitials(m.name)}
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-gray-900 font-medium">{m.name}</p>
                        {m.experienceLevel && (
                          <p className="text-gray-500 text-sm">{m.experienceLevel} • Ideal collaborator</p>
                        )}
                      </div>
                      <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                        {m.compatibility}% match
                      </span>
                    </div>
                    <p className="text-gray-700 text-sm">{m.reason}</p>
                    {m.skills && m.skills.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {m.skills.slice(0, 4).map((s, i) => (
                          <span key={`${s}-${i}`} className="bg-white border text-gray-700 border-gray-200 px-2 py-0.5 rounded-full text-xs">
                            {s}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

