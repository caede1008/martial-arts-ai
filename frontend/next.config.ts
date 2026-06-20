import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: [
  'acre-petition-fretful.ngrok-free.dev',
  'discounts-additions-kennedy-elderly.trycloudflare.com',
  ],
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "ngrok-skip-browser-warning",
            value: "true",
          },
        ],
      },
    ]
  },
};

export default nextConfig;