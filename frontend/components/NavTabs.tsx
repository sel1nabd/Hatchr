"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { href: "/", label: "Main App" },
  { href: "/cofounder", label: "Find Co-Founder" }
];

export default function NavTabs() {
  const pathname = usePathname();
  return (
    <nav className="mt-6 flex gap-4 border-b border-gray-100 pb-2">
      {tabs.map(tab => (
        <Link
          key={tab.href}
          href={tab.href}
          className={`py-2 px-4 rounded-t-lg font-medium text-sm transition-colors ${pathname === tab.href ? "bg-gray-100 text-gray-900" : "text-gray-500 hover:text-gray-900 hover:bg-gray-100"}`}
        >
          {tab.label}
        </Link>
      ))}
    </nav>
  );
}
