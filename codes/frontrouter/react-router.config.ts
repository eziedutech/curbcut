import type { Config } from "@react-router/dev/config";

export default {
  ssr: true,
  // Dokploy's Traefik ends TLS, so the server sees http:// while the browser's Origin says https://.
  allowedActionOrigins: ["curbcut.eziedutech.dev"],
} satisfies Config;
