/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  async rewrites() {
    if (!process.env.NEXT_PUBLIC_API_URL) return [];
    return [
      { source: '/api/:path*', destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*` },
    ];
  },
};

module.exports = nextConfig;
