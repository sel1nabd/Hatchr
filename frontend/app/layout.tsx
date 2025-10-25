import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import NavTabs from "@/components/NavTabs";

export const metadata: Metadata = {
  title: "Hatchr - Startup-as-a-Service",
  description: "Build a startup from a single idea",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Replace with actual check: you will probably need a global context or persistent check for a real app
  // For demo, tabs will always show

  const loggedIn = true; // Placeholder for profile-created check (replace with actual condition)

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
              <NavTabs />
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
