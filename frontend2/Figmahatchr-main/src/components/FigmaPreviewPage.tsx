import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { ExternalLink, Figma } from "lucide-react";
import { useMemo } from "react";

function buildEmbedUrl(raw?: string): string | null {
  if (!raw) return null;
  try {
    const encoded = encodeURIComponent(raw.trim());
    // If it's already an embed URL, just return it
    if (raw.includes("/embed?")) return raw;
    return `https://www.figma.com/embed?embed_host=share&url=${encoded}`;
  } catch {
    return null;
  }
}

export function FigmaPreviewPage() {
  const envUrl = import.meta.env.VITE_FIGMA_EMBED_URL;
  // Fallback to the file referenced in README
  const defaultFile = "https://www.figma.com/design/5szUENtKydvsGACvtY15Ht/Startup-Idea-Generator-Website";
  const iframeUrl = useMemo(() => buildEmbedUrl(envUrl || defaultFile), [envUrl]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 px-6 py-12">
      <div className="max-w-5xl mx-auto space-y-6">
        <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <div className="bg-gradient-to-br from-indigo-600 to-purple-600 p-2 rounded-lg">
                <Figma className="w-5 h-5 text-white" />
              </div>
              Figma Design Preview
            </CardTitle>
            <CardDescription>
              Live preview of your Figma file inside the app. Update VITE_FIGMA_EMBED_URL to point to your own file.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {iframeUrl ? (
              <div className="w-full overflow-hidden rounded-xl border">
                <iframe
                  title="Figma Embed"
                  className="w-full"
                  style={{ height: "75vh" }}
                  src={iframeUrl}
                  allowFullScreen
                />
              </div>
            ) : (
              <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-800">
                Unable to build Figma embed URL. Please set VITE_FIGMA_EMBED_URL to a public Figma file link.
              </div>
            )}
            <div className="mt-4 flex gap-3">
              <Button asChild variant="outline" className="gap-2">
                <a href={envUrl || defaultFile} target="_blank" rel="noreferrer">
                  <ExternalLink className="w-4 h-4" />
                  Open in Figma
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default FigmaPreviewPage;

