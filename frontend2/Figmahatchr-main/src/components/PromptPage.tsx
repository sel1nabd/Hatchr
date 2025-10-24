import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";
import { Switch } from "./ui/switch";
import { Label } from "./ui/label";
import { Sparkles, Zap, TrendingUp, Rocket } from "lucide-react";

export function PromptPage() {
  const [prompt, setPrompt] = useState("");
  const [isVerified, setIsVerified] = useState(false);
  const navigate = useNavigate();

  const handleGenerate = () => {
    if (prompt.trim()) {
      // Store the prompt and verified status in sessionStorage
      sessionStorage.setItem("startupPrompt", prompt);
      sessionStorage.setItem("isVerified", String(isVerified));
      navigate("/generate");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex flex-col relative overflow-hidden">
      {/* Decorative Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      {/* Header */}
      <header className="w-full py-8 px-6 relative z-10">
        <div className="max-w-[700px] mx-auto">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-gradient-to-br from-indigo-600 to-purple-600 p-2 rounded-xl shadow-lg">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <h1 className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">HatchR</h1>
          </div>
          <p className="text-slate-700">Build a startup from a single idea.</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 px-6 py-12 relative z-10">
        <div className="max-w-[700px] mx-auto space-y-8">
          {/* Main Card */}
          <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/20 p-8 space-y-6">
            <div className="space-y-2">
              <Label htmlFor="prompt" className="text-slate-900">Describe what you want to build</Label>
              <Textarea
                id="prompt"
                placeholder="e.g., 'Airbnb for pets'"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="min-h-[180px] resize-none text-lg bg-white/50 border-slate-200 focus:border-indigo-400 focus:ring-indigo-400/20 rounded-xl"
              />
              <p className="text-slate-500">Be as specific or creative as you'd like</p>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100">
              <div className="flex items-center space-x-3">
                <div className="bg-white p-2 rounded-lg shadow-sm">
                  <Zap className="w-5 h-5 text-indigo-600" />
                </div>
                <div>
                  <Label htmlFor="verified" className="cursor-pointer text-slate-900">
                    Verified Founder
                  </Label>
                  <p className="text-slate-600">Uses Concordium blockchain</p>
                </div>
              </div>
              <Switch
                id="verified"
                checked={isVerified}
                onCheckedChange={setIsVerified}
              />
            </div>

            <Button
              onClick={handleGenerate}
              disabled={!prompt.trim()}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-200"
              size="lg"
            >
              <Rocket className="w-5 h-5 mr-2" />
              Generate Startup
            </Button>
          </div>

          {/* Feature Pills */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 text-center border border-white/40 hover:bg-white/80 transition-all duration-200">
              <div className="bg-gradient-to-br from-blue-500 to-cyan-500 w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-2">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <p className="text-slate-700">Market Analysis</p>
            </div>
            <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 text-center border border-white/40 hover:bg-white/80 transition-all duration-200">
              <div className="bg-gradient-to-br from-purple-500 to-pink-500 w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-2">
                <Rocket className="w-5 h-5 text-white" />
              </div>
              <p className="text-slate-700">MVP Builder</p>
            </div>
            <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 text-center border border-white/40 hover:bg-white/80 transition-all duration-200">
              <div className="bg-gradient-to-br from-orange-500 to-red-500 w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-2">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <p className="text-slate-700">AI Powered</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full py-6 px-6 border-t border-white/30 relative z-10 bg-white/20 backdrop-blur-sm">
        <div className="max-w-[700px] mx-auto text-center text-slate-600">
          <p>Privacy · © 2025 HatchR</p>
        </div>
      </footer>

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
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}
