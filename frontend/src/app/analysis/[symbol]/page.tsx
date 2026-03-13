'use client';

import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export default function StockAnalysisPage() {
  const params = useParams();
  const symbol = (params?.symbol as string)?.toUpperCase() || '';
  const { data, isLoading, error } = useQuery({
    queryKey: ['analysis', symbol],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/analysis/stock/${symbol}`);
      if (!res.ok) throw new Error('Not found');
      return res.json();
    },
    enabled: !!symbol,
  });

  if (isLoading || !symbol) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <span className="text-slate-400">Loading...</span>
      </div>
    );
  }
  if (error || !data?.symbol) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="card p-8 text-center">
          <p className="text-slate-400 mb-4">No analysis found for {symbol}</p>
          <Link href="/dashboard" className="btn-primary">Back to Dashboard</Link>
        </div>
      </div>
    );
  }

  const r = data;
  return (
    <div className="min-h-screen">
      <nav className="border-b border-slate-700/50 bg-surface-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-14">
          <Link href="/" className="text-xl font-semibold text-primary-500">Stock AI</Link>
          <Link href="/dashboard" className="text-slate-400 hover:text-white">Dashboard</Link>
        </div>
      </nav>
      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-2">{r.symbol}</h1>
        {r.company_name && <p className="text-slate-400 mb-8">{r.company_name}</p>}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card p-6">
            <h3 className="text-slate-400 text-sm font-medium mb-2">Entry & Levels</h3>
            <p className="text-2xl text-white">Entry: ${Number(r.entry_price)?.toFixed(2)}</p>
            <p className="text-red-400">Stop Loss: ${Number(r.stop_loss)?.toFixed(2)}</p>
            <p className="text-emerald-400">Take Profit: ${Number(r.take_profit)?.toFixed(2)}</p>
            {r.support_level != null && <p className="text-slate-400">Support: ${Number(r.support_level).toFixed(2)}</p>}
            {r.resistance_level != null && <p className="text-slate-400">Resistance: ${Number(r.resistance_level).toFixed(2)}</p>}
          </div>
          <div className="card p-6">
            <h3 className="text-slate-400 text-sm font-medium mb-2">Metrics</h3>
            <p>Composite Score: <span className="text-primary-500 font-semibold">{Number(r.composite_score)?.toFixed(1)}</span></p>
            <p>Risk/Reward: {String(r.risk_reward_ratio)}</p>
            <p>Expected Return: {Number(r.expected_return_pct)?.toFixed(1)}%</p>
            <p>Position Risk: {Number(r.position_risk_pct)?.toFixed(1)}%</p>
            <p>Holding Period: {String(r.holding_period || '-')}</p>
          </div>
        </div>
        {r.sources?.length > 0 && (
          <div className="card p-6 mt-6">
            <h3 className="text-slate-400 text-sm font-medium mb-2">Sources</h3>
            <p className="text-slate-300">{r.sources.join(', ')}</p>
          </div>
        )}
        <div className="mt-8">
          <Link href="/dashboard" className="text-primary-500 hover:underline">← Back to Dashboard</Link>
        </div>
      </main>
    </div>
  );
}
