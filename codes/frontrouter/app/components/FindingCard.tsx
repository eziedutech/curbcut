import { Badge, Card, Code, Flex, Heading, Link, Text } from "@radix-ui/themes";

import type { Finding, Fix, VerifyRow } from "~/lib/types";

import { TierBadge } from "./TierBadge";

export function FindingCard({ finding, fix, test }: { finding: Finding; fix?: Fix; test?: VerifyRow }) {
  return (
    <Card className="cc-finding" asChild>
      <article aria-labelledby={`f-${finding.id}`}>
        <Flex gap="2" wrap="wrap" align="center" mb="2">
          <TierBadge kind={finding.tier} />
          {test && <TierBadge kind={test.verdict} />}
          <Badge color="gray" variant="outline" highContrast>
            {finding.severity}
          </Badge>
          <Text size="2" color="gray">
            {finding.id}
          </Text>
        </Flex>
        <Heading as="h4" size="3" id={`f-${finding.id}`} mb="1">
          {finding.understanding_url ? (
            <Link href={finding.understanding_url} target="_blank" rel="noreferrer">
              SC {finding.sc}
            </Link>
          ) : (
            <>SC {finding.sc}</>
          )}
          {": "}
          {finding.title}
        </Heading>
        <Text as="p" size="2" color="gray" mb="2">
          <Code variant="ghost">{finding.page}</Code> <Code variant="ghost">{finding.selector}</Code>
        </Text>
        <dl className="cc-dl">
          <dt>Who is affected</dt>
          <dd>{finding.who_is_affected}</dd>
          <dt>{finding.tier === "proven" ? "Measured" : "Why flagged"}</dt>
          <dd>{finding.reason}</dd>
          <dt>How to fix</dt>
          <dd>{finding.how_to_fix}</dd>
          {fix?.explanation && (
            <>
              <dt>Fix applied</dt>
              <dd>{fix.explanation}</dd>
            </>
          )}
          {test && (
            <>
              <dt>Test</dt>
              <dd>
                <Code variant="ghost">{test.test.split("::")[0]}</Code>: {test.base} before the fix, {test.head} after
              </dd>
            </>
          )}
        </dl>
      </article>
    </Card>
  );
}
