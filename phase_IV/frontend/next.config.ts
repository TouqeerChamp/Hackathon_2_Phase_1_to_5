import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: { ignoreBuildErrors: true },
  eslint: { ignoreDuringBuilds: true },
  // Turbopack ko khamosh karne ke liye empty config
  experimental: {
  }
};

export default nextConfig;
