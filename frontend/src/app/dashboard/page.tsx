'use client';

import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowUpRight, RefreshCw } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

async function fetchRecommendations() {
  const res = await fetch(`${API_BASE}/api/v1/recommendations?limit=50`);
  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
}

type Rec = {
  symbol: string;
  company_name?: string;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  risk_reward_ratio: string;
  composite_score: number;
  holding_period: string;
  sources?: string[];
};

const HOLDING_PERIOD_GROUPS = [
  {
    key: 'short',
    title: 'Short term (0–2 weeks)',
  },
  {
    key: 'medium',
    title: 'Medium term (1–2 months)',
  },
  {
    key: 'long',
    title: 'Long term (3–6 months)',
  },
] as const;

function groupByHoldingPeriod(list: Rec[]): Record<string, Rec[]> {
  const groups: Record<string, Rec[]> = {
    short: [],
    medium: [],
    long: [],
  };
  for (const r of list) {
    const period = (r.holding_period || '').toLowerCase();
    if (['short_term', 'swing'].includes(period)) groups.short.push(r);
    else if (period === 'medium_term') groups.medium.push(r);
    else if (period === 'long_term') groups.long.push(r);
  }
  return groups;
}

function useClock() {
  const [now, setNow] = useState<Date>(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  const time = now.toLocaleTimeString(undefined, { hour12: false });
  const date = now.toLocaleDateString(undefined, {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  return { time, date };
}

export default function DashboardPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['recommendations'],
    queryFn: fetchRecommendations,
  });
  const { time, date } = useClock();

  const list: Rec[] = Array.isArray(data) ? data : [];
  const byPeriod = groupByHoldingPeriod(list);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="animate-pulse text-slate-400">Loading recommendations...</div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-black">
        <Image src="/safron-logo.svg" alt="Safron" width={200} height={72} className="mb-10 h-14 w-auto" />
        <div className="card p-8 max-w-md text-center bg-slate-900/80">
          <p className="text-red-400 mb-4">Could not load recommendations from the API.</p>
          <button onClick={() => refetch()} className="btn-primary">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-slate-100">
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Top banner with logo and clock */}
        <div className="flex items-center justify-between mb-10">
          <div className="flex items-center gap-4">
            <Image src="/safron-logo.svg" alt="Safron" width={220} height={80} className="h-16 w-auto" />
          </div>
          <div className="text-right">
            <div className="text-4xl md:text-5xl font-semibold tracking-[0.25em] text-slate-100">
              {time}
            </div>
            <div className="text-slate-400 text-sm mt-1">{date}</div>
          </div>
        </div>

        <div className="flex items-center justify-between mb-6">
          <p className="text-slate-500 text-xs uppercase tracking-[0.25em]">
            Safron recommendation model · Capital per idea: USD 100,000
          </p>
          <div className="flex items-center gap-3">
            <button
              onClick={() => refetch()}
              className="flex items-center gap-2 text-slate-400 hover:text-emerald-400 text-sm"
            >
              <RefreshCw className="w-4 h-4" /> Refresh
            </button>
            <Link
              href="/performance"
              className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 text-sm"
            >
              View performance
            </Link>
          </div>
        </div>

        <h2 className="text-white font-semibold mb-4">Top 10 stock recommendations by holding period</h2>
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {HOLDING_PERIOD_GROUPS.map(({ key, title }) => {
            const recs = (byPeriod[key] || []).slice(0, 10);
            return (
              <div key={key} className="card p-5 bg-slate-900/80">
                <h3 className="text-white font-medium mb-4">{title}</h3>
                {recs.length === 0 ? (
                  <p className="text-slate-500 text-sm">No recommendations for this period yet.</p>
                ) : (
                  <div className="space-y-2">
                    {recs.map((r) => (
                      <div
                        key={r.symbol}
                        className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0"
                      >
                        <div className="flex-1 min-w-0">
                          <Link
                            href={`/analysis/${r.symbol}`}
                            className="font-medium text-emerald-400 hover:underline"
                          >
                            {r.symbol}
                          </Link>
                          <p className="text-slate-500 text-xs truncate">{r.company_name || '—'}</p>
                        </div>
                        <div className="flex items-center gap-3 text-right shrink-0">
                          <span className="text-slate-400 text-xs">
                            Entry {Number(r.entry_price)?.toFixed(2)}
                          </span>
                          <span className="text-emerald-400 text-sm font-medium">
                            {Number(r.composite_score)?.toFixed(1)}
                          </span>
                          <Link href={`/analysis/${r.symbol}`} className="text-slate-500 hover:text-emerald-400">
                            <ArrowUpRight className="w-4 h-4" />
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {list.length > 0 && (
          <div className="mt-8">
            <Link
              href="/analysis"
              className="text-emerald-400 hover:underline text-sm"
            >
              View full analysis →
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}
