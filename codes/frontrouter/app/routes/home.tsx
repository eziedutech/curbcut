import { Box, Card, Code, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { Link } from "react-router";

import { InfoTip } from "~/components/InfoTip";
import { NotChecked } from "~/components/NotChecked";
import { Notice } from "~/components/Notice";
import { TierBadge } from "~/components/TierBadge";
import { listReports } from "~/lib/backpy.server";
import { shortSha } from "~/lib/wcag";

import type { Route } from "./+types/home";

export const meta: Route.MetaFunction = () => [
  { title: "CurbCut: accessibility review that proves its fixes" },
  { name: "description", content: "IBM Bob reviews pull requests against WCAG 2.2 and proves each fix with a test." },
];

export async function loader() {
  try {
    return { reports: await listReports(), error: null };
  } catch {
    return { reports: null, error: "Reports are unavailable right now." };
  }
}

const TIERS = [
  { kind: "proven", text: "Measured by the engine. Cites a fact." },
  { kind: "flagged", text: "IBM Bob's judgment, with a reason." },
  { kind: "out_of_reach", text: "Cannot be checked this way. Always listed." },
  { kind: "verified", text: "Test fails before the fix, passes after." },
] as const;

export default function Home({ loaderData }: Route.ComponentProps) {
  const { reports, error } = loaderData;
  return (
    <Flex direction="column" gap="6">
      <Box>
        <Heading as="h1" size="8" mb="2">
          Accessibility review that proves its fixes
        </Heading>
        <Text as="p" size="4" color="gray">
          IBM Bob reviews each pull request against WCAG 2.2, with one subagent per principle, fixes what it finds, and
          proves every fix with a test.
        </Text>
      </Box>

      <Grid columns={{ initial: "1", sm: "2", md: "4" }} gap="3">
        {TIERS.map((t) => (
          <Card key={t.kind}>
            <TierBadge kind={t.kind} />
            <Text as="p" size="2" mt="2">
              {t.text}
            </Text>
          </Card>
        ))}
      </Grid>

      <Box>
        <Flex align="center" gap="1" mb="3">
          <Heading as="h2" size="5">
            Reviewed pull requests
          </Heading>
          <InfoTip label="reviewed pull requests">Each report is sent by the review pipeline after IBM Bob finishes.</InfoTip>
        </Flex>
        {error && <Notice title="Not loaded" detail={error} />}
        {reports && reports.length === 0 && <Notice title="No reports yet" detail="Reports appear here after a review." />}
        <Flex direction="column" gap="3">
          {reports?.map((r) => (
            <Card key={r.id} asChild>
              <Link to={`/reports/${r.id}`} className="cc-report-link">
                <Heading as="h3" size="4" mb="1">
                  {r.id.toUpperCase()}: <Code variant="ghost">{r.head}</Code>
                </Heading>
                <Text as="p" size="2" color="gray" mb="2">
                  {r.repo} at {shortSha(r.head_sha)}
                </Text>
                <Flex gap="3" wrap="wrap">
                  <Text size="2">
                    <strong>{r.proven}</strong> proven
                  </Text>
                  <Text size="2">
                    <strong>{r.flagged}</strong> flagged
                  </Text>
                  <Text size="2">
                    <strong>{r.out_of_reach}</strong> out of reach
                  </Text>
                  <Text size="2">
                    <strong>{r.not_scanned}</strong> not scanned
                  </Text>
                  {r.verified_fixes !== null && (
                    <Text size="2">
                      <strong>{r.verified_fixes}</strong> verified fixes
                    </Text>
                  )}
                </Flex>
              </Link>
            </Card>
          ))}
        </Flex>
      </Box>

      <NotChecked />
    </Flex>
  );
}
