/** @type {import('next').NextConfig} */
const nextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  // Pages render only after the client-side login check, so automatic dev-mode
  // instant-navigation validation cannot see them; validate only pages that opt in.
  experimental: {
    instantInsights: { validationLevel: "manual-warning" },
  },
  turbopack: {
    rules: {
      "*.css": { loaders: ["@tailwindcss/turbopack"], as: "*.css" },
    },
  },
}

export default nextConfig
