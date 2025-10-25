import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Users, Sparkles, ArrowRight } from "lucide-react";
import { api } from "../api";
import type { CofounderMatch, CofounderRequest } from "../types";

export function CofounderFinderPage() {
  const navigate = useNavigate();
  const [tab, setTab] = useState<"quick" | "detailed">("quick");
  const [form, setForm] = useState<CofounderRequest>({
    name: "",
    skills: [],
    goals: "",
    personality: "",
    experienceLevel: "Mid-Level",
  });
  const [inputSkills, setInputSkills] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [matches, setMatches] = useState<CofounderMatch[] | null>(null);

  const parseSkills = (text: string) =>
    text
      .split(/[,|\n]/)
      .map((s) => s.trim())
      .filter(Boolean);

  const handleFind = async () => {
    setLoading(true);
    setError(null);
    setMatches(null);
    try {
      const payload: CofounderRequest = {
        ...form,
        skills: form.skills.length ? form.skills : parseSkills(inputSkills),
      };
      const res = await api.matchCofounders(payload);
      setMatches(res);
    } catch (e: any) {
      setError(e?.message || "Unable to fetch matches");
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  const GRADIENTS = [
    "from-indigo-500 to-purple-500",
    "from-blue-500 to-cyan-500",
    "from-teal-500 to-emerald-500",
    "from-orange-500 to-pink-500",
  ];

  const initials = (name: string) =>
    name
      .split(" ")
      .map((s) => s[0])
      .filter(Boolean)
      .slice(0, 2)
      .join("")
      .toUpperCase();

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 px-6 py-12 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-24 right-24 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob" />
        <div className="absolute bottom-24 left-24 w-72 h-72 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000" />
      </div>

      <div className="max-w-4xl mx-auto relative z-10 space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Find Your Perfect Cofounder</h1>
          <p className="text-slate-600">Connect with complementary founders who share your vision</p>
        </div>

        <div className="flex justify-center">
          <div className="bg-white/80 backdrop-blur-xl rounded-lg border border-white/20 shadow-sm p-1">
            <button
              onClick={() => setTab("quick")}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                tab === "quick" ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow" : "text-gray-700 hover:text-gray-900"
              }`}
            >
              Quick Match
            </button>
            <button
              onClick={() => setTab("detailed")}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                tab === "detailed" ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow" : "text-gray-700 hover:text-gray-900"
              }`}
            >
              Detailed Profile
            </button>
          </div>
        </div>

        {tab === "quick" && (
          <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-slate-900">
                <div className="bg-gradient-to-br from-indigo-600 to-purple-600 p-2 rounded-lg">
                  <Users className="w-5 h-5 text-white" />
                </div>
                Quick Match
              </CardTitle>
              <CardDescription>Enter a few details to get instant matches</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-3">
                <div>
                  <label className="text-sm font-medium text-slate-800">Your Name</label>
                  <input
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    placeholder="Jane Smith"
                    className="mt-1 w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-800">Experience</label>
                  <select
                    value={form.experienceLevel}
                    onChange={(e) => setForm({ ...form, experienceLevel: e.target.value })}
                    className="mt-1 w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  >
                    <option>Entry</option>
                    <option>Mid-Level</option>
                    <option>Senior</option>
                    <option>Serial Founder</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-800">Skills</label>
                <input
                  value={inputSkills}
                  onChange={(e) => setInputSkills(e.target.value)}
                  placeholder="AI, React, Growth"
                  className="mt-1 w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-800">Goals</label>
                <input
                  value={form.goals}
                  onChange={(e) => setForm({ ...form, goals: e.target.value })}
                  placeholder="Launch an AI tool"
                  className="mt-1 w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-800">Personality & Working Style</label>
                <input
                  value={form.personality}
                  onChange={(e) => setForm({ ...form, personality: e.target.value })}
                  placeholder="Collaborative, fast-paced, data-informed"
                  className="mt-1 w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
              </div>
              <div className="flex gap-3">
                <Button onClick={handleFind} disabled={loading} className="gap-2">
                  {loading ? "Finding…" : <>Find Matches <ArrowRight className="w-4 h-4" /></>}
                </Button>
                <Button variant="outline" onClick={() => navigate("/cofounder/profile")}>Create Profile</Button>
                <Button variant="outline" onClick={() => navigate("/cofounder/explore")}>Explore</Button>
              </div>

              {(loading || matches || error) && (
                <div className="mt-4 space-y-3">
                  {loading && (
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
                  {!loading && error && (
                    <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">{error}</div>
                  )}
                  {!loading && !error && matches && matches.length === 0 && (
                    <p className="text-sm text-slate-600">No matches returned. Try broadening your skills or goals.</p>
                  )}
                  {!loading && !error && matches && matches.length > 0 && matches.map((m, idx) => (
                    <div key={`${m.name}-${idx}`} className="flex items-start gap-4 p-4 rounded-xl bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${GRADIENTS[idx % GRADIENTS.length]} flex items-center justify-center text-white font-semibold`}>
                        {initials(m.name)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-slate-900 font-medium">{m.name}</div>
                            {m.experienceLevel && <div className="text-xs text-slate-500">{m.experienceLevel}</div>}
                          </div>
                          <Badge variant="secondary" className="bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200 text-indigo-700">{m.compatibility}% match</Badge>
                        </div>
                        <div className="text-slate-700 text-sm mt-1">{m.summary}</div>
                        {m.sharedSkills && m.sharedSkills.length > 0 && (
                          <div className="mt-1 flex flex-wrap gap-1">
                            {m.sharedSkills.slice(0, 4).map((s) => (
                              <Badge key={s} variant="outline" className="bg-white/50">{s}</Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {tab === "detailed" && (
          <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
            <CardHeader>
              <CardTitle className="text-slate-900">Create Your Cofounder Profile</CardTitle>
              <CardDescription>Save a profile to explore and match later</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Simplified detailed form saved to localStorage */}
              <DetailedProfileForm onSaved={() => navigate("/cofounder/explore")} />
            </CardContent>
          </Card>
        )}
      </div>

      <style>{`
        @keyframes blob { 0%,100%{ transform: translate(0,0) scale(1);} 33%{ transform: translate(30px,-50px) scale(1.1);} 66%{ transform: translate(-20px,20px) scale(0.9);} }
        .animate-blob { animation: blob 7s infinite; }
        .animation-delay-2000 { animation-delay: 2s; }
      `}</style>
    </div>
  );
}

function DetailedProfileForm({ onSaved }: { onSaved: () => void }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [bio, setBio] = useState("");
  const [role, setRole] = useState("");
  const [skills, setSkills] = useState("");
  const [interests, setInterests] = useState("");
  const [availability, setAvailability] = useState("");
  const [workStyle, setWorkStyle] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSave = () => {
    setSaving(true);
    const profile = {
      id: Date.now(),
      name,
      email,
      bio,
      role,
      skills: skills.split(/[,|\n]/).map((s) => s.trim()).filter(Boolean),
      startupInterests: interests.split(/[,|\n]/).map((s) => s.trim()).filter(Boolean),
      availability: availability.split(/[,|\n]/).map((s) => s.trim()).filter(Boolean),
      workStyle: workStyle.split(/[,|\n]/).map((s) => s.trim()).filter(Boolean),
    };
    const raw = localStorage.getItem("cofounderProfiles");
    const arr = raw ? (JSON.parse(raw) as any[]) : [];
    arr.push(profile);
    localStorage.setItem("cofounderProfiles", JSON.stringify(arr));
    setSaving(false);
    onSaved();
  };

  return (
    <div className="grid gap-3">
      <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
      <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <textarea className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Bio" value={bio} onChange={(e) => setBio(e.target.value)} />
      <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Role" value={role} onChange={(e) => setRole(e.target.value)} />
      <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Skills (comma-separated)" value={skills} onChange={(e) => setSkills(e.target.value)} />
      <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Interests (comma-separated)" value={interests} onChange={(e) => setInterests(e.target.value)} />
      <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Availability (comma-separated)" value={availability} onChange={(e) => setAvailability(e.target.value)} />
      <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Work Style (comma-separated)" value={workStyle} onChange={(e) => setWorkStyle(e.target.value)} />
      <Button onClick={handleSave} disabled={saving} className="w-full">{saving ? "Saving…" : "Save Profile"}</Button>
    </div>
  );
}

export default CofounderFinderPage;

