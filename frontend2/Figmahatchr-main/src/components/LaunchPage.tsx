import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Sparkles, Code, Database, ArrowRight, Users, Megaphone, RefreshCw, Rocket, Copy, CheckCircle2, ExternalLink, AlertTriangle } from "lucide-react";
import { api } from "../api";
import type { CofounderMatch, CofounderRequest, ProjectResponse } from "../types";

const PROMOTION_CHANNELS = [
  { name: "Product Hunt", icon: "🚀" },
  { name: "Hacker News", icon: "📰" },
  { name: "IndieHackers", icon: "💡" },
  { name: "Reddit", icon: "🤖" },
  { name: "Twitter/X", icon: "🐦" },
  { name: "LinkedIn", icon: "💼" },
  { name: "Dev.to", icon: "👨‍💻" },
  { name: "Beta List", icon: "🎯" },
];

const GRADIENTS = [
  "from-indigo-500 to-purple-500",
  "from-blue-500 to-cyan-500",
  "from-teal-500 to-emerald-500",
  "from-orange-500 to-pink-500",
];

function getGradient(index: number): string {
  return GRADIENTS[index % GRADIENTS.length];
}

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((part) => part.trim()[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

function buildDemoProfile(projectName: string, prompt: string, isVerified: boolean, desiredRoles: string[]): CofounderRequest {
  const skills = new Set<string>(["Product Strategy", "Go-To-Market"]);
  const lowerPrompt = prompt.toLowerCase();

  if (lowerPrompt.includes("ai") || lowerPrompt.includes("machine learning")) {
    skills.add("AI");
    skills.add("ML");
  }
  if (lowerPrompt.includes("health") || lowerPrompt.includes("med")) {
    skills.add("Healthcare");
    skills.add("Compliance");
  }
  if (lowerPrompt.includes("fintech") || lowerPrompt.includes("finance") || lowerPrompt.includes("payments")) {
    skills.add("Fintech");
    skills.add("Risk");
  }
  if (lowerPrompt.includes("web3") || lowerPrompt.includes("blockchain")) {
    skills.add("Blockchain");
    skills.add("Smart Contracts");
  }
  if (lowerPrompt.includes("education") || lowerPrompt.includes("edtech")) {
    skills.add("Education");
    skills.add("Curriculum Design");
  }
  if (lowerPrompt.includes("saas") || lowerPrompt.includes("platform")) {
    skills.add("SaaS");
    skills.add("Platform Engineering");
  }
  if (lowerPrompt.includes("mobile")) {
    skills.add("Mobile");
    skills.add("UX");
  }
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
  desiredRoles.forEach((role) => {
    (ROLE_SKILL_MAP[role] || []).forEach((s) => skills.add(s));
  });

  if (skills.size === 0) {
    skills.add("Product");
  }

  const experienceLevel = isVerified ? "Senior" : "Mid-Level";
  const personality = isVerified
    ? "Trusted, execution-focused founder looking for complementary skills"
    : "Curious, collaborative builder seeking a partner to accelerate launch";

  const goals = prompt.trim().length > 0 ? prompt : `Launch ${projectName} to market`;

  return {
    name: `${projectName} Founder`,
    skills: Array.from(skills),
    goals,
    personality,
    experienceLevel,
  };
}

export function LaunchPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const projectId = params.get("projectId") || sessionStorage.getItem("currentProjectId") || "";
  const [project, setProject] = useState<ProjectResponse | null>(null);
  const prompt = sessionStorage.getItem("startupPrompt") || "";
  const isVerified = sessionStorage.getItem("isVerified") === "true";
  const desiredRoles: string[] = (() => {
    try {
      const raw = sessionStorage.getItem("desiredRoles");
      return raw ? (JSON.parse(raw) as string[]) : [];
    } catch {
      return [];
    }
  })();
  const [copied, setCopied] = useState(false);
  const [matches, setMatches] = useState<CofounderMatch[] | null>(null);
  const [loadingMatches, setLoadingMatches] = useState<boolean>(true);
  const [matchError, setMatchError] = useState<string | null>(null);

<<<<<<< HEAD
  // Fetch real project data from backend
  useEffect(() => {
    const projectId = sessionStorage.getItem("projectId");
    if (!projectId) {
      setLoadingProject(false);
      return;
    }

    const fetchProject = async () => {
      try {
        const data = await api.getProject(projectId);
        setProjectData(data);
      } catch (error) {
        console.error("Failed to fetch project:", error);
        setProjectError("Could not load project data");
      } finally {
        setLoadingProject(false);
      }
    };

    fetchProject();
  }, []);

  const founderProfile = useMemo(() => buildDemoProfile(project?.project_name || "Your Startup", prompt, isVerified, desiredRoles), [project, prompt, isVerified, desiredRoles]);
=======
  const founderProfile = useMemo(() => buildDemoProfile(project?.project_name || "Your Startup", prompt, isVerified, desiredRoles), [project, prompt, isVerified, desiredRoles]);
>>>>>>> d2d5a3e (feat(frontend2): integrate full backend functionality (generate→status polling→launch), lovable link, and local cofounder fallback; aligns with Next features)

  useEffect(() => {
    // Load project details
    async function loadProject() {
      if (!projectId) return;
      try {
        const data = await api.getProject(projectId);
        setProject(data);
        sessionStorage.setItem("projectName", data.project_name);
      } catch (e) {
        // ignore, keep basic view
      }
    }
    loadProject();

    let cancelled = false;
    setLoadingMatches(true);
    setMatchError(null);

    const loadMatches = async () => {
      try {
        const recommendations = await api.matchCofounders(founderProfile);
        if (!cancelled) {
          setMatches(recommendations);
        }
      } catch (error) {
        console.error("Failed to fetch cofounder matches", error);
        if (!cancelled) {
          setMatchError("Unable to load matches right now. Try again soon.");
          setMatches([]);
        }
      } finally {
        if (!cancelled) {
          setLoadingMatches(false);
        }
      }
    };

    loadMatches();

    return () => {
      cancelled = true;
    };
  }, [founderProfile, projectId]);

  const handleReRun = () => {
    navigate("/");
  };

  const handleCopyPlan = () => {
    const cofounderSection =
      matches && matches.length > 0
        ? matches.map((match) => `• ${match.name} (${match.compatibility}%): ${match.summary}`).join("\n")
        : "• Matches are being prepared — check the dashboard soon.";

    const plan = `Launch Plan for ${project?.project_name || sessionStorage.getItem("projectName") || "Your Startup"}

Cofounder Matches:
${cofounderSection}

Promotion Channels:
${PROMOTION_CHANNELS.map((channel) => `• ${channel.name}`).join("\n")}

Stack:
${(project?.stack || ["Next.js", "TypeScript", "Tailwind CSS", "Supabase"]).map((tech) => `• ${tech}`).join("\n")}
• Deployment: Vercel

Next Steps:
1. Polish your MVP based on user feedback
2. Reach out to potential cofounders
3. Start promoting on recommended channels
4. Set up analytics and feedback loops
`;
    navigator.clipboard.writeText(plan);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 px-6 py-12 relative overflow-hidden">
      {/* Decorative Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-40 right-40 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute bottom-40 left-40 w-96 h-96 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
      </div>

      <div className="max-w-[700px] mx-auto space-y-8 relative z-10">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-500 rounded-3xl shadow-2xl mb-4 animate-bounce">
            <Rocket className="w-10 h-10 text-white" />
          </div>
          <div>
            <h1 className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">Your Startup is Ready!</h1>
            <p className="text-slate-600">Here's your roadmap to launch</p>
          </div>
        </div>

        {/* Overview Card */}
        <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl overflow-hidden">
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6">
            <CardTitle className="text-white mb-2">{project?.project_name || sessionStorage.getItem("projectName") || "Your Startup"}</CardTitle>
            <CardDescription className="text-indigo-100">{prompt || project?.tagline}</CardDescription>
          </div>
          <CardContent className="pt-6 space-y-4">
            {/* Live backend section removed to simplify launch view */}
            <div className="space-y-3">
              <p className="text-slate-700">Tech Stack</p>
              <div className="flex flex-wrap gap-2">
<<<<<<< HEAD
                {projectData?.tech_stack ? (
                  projectData.tech_stack.map((tech: string, idx: number) => (
                    <Badge key={idx} variant="secondary" className="gap-1 bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200 text-blue-700">
                      <Code className="w-3 h-3" />
                      {tech}
                    </Badge>
                  ))
                ) : (
                  <>
                    <Badge variant="secondary" className="gap-1 bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200 text-blue-700">
                      <Code className="w-3 h-3" />
                      FastAPI
                    </Badge>
                    <Badge variant="secondary" className="gap-1 bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200 text-purple-700">
                      <Database className="w-3 h-3" />
                      SQLite
                    </Badge>
                  </>
                )}
=======
                {(project?.stack || ["Next.js", "TypeScript", "Tailwind CSS", "Supabase"]).map((tech) => (
                  <Badge key={tech} variant="secondary" className="gap-1 bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200 text-blue-700">
                    {tech}
                  </Badge>
                ))}
>>>>>>> d2d5a3e (feat(frontend2): integrate full backend functionality (generate→status polling→launch), lovable link, and local cofounder fallback; aligns with Next features)
              </div>
          </div>
        </CardContent>
      </Card>

        {/* Cofounder Suggestions */}
        <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-slate-900">
              <div className="bg-gradient-to-br from-indigo-600 to-purple-600 p-2 rounded-lg">
                <Users className="w-5 h-5 text-white" />
              </div>
              Cofounder Suggestions
            </CardTitle>
            <CardDescription>
              Demo recommendations generated by Hatchr AI using your founder profile
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {loadingMatches && (
              <>
                {Array.from({ length: 3 }).map((_, index) => (
                  <div
                    key={`skeleton-${index}`}
                    className="flex items-start gap-4 p-4 rounded-xl border border-slate-200 bg-white/60 animate-pulse"
                  >
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
              <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                {matchError}
              </div>
            )}

            {!loadingMatches && !matchError && matches && matches.length === 0 && (
              <p className="text-sm text-slate-600">
                We saved your profile. Check back shortly for curated cofounder suggestions.
              </p>
            )}

            {!loadingMatches &&
              !matchError &&
              matches &&
              matches.length > 0 &&
              matches.map((match, index) => (
                <div
                  key={`${match.name}-${index}`}
                  className="flex items-start gap-4 p-4 rounded-xl bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200 hover:border-indigo-300 hover:shadow-md transition-all duration-200 group"
                >
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${getGradient(index)} flex items-center justify-center shadow-lg`}>
                    <span className="text-white">{getInitials(match.name)}</span>
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-slate-900 font-medium">{match.name}</p>
                        {match.experienceLevel && (
                          <p className="text-slate-500 text-sm">{match.experienceLevel} • Ideal collaborator</p>
                        )}
                      </div>
                      <Badge variant="secondary" className="bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200 text-indigo-700">
                        {match.compatibility}% match
                      </Badge>
                    </div>
                    <p className="text-slate-600 text-sm">{match.summary}</p>
                    {match.sharedSkills.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {match.sharedSkills.map((skill) => (
                          <Badge key={skill} variant="outline" className="bg-white/50">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                  <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              ))}
          </CardContent>
        </Card>

        {/* Promotion Channels */}
        <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-slate-900">
              <div className="bg-gradient-to-br from-orange-500 to-red-500 p-2 rounded-lg">
                <Megaphone className="w-5 h-5 text-white" />
              </div>
              Recommended Promotion Channels
            </CardTitle>
            <CardDescription>
              Where to launch and get your first users
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {PROMOTION_CHANNELS.map((channel) => (
                <div
                  key={channel.name}
                  className="p-4 rounded-xl bg-gradient-to-br from-white to-slate-50 border border-slate-200 hover:border-indigo-300 hover:shadow-md transition-all duration-200 text-center group cursor-pointer"
                >
                  <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">{channel.icon}</div>
                  <p className="text-slate-700">{channel.name}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="grid grid-cols-2 gap-4">
          <Button 
            onClick={handleCopyPlan} 
            variant="outline" 
            className="gap-2 bg-white/50 backdrop-blur-sm border-slate-300 hover:bg-white hover:border-indigo-300 hover:shadow-md transition-all"
          >
            {copied ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                Copy Launch Plan
              </>
            )}
          </Button>
          <Button 
            onClick={handleReRun} 
            variant="outline" 
            className="gap-2 bg-white/50 backdrop-blur-sm border-slate-300 hover:bg-white hover:border-indigo-300 hover:shadow-md transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            New Startup
          </Button>
        </div>

        {/* CTA */}
        <Card className="bg-gradient-to-r from-indigo-600 to-purple-600 border-0 shadow-2xl overflow-hidden">
          <CardContent className="p-8 text-center space-y-4">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Sparkles className="w-6 h-6 text-white" />
              <h3 className="text-white">Ready to Launch?</h3>
            </div>
            <p className="text-indigo-100">
              Your startup package is ready. Start building your dream today.
            </p>
            <Button 
              onClick={async () => {
                if (!projectId) return;
                try {
                  const data = await api.getLovableUrl(projectId);
                  window.open(data.lovable_url, "_blank");
                } catch {}
              }}
              variant="secondary" 
              className="gap-2 bg-white hover:bg-slate-50 text-indigo-600 shadow-lg"
              size="lg"
            >
              <ExternalLink className="w-4 h-4" />
              Build on Lovable
            </Button>
          </CardContent>
        </Card>
      </div>

      <style>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
      `}</style>
    </div>
  );
}
