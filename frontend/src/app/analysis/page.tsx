import Link from 'next/link';

export default function AnalysisPage() {
  return (
    <div className="min-h-screen">
      <nav className="border-b border-slate-700/50 bg-surface-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-14">
          <Link href="/" className="text-xl font-semibold text-primary-500">Stock AI</Link>
          <Link href="/dashboard" className="text-slate-400 hover:text-white">Dashboard</Link>
        </div>
      </nav>
      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-white mb-4">Stock Analysis</h1>
        <p className="text-slate-400 mb-6">Select a stock from the Dashboard to view detailed analysis.</p>
        <Link href="/dashboard" className="btn-primary">Go to Dashboard</Link>
      </main>
    </div>
  );
}
