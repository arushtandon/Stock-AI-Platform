import Link from 'next/link';

export default function PortfolioPage() {
  return (
    <div className="min-h-screen">
      <nav className="border-b border-slate-700/50 bg-surface-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-14">
          <Link href="/" className="text-xl font-semibold text-primary-500">Stock AI</Link>
          <Link href="/dashboard" className="text-slate-400 hover:text-white">Dashboard</Link>
        </div>
      </nav>
      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-white mb-4">Portfolio</h1>
        <div className="card p-8 text-center text-slate-400">
          Track your selected recommendations here. Connect your subscription to sync picks.
        </div>
      </main>
    </div>
  );
}
