import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hatchr - Startup-as-a-Service",
  description: "Build a startup from a single idea",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <div className="min-h-screen bg-white text-gray-900">
          {/* Header */}
          <header className="border-b border-gray-200">
            <div className="max-w-3xl mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl font-bold">Hatchr</h1>
                </div>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                Build a startup from a single idea
              </p>
            </div>
          </header>

          {/* Main Content */}
          <main className="max-w-3xl mx-auto px-6 py-12">
            {children}
          </main>

          {/* Footer */}
          <footer className="border-t border-gray-200 mt-20">
            <div className="max-w-3xl mx-auto px-6 py-6">
              <p className="text-sm text-gray-500">
                © 2025 Hatchr. Privacy & Terms.
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
