"use client";

import { useRouter } from "next/navigation";

type LaunchChannel = {
  name: string;
  description: string;
  priority: "high" | "medium" | "low";
};

export default function Launch() {
  const router = useRouter();

  const launchChannels: LaunchChannel[] = [
    {
      name: "Product Hunt",
      description: "Launch to tech-savvy early adopters",
      priority: "high",
    },
    {
      name: "IndieHackers",
      description: "Share with indie maker community",
      priority: "high",
    },
    {
      name: "Reddit (r/SideProject)",
      description: "Get feedback from builders",
      priority: "medium",
    },
    {
      name: "Twitter/X",
      description: "Build in public, share progress",
      priority: "medium",
    },
    {
      name: "LinkedIn",
      description: "Reach professional network",
      priority: "low",
    },
    {
      name: "Hacker News",
      description: "Show HN for technical audience",
      priority: "medium",
    },
  ];

  const handleRerun = () => {
    router.push("/");
  };

  const handleDownloadPlan = () => {
    // TODO: Export to Notion or download as markdown
    console.log("Downloading launch plan...");
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Startup overview */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-2">
          Your Startup: AI Scheduling Tool
        </h2>
        <p className="text-gray-600 mb-4">
          A smart scheduling platform for freelancers powered by AI
        </p>

        <div className="flex flex-wrap gap-2 mb-4">
          <span className="px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-700">
            Next.js
          </span>
          <span className="px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-700">
            Supabase
          </span>
          <span className="px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-700">
            Tailwind CSS
          </span>
          <span className="px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-700">
            TypeScript
          </span>
        </div>

        <div className="inline-flex items-center gap-2 bg-green-50 px-3 py-1 rounded-full border border-green-200">
          <span className="text-sm">✅</span>
          <span className="text-xs font-medium text-green-800">
            Concordium verified
          </span>
        </div>
      </div>

      {/* Marketing assets */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Marketing Assets</h3>
        <p className="text-sm text-gray-600 mb-4">
          Auto-generated pitch materials using Livepeer Daydream
        </p>

        <div className="space-y-3">
          {/* Video pitch */}
          <div className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl">🎬</span>
                  <h4 className="font-medium">Pitch Video</h4>
                </div>
                <p className="text-sm text-gray-600">
                  30-second promotional video
                </p>
              </div>
              <button className="px-3 py-1 text-sm font-medium text-gray-700 border border-gray-300 rounded hover:bg-gray-50 transition-colors">
                View
              </button>
            </div>
          </div>

          {/* Pitch deck */}
          <div className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl">📊</span>
                  <h4 className="font-medium">Pitch Deck</h4>
                </div>
                <p className="text-sm text-gray-600">
                  5-slide investor overview
                </p>
              </div>
              <button className="px-3 py-1 text-sm font-medium text-gray-700 border border-gray-300 rounded hover:bg-gray-50 transition-colors">
                Download
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Launch channels */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Recommended Launch Channels</h3>
          <button
            onClick={handleDownloadPlan}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Export Plan
          </button>
        </div>

        <div className="space-y-2">
          {launchChannels.map((channel, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-2 h-2 rounded-full ${channel.priority === "high"
                      ? "bg-red-500"
                      : channel.priority === "medium"
                        ? "bg-yellow-500"
                        : "bg-green-500"
                    }`}
                />
                <div>
                  <h4 className="font-medium text-sm">{channel.name}</h4>
                  <p className="text-xs text-gray-600">
                    {channel.description}
                  </p>
                </div>
              </div>
              <span
                className={`text-xs font-medium px-2 py-1 rounded ${channel.priority === "high"
                    ? "bg-red-50 text-red-700"
                    : channel.priority === "medium"
                      ? "bg-yellow-50 text-yellow-700"
                      : "bg-green-50 text-green-700"
                  }`}
              >
                {channel.priority}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Next steps */}
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-6">
        <h3 className="font-semibold mb-3">Next Steps</h3>
        <ol className="space-y-2 text-sm text-gray-700">
          <li className="flex gap-2">
            <span className="font-medium">1.</span>
            <span>Customize your generated app with branding and content</span>
          </li>
          <li className="flex gap-2">
            <span className="font-medium">2.</span>
            <span>Deploy to Vercel or your preferred hosting platform</span>
          </li>
          <li className="flex gap-2">
            <span className="font-medium">3.</span>
            <span>Share marketing materials on recommended channels</span>
          </li>
          <li className="flex gap-2">
            <span className="font-medium">4.</span>
            <span>Collect early user feedback and iterate</span>
          </li>
        </ol>

        <button
          onClick={handleRerun}
          className="w-full mt-6 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          ← Build Another Startup
        </button>
      </div>
    </div>
  );
}
