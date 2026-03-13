import Link from 'next/link';
import Image from 'next/image';

export default function PerformancePage() {
  return (
    <div className="min-h-screen">
      <nav className="border-b border-slate-700/50 bg-surface-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-14">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/safron-logo.svg" alt="Safron" width={120} height={40} className="h-8 w-auto" />
          </Link>
          <div className="flex gap-4">
            <Link href="/dashboard" className="text-slate-400 hover:text-white">Dashboard</Link>
            <Link href="/analysis" className="text-slate-400 hover:text-white">Analysis</Link>
            <Link href="/portfolio" className="text-slate-400 hover:text-white">Portfolio</Link>
            <Link href="/performance" className="text-white">Performance</Link>
            <Link href="/integrations" className="text-slate-400 hover:text-white">Integrations</Link>
          </div>
        </div>
      </nav>
      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-white mb-4">Performance</h1>
        <div className="card p-8">
          <p className="text-slate-400 mb-4">Historical performance of recommendations:</p>
          <ul className="text-slate-300 space-y-2">
            <li>Win rate</li>
            <li>Average return</li>
            <li>Max drawdown</li>
            <li>Equity curve &amp; monthly returns</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
