'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import Image from 'next/image';
import { Key, CheckCircle, XCircle, ExternalLink } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

async function fetchIntegrationStatus() {
  const res = await fetch(`${API_BASE}/api/v1/integrations/status`);
  if (!res.ok) return null;
  return res.json();
}

const SOURCES = [
  { id: 'danelfin', name: 'Danelfin', envVar: 'DANELFIN_API_KEY', url: 'https://www.danelfin.com' },
  { id: 'seeking_alpha', name: 'Seeking Alpha Premium', envVar: 'SEEKING_ALPHA_API_KEY', url: 'https://seekingalpha.com' },
  { id: 'investing_pro', name: 'Investing.com Pro', envVar: 'INVESTING_PRO_API_KEY', url: 'https://www.investing.com' },
  { id: 'tradingview', name: 'TradingView', envVar: 'TRADINGVIEW_API_KEY', url: 'https://www.tradingview.com' },
] as const;

export default function IntegrationsPage() {
  const { data: status, isLoading } = useQuery({
    queryKey: ['integrations-status'],
    queryFn: fetchIntegrationStatus,
  });

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
            <Link href="/performance" className="text-slate-400 hover:text-white">Performance</Link>
            <Link href="/integrations" className="text-white flex items-center gap-1">
              <Key className="w-4 h-4" /> Integrations
            </Link>
          </div>
        </div>
      </nav>
      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-white mb-2">Premium data source credentials</h1>
        <p className="text-slate-400 mb-8">
          Add your API keys or login credentials for each service below. Recommendations are aggregated from these sources. Set variables in <strong>Render → stock-ai-api → Environment</strong> (or in your deployment env). Keys are never shown in the UI.
        </p>

        <div className="space-y-4 mb-10">
          {SOURCES.map((source) => {
            const configured = status ? status[source.id] === true : false;
            return (
              <div key={source.id} className="card p-6 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Key className="w-8 h-8 text-slate-500" />
                  <div>
                    <h2 className="font-semibold text-white">{source.name}</h2>
                    <p className="text-slate-500 text-sm">Env: <code className="bg-slate-800 px-1 rounded">{source.envVar}</code></p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  {isLoading ? (
                    <span className="text-slate-500 text-sm">Checking…</span>
                  ) : configured ? (
                    <span className="flex items-center gap-1 text-emerald-400 text-sm">
                      <CheckCircle className="w-4 h-4" /> Connected
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-amber-500 text-sm">
                      <XCircle className="w-4 h-4" /> Not configured
                    </span>
                  )}
                  <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-white">
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>

        <div className="card p-6 bg-slate-800/50">
          <h3 className="font-semibold text-white mb-2">How to add credentials</h3>
          <ol className="text-slate-400 text-sm list-decimal list-inside space-y-2">
            <li>Open <strong>Render Dashboard</strong> → <strong>stock-ai-api</strong> → <strong>Environment</strong>.</li>
            <li>Add a variable for each source (e.g. <code className="bg-slate-900 px-1 rounded">DANELFIN_API_KEY</code>).</li>
            <li>Paste your API key or token from the provider (Danelfin, Seeking Alpha, etc.).</li>
            <li>Save and redeploy the API. This page will show &quot;Connected&quot; when the key is set.</li>
          </ol>
          <p className="text-slate-500 text-sm mt-4">
            Without credentials, the model uses demo/synthetic data for rankings. With credentials, live data from each platform is used to produce recommendations.
          </p>
        </div>

        <div className="mt-6">
          <Link href="/dashboard" className="text-primary-500 hover:underline">← Back to Dashboard</Link>
        </div>
      </main>
    </div>
  );
}
