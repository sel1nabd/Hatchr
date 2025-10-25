import { NavLink, useNavigate } from "react-router-dom";
import { Rocket, Users, Search, UserPlus, LayoutGrid } from "lucide-react";

function cls(...parts: Array<string | false | undefined>) {
  return parts.filter(Boolean).join(" ");
}

export default function HeaderNav() {
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-30 bg-white/70 backdrop-blur-xl border-b border-white/30">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <button className="flex items-center gap-2" onClick={() => navigate("/")}> 
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow">
            <Rocket className="w-4 h-4" />
          </div>
          <span className="font-semibold text-slate-900">HatchR</span>
        </button>
        <nav className="flex items-center gap-2">
          <NavLink
            to="/"
            className={({ isActive }) =>
              cls(
                "px-3 py-1.5 rounded-md text-sm font-medium",
                isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
              )
            }
          >
            Generator
          </NavLink>
          <NavLink
            to="/cofounder"
            className={({ isActive }) =>
              cls(
                "px-3 py-1.5 rounded-md text-sm font-medium flex items-center gap-1",
                isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
              )
            }
          >
            <Users className="w-4 h-4" /> Finder
          </NavLink>
          <NavLink
            to="/cofounder/explore"
            className={({ isActive }) =>
              cls(
                "px-3 py-1.5 rounded-md text-sm font-medium flex items-center gap-1",
                isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
              )
            }
          >
            <Search className="w-4 h-4" /> Explore
          </NavLink>
          <NavLink
            to="/cofounder/profile"
            className={({ isActive }) =>
              cls(
                "px-3 py-1.5 rounded-md text-sm font-medium flex items-center gap-1",
                isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
              )
            }
          >
            <UserPlus className="w-4 h-4" /> Profile
          </NavLink>
          <NavLink
            to="/figma"
            className={({ isActive }) =>
              cls(
                "px-3 py-1.5 rounded-md text-sm font-medium flex items-center gap-1",
                isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
              )
            }
          >
            <LayoutGrid className="w-4 h-4" /> Figma
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

