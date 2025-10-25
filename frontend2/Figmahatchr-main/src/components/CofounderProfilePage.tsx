import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";

export default function CofounderProfilePage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [bio, setBio] = useState("");
  const [role, setRole] = useState("");
  const [skills, setSkills] = useState("");
  const [interests, setInterests] = useState("");
  const [availability, setAvailability] = useState("");
  const [workStyle, setWorkStyle] = useState("");
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
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
    setSaved(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 px-6 py-12 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-24 right-24 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob" />
        <div className="absolute bottom-24 left-24 w-72 h-72 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000" />
      </div>
      <div className="max-w-3xl mx-auto relative z-10">
        <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
          <CardHeader>
            <CardTitle className="text-slate-900">Create Your Cofounder Profile</CardTitle>
            <CardDescription>Tell others about your background and preferences</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3">
              <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
              <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <textarea className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Bio" value={bio} onChange={(e) => setBio(e.target.value)} />
              <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Role" value={role} onChange={(e) => setRole(e.target.value)} />
              <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Skills (comma-separated)" value={skills} onChange={(e) => setSkills(e.target.value)} />
              <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Interests (comma-separated)" value={interests} onChange={(e) => setInterests(e.target.value)} />
              <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Availability (comma-separated)" value={availability} onChange={(e) => setAvailability(e.target.value)} />
              <input className="px-3 py-2 border border-slate-200 rounded-lg" placeholder="Work Style (comma-separated)" value={workStyle} onChange={(e) => setWorkStyle(e.target.value)} />
              <Button onClick={handleSave} className="w-full">Save Profile</Button>
              {saved && <div className="text-sm text-green-700 bg-green-50 border border-green-200 rounded p-2">Profile saved! Go to Explore to find matches.</div>}
            </div>
          </CardContent>
        </Card>
      </div>
      <style>{`
        @keyframes blob { 0%,100%{ transform: translate(0,0) scale(1);} 33%{ transform: translate(30px,-50px) scale(1.1);} 66%{ transform: translate(-20px,20px) scale(0.9);} }
        .animate-blob { animation: blob 7s infinite; }
        .animation-delay-2000 { animation-delay: 2s; }
      `}</style>
    </div>
  );
}

