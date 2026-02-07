import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    typedRoutes: true,
  },
  webpack: (config, { isServer }) => {
    // Ensure aliases are properly resolved in both client and server bundles
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false, // Disable fs module for client-side
      };
    }
    
    return config;
  },
};

export default nextConfig;
