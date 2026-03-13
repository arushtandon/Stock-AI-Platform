import Link from 'next/link';
import Image from 'next/image';
import { BarChart3, TrendingUp, Shield, Key } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <nav className="border-b border-slate-700/50 bg-surface-900/50 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-14">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/safron-logo.svg" alt="Safron" width={120} height={40} priority className="h-8 w-auto" />
          </Link>
          <div className="flex gap-4">
            <Link href="/dashboard" className="text-slate-300 hover:text-white">Dashboard</Link>
            <Link href="/analysis" className="text-slate-300 hover:text-white">Analysis</Link>
            <Link href="/portfolio" className="text-slate-300 hover:text-white">Portfolio</Link>
            <Link href="/performance" className="text-slate-300 hover:text-white">Performance</Link>
            <Link href="/integrations" className="text-slate-300 hover:text-white flex items-center gap-1">
              <Key className="w-4 h-4" /> Integrations
            </Link>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-16">
        <p className="text-primary-500 font-medium mb-2">Internal use only</p>
        <h1 className="text-4xl font-bold text-white mb-4">
          Safron Stock Recommendation Model
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl mb-6">
          Internal company platform that aggregates analysis from top research sources—Danelfin, Seeking Alpha Premium, Investing.com Pro, and TradingView—to produce daily top 20 stock recommendations and risk metrics.
        </p>
        <p className="text-slate-500 text-sm max-w-2xl mb-12">
          Add your premium API credentials in <Link href="/integrations" className="text-primary-500 hover:underline">Integrations</Link> (or in Render → stock-ai-api → Environment) to pull live data. Without credentials, the system uses demo data for rankings.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {[
            { icon: BarChart3, title: 'Multi-Source Ranking', desc: 'Danelfin, Seeking Alpha, Investing Pro, TradingView' },
            { icon: TrendingUp, title: 'Top 20 Daily Picks', desc: 'Entry, stop loss, take profit per pick' },
            { icon: Shield, title: 'Risk Management', desc: 'ATR-based stops, volatility, drawdown' },
            { icon: Key, title: 'Premium Credentials', desc: 'Configure API keys for all 4 sources' },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card p-6">
              <Icon className="w-10 h-10 text-primary-500 mb-3" />
              <h3 className="font-semibold text-white mb-1">{title}</h3>
              <p className="text-slate-400 text-sm">{desc}</p>
            </div>
          ))}
        </div>
        <div className="flex gap-4">
          <Link href="/dashboard" className="btn-primary inline-flex items-center gap-2">
            View Dashboard
          </Link>
          <Link href="/integrations" className="px-4 py-2 rounded-lg border border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white inline-flex items-center gap-2">
            <Key className="w-4 h-4" /> Configure credentials
          </Link>
        </div>
      </main>
    </div>
  );
}
