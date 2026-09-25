import { Box, Code, Flex, Heading, Table, Text } from "@radix-ui/themes";

import { InfoTip } from "~/components/InfoTip";
import { NotChecked } from "~/components/NotChecked";
import benchmark from "~/data/benchmark.json";
import { PRINCIPLE_LABEL, PRINCIPLES } from "~/lib/wcag";

import type { Route } from "./+types/evidence";

export const meta: Route.MetaFunction = () => [{ title: "Evidence - CurbCut" }];

type Column = {
  found: number;
  planted: number;
  judgment_only_found: number;
  judgment_only_planted: number;
  decoys_hit: number;
  decoys: number;
  items: number;
  unmatched: { id: string; scs: string[]; label: string }[];
  by_principle: Record<string, { found: number; planted: number }>;
  per_issue: { gt_id: string; found: boolean }[];
};
type Run = {
  run: string;
  axe_only: Column;
  engine: Column;
  curbcut: Column;
  verify?: { verified: number; not_proving: number; total: number };
};

const COLUMNS = [
  { key: "axe_only", label: "axe-core alone" },
  { key: "engine", label: "CurbCut engine" },
  { key: "curbcut", label: "CurbCut with IBM Bob" },
] as const;

export default function Evidence() {
  const runs = (benchmark as { runs: Run[] }).runs;
  const pr1 = runs.filter((r) => r.run.startsWith("pr-1")).map((r) => r.curbcut.found);
  return (
    <Flex direction="column" gap="6">
      <Box>
        <Heading as="h1" size="7" mb="2">
          Evidence
        </Heading>
        <Text as="p" color="gray">
          Scored against issues planted in OpenClass, a demo class app, plus decoys that look wrong but are correct.
        </Text>
      </Box>

      {runs.map((run) => (
        <Box key={run.run}>
          <Heading as="h2" size="5" mb="3">
            {run.run.toUpperCase()}
          </Heading>
          <Table.Root variant="surface">
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeaderCell>Method</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>Planted issues found</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>
                  <Flex align="center" gap="1">
                    Judgment-only issues
                    <InfoTip label="judgment-only issues">Issues no automated rule can detect, such as unclear alt text.</InfoTip>
                  </Flex>
                </Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>Decoys wrongly flagged</Table.ColumnHeaderCell>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {COLUMNS.map((c) => {
                const col = run[c.key];
                return (
                  <Table.Row key={c.key}>
                    <Table.RowHeaderCell>{c.label}</Table.RowHeaderCell>
                    <Table.Cell>
                      {col.found} of {col.planted}
                    </Table.Cell>
                    <Table.Cell>
                      {col.judgment_only_found} of {col.judgment_only_planted}
                    </Table.Cell>
                    <Table.Cell>
                      {col.decoys_hit} of {col.decoys}
                    </Table.Cell>
                  </Table.Row>
                );
              })}
            </Table.Body>
          </Table.Root>

          <Table.Root variant="surface" mt="3">
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeaderCell>WCAG principle</Table.ColumnHeaderCell>
                {COLUMNS.map((c) => (
                  <Table.ColumnHeaderCell key={c.key}>{c.label}</Table.ColumnHeaderCell>
                ))}
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {PRINCIPLES.map((p) => (
                <Table.Row key={p}>
                  <Table.RowHeaderCell>{PRINCIPLE_LABEL[p]}</Table.RowHeaderCell>
                  {COLUMNS.map((c) => {
                    const b = run[c.key].by_principle[p];
                    return (
                      <Table.Cell key={c.key}>
                        {b.found} of {b.planted}
                      </Table.Cell>
                    );
                  })}
                </Table.Row>
              ))}
            </Table.Body>
          </Table.Root>

          <Flex direction="column" gap="1" mt="3">
            {run.verify && (
              <Text size="2">
                Fixes proven by a test that fails before and passes after: <strong>{run.verify.verified}</strong> of{" "}
                {run.verify.total}.
              </Text>
            )}
            <Text size="2">
              Missed by CurbCut:{" "}
              {run.curbcut.per_issue
                .filter((i) => !i.found)
                .map((i) => i.gt_id)
                .join(", ") || "none"}
              .
            </Text>
            <Text size="2">
              Findings matching no planted issue: {run.curbcut.unmatched.length} of {run.curbcut.items}. Some are real issues
              that were not planted; they are listed in the results file, not counted as correct.
            </Text>
          </Flex>
        </Box>
      ))}

      <Box>
        <Heading as="h2" size="5" mb="2">
          Limits of this benchmark
        </Heading>
        <ul className="cc-list">
          {pr1.length > 1 && (
            <li>
              <Text>
                Two runs on PR-1 found {pr1.join(" and ")} issues. Differences of this size are run-to-run variation in
                IBM Bob's judgment, not an improvement.
              </Text>
            </li>
          )}
          <li>
            <Text>The issues were planted by the same team that built CurbCut.</Text>
          </li>
          <li>
            <Text>A finding counts only if it points at the same element with an accepted success criterion.</Text>
          </li>
          <li>
            <Text>
              Rerun it: <Code highContrast>uv run --project codes/engine python scripts/benchmark/score.py pr-1</Code>
            </Text>
          </li>
        </ul>
      </Box>

      <NotChecked />
    </Flex>
  );
}
