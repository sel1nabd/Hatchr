import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { MessageCircle as ChatIcon } from "lucide-react";
import { api } from "../api";
import type { CofounderMatch } from "../types";

type Profile = {
  id: number;
  name: string;
  email: string;
  bio: string;
  role: string;
  skills: string[];
  startupInterests: string[];
  availability: string[];
  workStyle: string[];
};

export default function CofounderExplorePage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [matches, setMatches] = useState<CofounderMatch[] | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem("cofounderProfiles");
    setProfiles(raw ? (JSON.parse(raw) as Profile[]) : []);
    setLoading(false);
  }, []);

  async function findFor(profile: Profile) {
    setMatches(null);
    try {
      const payload = {
        name: profile.name,
        skills: profile.skills,
        goals: profile.bio || "",
        personality: profile.workStyle.join(", ") || "",
      };
      const res = await api.matchCofounders(payload);
      setMatches(res);
    } catch {
      setMatches([]);
    }
  }

  if (loading) return <div className="px-6 py-12 text-center">Loading…</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 px-6 py-12 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-24 right-24 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob" />
        <div className="absolute bottom-24 left-24 w-72 h-72 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000" />
      </div>

      <div className="max-w-6xl mx-auto relative z-10 space-y-6">
        <div className="text-center mb-4">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Explore Profiles</h1>
          <p className="text-slate-600">Saved profiles and recommended matches</p>
        </div>

        {profiles.length === 0 ? (
          <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl text-center p-8">
            <p className="text-slate-700">No profiles yet. Create one from the Cofounder Finder.</p>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {profiles.map((p) => (
              <Card key={p.id} className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
                <CardHeader>
                  <CardTitle className="text-slate-900">{p.name}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="text-sm text-slate-600">{p.role}</div>
                  <div className="text-sm text-slate-700 line-clamp-3">{p.bio}</div>
                  <div className="flex flex-wrap gap-1">
                    {p.skills.slice(0, 4).map((s, i) => (
                      <span key={`${s}-${i}`} className="px-2 py-0.5 rounded-full border text-xs bg-white">
                        {s}
                      </span>
                    ))}
                  </div>
                  <div className="flex justify-between items-center pt-2">
                    <div className="text-xs text-slate-500">{p.availability.join(", ")}</div>
                    <Button variant="outline" size="sm" onClick={() => findFor(p)} className="gap-1">
                      <ChatIcon className="w-4 h-4" />
                      Find Matches
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {matches && (
          <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
            <CardHeader>
              <CardTitle className="text-slate-900">Recommended Matches</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {matches.length === 0 && <p className="text-sm text-slate-600">No matches found.</p>}
              {matches.map((m, idx) => (
                <div key={`${m.name}-${idx}`} className="flex items-start gap-4 p-4 rounded-xl bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 text-white flex items-center justify-center font-semibold">
                    {m.name.split(' ').map((s)=>s[0]).slice(0,2).join('').toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-slate-900 font-medium">{m.name}</div>
                        {m.experienceLevel && <div className="text-xs text-slate-500">{m.experienceLevel}</div>}
                      </div>
                      <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">{m.compatibility}% match</span>
                    </div>
                    <div className="text-slate-700 text-sm mt-1">{m.summary}</div>
                  </div>
                </div>
              ))}
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
