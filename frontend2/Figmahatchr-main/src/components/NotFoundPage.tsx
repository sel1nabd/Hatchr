import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center px-6">
      <div className="text-center space-y-3">
        <div className="text-6xl">😕</div>
        <h1 className="text-xl font-semibold text-slate-900">Page not found</h1>
        <p className="text-slate-600">The page you’re looking for doesn’t exist.</p>
        <div className="pt-3">
          <Link to="/" className="px-4 py-2 bg-slate-900 text-white rounded-md text-sm">Back to Generator</Link>
        </div>
      </div>
    </div>
  );
}

