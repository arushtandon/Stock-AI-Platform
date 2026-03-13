import Link from 'next/link';
import { BarChart3, TrendingUp, Shield, Bell } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <nav className="border-b border-slate-700/50 bg-surface-900/50 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-14">
          <span className="text-xl font-semibold text-primary-500">Stock AI</span>
          <div className="flex gap-4">
            <Link href="/dashboard" className="text-slate-300 hover:text-white">Dashboard</Link>
            <Link href="/analysis" className="text-slate-300 hover:text-white">Analysis</Link>
            <Link href="/portfolio" className="text-slate-300 hover:text-white">Portfolio</Link>
            <Link href="/performance" className="text-slate-300 hover:text-white">Performance</Link>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-white mb-4">
          Cloud-Based Stock Analysis & Recommendations
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl mb-12">
          Aggregates insights from Danelfin, Seeking Alpha, InvestingPro, and TradingView to produce the top 20 investment opportunities every day.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {[
            { icon: BarChart3, title: 'Multi-Source Ranking', desc: 'Composite scores from 4 premium platforms' },
            { icon: TrendingUp, title: 'Top 20 Daily Picks', desc: 'Entry, stop loss, take profit for each' },
            { icon: Shield, title: 'Risk Management', desc: 'ATR-based stops, volatility, drawdown' },
            { icon: Bell, title: 'Alerts', desc: 'Email, push, Telegram, Slack' },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card p-6">
              <Icon className="w-10 h-10 text-primary-500 mb-3" />
              <h3 className="font-semibold text-white mb-1">{title}</h3>
              <p className="text-slate-400 text-sm">{desc}</p>
            </div>
          ))}
        </div>
        <Link href="/dashboard" className="btn-primary inline-flex items-center gap-2">
          View Dashboard
        </Link>
      </main>
    </div>
  );
}
