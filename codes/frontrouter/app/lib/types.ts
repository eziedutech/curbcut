export type Tier = "proven" | "flagged";

export type Finding = {
  id: string;
  tier: Tier;
  sc: string;
  title: string;
  principle: "perceivable" | "operable" | "understandable" | "robust";
  severity: "critical" | "serious" | "moderate" | "minor";
  page: string;
  selector: string;
  fact_ids: string[];
  reason: string;
  who_is_affected: string;
  how_to_fix: string;
  fixable: boolean;
  understanding_url?: string;
  source: string;
};

export type Fix = { finding_id: string; status?: string; files_changed?: string[]; explanation?: string };

export type VerifyRow = {
  test: string;
  finding_id: string | null;
  base: string | null;
  head: string | null;
  verdict: "verified" | "not_proving" | "still_failing" | "error";
};

export type Summary = { proven: number; flagged: number; out_of_reach: number; not_scanned: number };

export type Report = {
  id: string;
  repo: string;
  generated_at: string;
  received_at?: string;
  engine: { axe_core: string; chromium: string; curbcut: string };
  pr: { base: string; head: string; base_sha: string; head_sha: string };
  facts: { summary: { facts_total: number }; digest: string; duration_s: number };
  review: {
    summary: Summary;
    findings: Finding[];
    out_of_reach: { sc: string; title: string; reason: string }[];
    not_scanned: { fact_id?: string; page?: string; reason: string }[];
  };
  fixes: { fixes: Fix[]; not_fixed?: { finding_id: string; reason?: string }[] } | null;
  verify: { summary: { verified: number; not_proving: number; still_failing: number; error: number; total: number }; results: VerifyRow[] } | null;
  after: { head: { ref: string; sha: string }; summary: { facts_total: number } } | null;
  narration: { page: string; before: string[] | null; after: string[] | null }[];
};

export type ReportListItem = Summary & {
  id: string;
  repo: string;
  head: string;
  head_sha: string;
  received_at: string;
  verified_fixes: number | null;
};
