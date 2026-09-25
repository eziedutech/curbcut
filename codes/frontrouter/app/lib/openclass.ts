// Static copies of the reviewed OpenClass versions (scripts/export_openclass.py).
const VERSIONS: Record<string, { before: string; after?: string }> = {
  "pr-1": { before: "pr-1", after: "pr-1-fixed" },
  "pr-1-run2": { before: "pr-1", after: "pr-1-fixed" },
  "pr-2": { before: "pr-2" },
};

export function openclassLinks(reportId: string, page: string) {
  const v = VERSIONS[reportId];
  if (!v) return null;
  return {
    before: `/openclass/${v.before}/${page}`,
    after: v.after ? `/openclass/${v.after}/${page}` : null,
  };
}
