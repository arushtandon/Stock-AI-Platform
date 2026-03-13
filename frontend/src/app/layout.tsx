import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from '@/components/Providers';

const inter = Inter({ subsets: ['latin'], variable: '--font-geist-sans' });

export const metadata: Metadata = {
  title: 'Safron Stock Recommendations',
  description: 'Internal company stock recommendation model — Danelfin, Seeking Alpha, Investing Pro, TradingView',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans bg-surface-950 text-slate-100 min-h-screen`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
