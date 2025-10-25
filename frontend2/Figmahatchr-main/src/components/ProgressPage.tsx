import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Progress } from "./ui/progress";
import { Badge } from "./ui/badge";
import { CheckCircle2, Loader2, Download, ExternalLink, Sparkles, Search, Code2, Package } from "lucide-react";
import { api } from "../api";

type Step = {
  id: number;
  label: string;
  description: string;
  icon: React.ReactNode;
  status: "pending" | "processing" | "complete";
};

export function ProgressPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const jobIdFromUrl = params.get("jobId") || sessionStorage.getItem("currentJobId") || "";
  const [steps, setSteps] = useState<Step[]>([
    { 
      id: 1, 
      label: "Finding competitors", 
      description: "Analyzing market and discovering opportunities",
      icon: <Search className="w-5 h-5" />,
      status: "pending" 
    },
    { 
      id: 2, 
      label: "Building MVP", 
      description: "Generating your product architecture",
      icon: <Code2 className="w-5 h-5" />,
      status: "pending" 
    },
    { 
      id: 3, 
      label: "Packaging startup", 
      description: "Creating launch materials and resources",
      icon: <Package className="w-5 h-5" />,
      status: "pending" 
    },
  ]);
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [projectId, setProjectId] = useState<string | null>(null);
  const isVerified = sessionStorage.getItem("isVerified") === "true";

  useEffect(() => {
    // Set a placeholder project name from prompt for the header
    const prompt = sessionStorage.getItem("startupPrompt") || "";
    const name = generateProjectName(prompt);
    setProjectName(name);
    sessionStorage.setItem("projectName", name);

    if (!jobIdFromUrl) return;

    // Poll backend for real status
    const interval = setInterval(async () => {
      try {
        const status = await api.getStatus(jobIdFromUrl);
        // map backend step statuses
        setSteps((prev) =>
          prev.map((s, idx) => {
            const srv = status.steps[idx];
            if (!srv) return s;
            const map: any = { pending: "pending", in_progress: "processing", completed: "complete" };
            return { ...s, status: map[srv.status] || s.status };
          })
        );
        setProgress(status.progress);
        if (status.project_name) setProjectName(status.project_name);
        if (status.status === "completed") {
          clearInterval(interval);
          setIsComplete(true);
          if (status.project_id) {
            setProjectId(status.project_id);
            sessionStorage.setItem("currentProjectId", status.project_id);
          }
        }
      } catch (e) {
        // keep polling; optionally show a soft error message
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobIdFromUrl]);

  const generateProjectName = (prompt: string): string => {
    // Simple logic to generate a name from the prompt
    if (prompt.toLowerCase().includes("airbnb")) return "PetStay";
    if (prompt.toLowerCase().includes("uber")) return "RideShare Pro";
    if (prompt.toLowerCase().includes("netflix")) return "StreamVault";
    
    // Default names
    const defaultNames = ["StartupHub", "LaunchPad", "BuildFast", "IdeaForge"];
    return defaultNames[Math.floor(Math.random() * defaultNames.length)];
  };

  const handleLaunch = () => {
    const id = projectId || sessionStorage.getItem("currentProjectId");
    if (id) navigate(`/launch?projectId=${encodeURIComponent(id)}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center px-6 py-12 relative overflow-hidden">
      {/* Decorative Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 right-20 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute bottom-20 left-20 w-72 h-72 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className="max-w-[700px] w-full space-y-6 relative z-10">
        <div className="text-center space-y-3">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl shadow-lg mb-4">
            <Sparkles className="w-8 h-8 text-white animate-pulse" />
          </div>
          <h1 className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Generating Your Startup</h1>
          <p className="text-slate-600">Analyzing, building, and packaging your idea...</p>
        </div>

        <Card className="p-8 space-y-8 bg-white/80 backdrop-blur-xl border-white/20 shadow-2xl">
          {/* Progress Bar */}
          <div className="space-y-3">
            <div className="relative">
              <Progress value={progress} className="h-3 bg-slate-100" />
              <div className="absolute top-0 left-0 h-3 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full transition-all duration-500" style={{ width: `${progress}%` }}></div>
            </div>
            <div className="flex items-center justify-between">
              <p className="text-slate-600">Progress</p>
              <p className="text-indigo-600">{Math.round(progress)}%</p>
            </div>
          </div>

          {/* Steps */}
          <div className="space-y-4">
            {steps.map((step, index) => (
              <div 
                key={step.id} 
                className={`flex items-start gap-4 p-4 rounded-xl transition-all duration-300 ${
                  step.status === "processing" 
                    ? "bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200 scale-105" 
                    : step.status === "complete"
                    ? "bg-green-50 border border-green-200"
                    : "bg-slate-50 border border-slate-200"
                }`}
              >
                <div className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-300 ${
                  step.status === "complete" 
                    ? "bg-green-500 text-white shadow-lg" 
                    : step.status === "processing"
                    ? "bg-gradient-to-br from-indigo-600 to-purple-600 text-white shadow-lg animate-pulse"
                    : "bg-slate-200 text-slate-400"
                }`}>
                  {step.status === "complete" && <CheckCircle2 className="w-5 h-5" />}
                  {step.status === "processing" && <Loader2 className="w-5 h-5 animate-spin" />}
                  {step.status === "pending" && step.icon}
                </div>
                <div className="flex-1">
                  <p className={`transition-colors ${
                    step.status === "complete" ? "text-green-900" :
                    step.status === "processing" ? "text-indigo-900" :
                    "text-slate-500"
                  }`}>
                    Step {step.id}: {step.label}
                  </p>
                  <p className={`transition-colors ${
                    step.status === "processing" ? "text-indigo-600" : "text-slate-500"
                  }`}>
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Success Card */}
          {isComplete && (
            <div className="pt-6 border-t border-slate-200 space-y-6 animate-in fade-in duration-500">
              <div className="text-center space-y-3 p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-100">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full mb-2">
                  <CheckCircle2 className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-slate-900">Startup Generated: {projectName}</h2>
                {isVerified && (
                  <Badge variant="outline" className="gap-1 bg-white/50 border-indigo-200 text-indigo-700">
                    <CheckCircle2 className="w-3 h-3" />
                    Concordium verified founder
                  </Badge>
                )}
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Button variant="outline" className="gap-2 border-slate-300 hover:bg-slate-50">
                  <Download className="w-4 h-4" />
                  Download
                </Button>
                <Button variant="outline" className="gap-2 border-slate-300 hover:bg-slate-50">
                  <ExternalLink className="w-4 h-4" />
                  Deploy to Vercel
                </Button>
              </div>

              <Button 
                onClick={handleLaunch} 
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-200" 
                size="lg"
              >
                Continue to Launch Guide
              </Button>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
