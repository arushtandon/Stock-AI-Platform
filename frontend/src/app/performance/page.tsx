'use client';

import { useQuery } from '@tanstack/react-query';
import Image from 'next/image';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

async function fetchPerformance() {
  const res = await fetch(`${API_BASE}/api/v1/performance`);
  if (!res.ok) throw new Error('Failed to fetch performance');
  return res.json();
}

type Position = {
  symbol: string;
  entry_price: number;
  current_price: number;
  pnl_usd: number;
  return_pct: number;
  margin_used: number;
  status: string;
};

export default function PerformancePage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['performance'],
    queryFn: fetchPerformance,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#020617]">
        <div className="animate-pulse text-slate-400">Loading performance...</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#020617]">
        <Image src="/safron-logo.svg" alt="Safron" width={140} height={48} className="mb-6 h-10 w-auto" />
        <div className="card p-8 max-w-md text-center">
          <p className="text-red-400 mb-4">Could not load performance from the API.</p>
          <button onClick={() => refetch()} className="btn-primary">Retry</button>
        </div>
      </div>
    );
  }

  const positions: Position[] = data.positions || [];

  return (
    <div className="min-h-screen bg-[#020617]">
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Image src="/safron-logo.svg" alt="Safron" width={140} height={48} className="h-10 w-auto" />
            <div>
              <h1 className="text-xl font-semibold text-white">Portfolio performance</h1>
              <p className="text-slate-500 text-xs">Capital per position: USD {data.capital_per_position?.toLocaleString?.() || '100,000'}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          <div className="card p-4">
            <p className="text-slate-400 text-xs uppercase mb-1">Total positions</p>
            <p className="text-white text-lg font-semibold">{data.total_positions}</p>
          </div>
          <div className="card p-4">
            <p className="text-slate-400 text-xs uppercase mb-1">Realized PnL (USD)</p>
            <p className={(data.realized_pnl_usd ?? 0) >= 0 ? 'text-emerald-400 text-lg font-semibold' : 'text-red-400 text-lg font-semibold'}>
              {(data.realized_pnl_usd ?? 0).toFixed(2)}
            </p>
          </div>
          <div className="card p-4">
            <p className="text-slate-400 text-xs uppercase mb-1">Realized PnL (%)</p>
            <p className={(data.realized_pnl_pct ?? 0) >= 0 ? 'text-emerald-400 text-lg font-semibold' : 'text-red-400 text-lg font-semibold'}>
              {(data.realized_pnl_pct ?? 0).toFixed(2)}%
            </p>
          </div>
          <div className="card p-4">
            <p className="text-slate-400 text-xs uppercase mb-1">Unrealized PnL (USD)</p>
            <p className={(data.unrealized_pnl_usd ?? 0) >= 0 ? 'text-emerald-400 text-lg font-semibold' : 'text-red-400 text-lg font-semibold'}>
              {(data.unrealized_pnl_usd ?? 0).toFixed(2)}
            </p>
          </div>
          <div className="card p-4">
            <p className="text-slate-400 text-xs uppercase mb-1">Unrealized PnL (%)</p>
            <p className={(data.unrealized_pnl_pct ?? 0) >= 0 ? 'text-emerald-400 text-lg font-semibold' : 'text-red-400 text-lg font-semibold'}>
              {(data.unrealized_pnl_pct ?? 0).toFixed(2)}%
            </p>
          </div>
          <div className="card p-4">
            <p className="text-slate-400 text-xs uppercase mb-1">Win rate</p>
            <p className="text-emerald-400 text-lg font-semibold">{(data.win_rate_pct ?? 0).toFixed(1)}%</p>
          </div>
        </div>

        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700 text-left text-slate-400">
                  <th className="p-3">Symbol</th>
                  <th className="p-3">Entry</th>
                  <th className="p-3">Current</th>
                  <th className="p-3">Return %</th>
                  <th className="p-3">PnL (USD)</th>
                  <th className="p-3">Margin used</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {positions.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="p-4 text-center text-slate-500">
                      No tracked positions yet.
                    </td>
                  </tr>
                ) : (
                  positions.map((p) => (
                    <tr key={p.symbol} className="border-b border-slate-800">
                      <td className="p-3 text-white">{p.symbol}</td>
                      <td className="p-3 text-slate-300">{p.entry_price.toFixed(2)}</td>
                      <td className="p-3 text-slate-300">{p.current_price.toFixed(2)}</td>
                      <td className={`p-3 ${p.return_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {p.return_pct.toFixed(2)}%
                      </td>
                      <td className={`p-3 ${p.pnl_usd >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {p.pnl_usd.toFixed(2)}
                      </td>
                      <td className="p-3 text-slate-300">{p.margin_used.toLocaleString()}</td>
                      <td className="p-3 text-slate-300">{p.status}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
