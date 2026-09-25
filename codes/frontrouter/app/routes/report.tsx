import { Box, Card, Code, DataList, Flex, Grid, Heading, Table, Text } from "@radix-ui/themes";
import { data } from "react-router";

import { Breadcrumbs } from "~/components/Breadcrumbs";
import { FindingCard } from "~/components/FindingCard";
import { InfoTip } from "~/components/InfoTip";
import { NotChecked } from "~/components/NotChecked";
import { StatTile } from "~/components/StatTile";
import { TierBadge } from "~/components/TierBadge";
import { BackpyError, getReport } from "~/lib/backpy.server";
import type { Report } from "~/lib/types";
import { PRINCIPLE_LABEL, PRINCIPLES, shortSha } from "~/lib/wcag";

import type { Route } from "./+types/report";

export const meta: Route.MetaFunction = ({ params }) => [{ title: `${params.id.toUpperCase()} report - CurbCut` }];

export async function loader({ params }: Route.LoaderArgs) {
  try {
    return { report: await getReport(params.id) };
  } catch (error) {
    if (error instanceof BackpyError && error.status === 404) throw data("Report not found", { status: 404 });
    throw data("Report unavailable", { status: 503 });
  }
}

function Narration({ report }: { report: Report }) {
  return (
    <>
      {report.narration
        .filter((n) => n.before)
        .map((n) => {
          const before = n.before ?? [];
          const after = n.after ?? [];
          return (
            <Grid key={n.page} columns={{ initial: "1", sm: "2" }} gap="3">
              <Card>
                <Heading as="h3" size="2" mb="2">
                  Before the fix
                </Heading>
                <ol className="cc-narration">
                  {before.map((line, i) => (
                    <li key={i} className={after.includes(line) ? undefined : "cc-changed"}>
                      {line}
                    </li>
                  ))}
                </ol>
              </Card>
              <Card>
                <Heading as="h3" size="2" mb="2">
                  After the fix
                </Heading>
                {n.after ? (
                  <ol className="cc-narration">
                    {after.map((line, i) => (
                      <li key={i} className={before.includes(line) ? undefined : "cc-fixed"}>
                        {line}
                      </li>
                    ))}
                  </ol>
                ) : (
                  <Text size="2" color="gray">
                    No fixed branch was scanned.
                  </Text>
                )}
              </Card>
            </Grid>
          );
        })}
    </>
  );
}

export default function ReportPage({ loaderData }: Route.ComponentProps) {
  const { report } = loaderData;
  const s = report.review.summary;
  const fixes = new Map((report.fixes?.fixes ?? []).map((f) => [f.finding_id.toUpperCase(), f]));
  const tests = new Map((report.verify?.results ?? []).filter((r) => r.finding_id).map((r) => [r.finding_id!.toUpperCase(), r]));
  const v = report.verify?.summary;

  return (
    <Flex direction="column" gap="6">
      <Box>
        <Breadcrumbs items={[{ label: "Overview", to: "/" }, { label: report.id.toUpperCase() }]} />
        <Heading as="h1" size="7" mb="1">
          {report.id.toUpperCase()}: <Code variant="ghost">{report.pr.head}</Code>
        </Heading>
        <Text as="p" color="gray">
          {report.repo}, {report.pr.base} at {shortSha(report.pr.base_sha)} to {report.pr.head} at{" "}
          {shortSha(report.pr.head_sha)}
        </Text>
      </Box>

      <Grid columns={{ initial: "2", sm: "3", md: "5" }} gap="3">
        <StatTile label="Proven" value={s.proven} info="Backed by a measured fact from the engine." />
        <StatTile label="Flagged" value={s.flagged} info="IBM Bob's judgment with a written reason. Can be wrong." />
        <StatTile label="Out of reach" value={s.out_of_reach} info="Criteria this method cannot check for these pages." />
        <StatTile label="Not scanned" value={s.not_scanned} info="Pages or facts that could not be processed, with the reason." />
        <StatTile
          label="Verified fixes"
          value={v ? `${v.verified}/${v.total}` : "none"}
          info="A test that fails on the pull request and passes on the fixed branch."
        />
      </Grid>

      <Box>
        <Flex align="center" gap="1" mb="3">
          <Heading as="h2" size="5">
            Screen reader narration
          </Heading>
          <InfoTip label="screen reader narration">
            Simulated from the accessibility tree, not a real screen reader. Highlighted lines changed with the fix.
          </InfoTip>
        </Flex>
        <Narration report={report} />
      </Box>

      <Box>
        <Heading as="h2" size="5" mb="3">
          Findings
        </Heading>
        <Flex direction="column" gap="5">
          {PRINCIPLES.map((p) => {
            const list = report.review.findings.filter((f) => f.principle === p);
            return (
              <Box key={p}>
                <Heading as="h3" size="4" mb="2">
                  {PRINCIPLE_LABEL[p]} ({list.length})
                </Heading>
                <Flex direction="column" gap="3">
                  {list.map((f) => (
                    <FindingCard key={f.id} finding={f} fix={fixes.get(f.id.toUpperCase())} test={tests.get(f.id.toUpperCase())} />
                  ))}
                </Flex>
              </Box>
            );
          })}
        </Flex>
      </Box>

      <Box>
        <Heading as="h2" size="5" mb="3">
          Out of reach
        </Heading>
        <Table.Root variant="surface">
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Criterion</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Why it is not checked</Table.ColumnHeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {report.review.out_of_reach.map((o) => (
              <Table.Row key={o.sc}>
                <Table.RowHeaderCell>
                  <Flex gap="2" align="center" wrap="wrap">
                    <TierBadge kind="out_of_reach" /> {o.sc} {o.title}
                  </Flex>
                </Table.RowHeaderCell>
                <Table.Cell>{o.reason}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
        {report.review.not_scanned.length > 0 && (
          <Box mt="3">
            <Heading as="h3" size="3" mb="2">
              Not scanned
            </Heading>
            <ul className="cc-list">
              {report.review.not_scanned.map((n, i) => (
                <li key={i}>
                  <Text size="2">
                    {n.fact_id ?? n.page}: {n.reason}
                  </Text>
                </li>
              ))}
            </ul>
          </Box>
        )}
      </Box>

      <Box>
        <Heading as="h2" size="5" mb="3">
          Run
        </Heading>
        <DataList.Root>
          <DataList.Item>
            <DataList.Label>Engine facts</DataList.Label>
            <DataList.Value>
              {report.facts.summary.facts_total} in {report.facts.duration_s} s, digest {report.facts.digest.slice(0, 12)}
            </DataList.Value>
          </DataList.Item>
          {report.after && (
            <DataList.Item>
              <DataList.Label>After the fix</DataList.Label>
              <DataList.Value>
                {report.after.summary.facts_total} facts on {report.after.head.ref}
              </DataList.Value>
            </DataList.Item>
          )}
          <DataList.Item>
            <DataList.Label>Engine</DataList.Label>
            <DataList.Value>
              axe-core {report.engine.axe_core}, Chromium {report.engine.chromium}
            </DataList.Value>
          </DataList.Item>
        </DataList.Root>
      </Box>

      <NotChecked />
    </Flex>
  );
}
