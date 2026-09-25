import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("reports/:id", "routes/report.tsx"),
  route("evidence", "routes/evidence.tsx"),
  route("about", "routes/about.tsx"),
  route("health", "routes/health.ts"),
  route("api/reports/ingest", "routes/ingest.ts"),
] satisfies RouteConfig;
