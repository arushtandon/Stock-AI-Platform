'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowUpRight, RefreshCw } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

async function fetchRecommendations() {
  const res = await fetch(`${API_BASE}/api/v1/recommendations?limit=20`);
  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
}

export default function DashboardPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['recommendations'],
    queryFn: fetchRecommendations,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-slate-400">Loading recommendations...</div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="card p-8 max-w-md text-center">
          <p className="text-red-400 mb-4">Could not load recommendations. Is the API running?</p>
          <p className="text-slate-500 text-sm mb-4">Start backend: uvicorn api.main:app --reload</p>
          <button onClick={() => refetch()} className="btn-primary">Retry</button>
        </div>
      </div>
    );
  }

  const list = Array.isArray(data) ? data : [];

  return (
    <div className="min-h-screen">
      <nav className="border-b border-slate-700/50 bg-surface-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-14">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/safron-logo.svg" alt="Safron" width={120} height={40} className="h-8 w-auto" />
          </Link>
          <div className="flex gap-4">
            <Link href="/dashboard" className="text-white">Dashboard</Link>
            <Link href="/analysis" className="text-slate-400 hover:text-white">Analysis</Link>
            <Link href="/portfolio" className="text-slate-400 hover:text-white">Portfolio</Link>
            <Link href="/performance" className="text-slate-400 hover:text-white">Performance</Link>
            <Link href="/integrations" className="text-slate-400 hover:text-white">Integrations</Link>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-white">Safron top 20 stock picks</h1>
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 text-slate-400 hover:text-white"
          >
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
        </div>
        {list.length === 0 ? (
          <div className="card p-8 text-center text-slate-400">
            No recommendations yet. Run the daily pipeline or call POST /api/v1/recommendations/refresh (with auth).
          </div>
        ) : (
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700 text-left text-slate-400 text-sm">
                    <th className="p-4">Symbol</th>
                    <th className="p-4">Entry</th>
                    <th className="p-4">Stop Loss</th>
                    <th className="p-4">Take Profit</th>
                    <th className="p-4">R/R</th>
                    <th className="p-4">Score</th>
                    <th className="p-4">Period</th>
                    <th className="p-4">Sources</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {list.map((r: Record<string, unknown>) => (
                    <tr key={String(r.symbol)} className="border-b border-slate-700/50 hover:bg-slate-800/30">
                      <td className="p-4">
                        <Link href={`/analysis/${r.symbol}`} className="font-semibold text-primary-500 hover:underline">
                          {String(r.symbol)}
                        </Link>
                      </td>
                      <td className="p-4">{Number(r.entry_price)?.toFixed(2)}</td>
                      <td className="p-4 text-red-400">{Number(r.stop_loss)?.toFixed(2)}</td>
                      <td className="p-4 text-emerald-400">{Number(r.take_profit)?.toFixed(2)}</td>
                      <td className="p-4">{String(r.risk_reward_ratio)}</td>
                      <td className="p-4">{Number(r.composite_score)?.toFixed(1)}</td>
                      <td className="p-4 text-slate-400">{String(r.holding_period || '-')}</td>
                      <td className="p-4 text-slate-400 text-sm">
                        {(r.sources as string[])?.join(', ') || '-'}
                      </td>
                      <td className="p-4">
                        <Link href={`/analysis/${r.symbol}`}>
                          <ArrowUpRight className="w-4 h-4 text-slate-500 hover:text-primary-500" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
