import { Box, Card, Flex, Grid, Heading, Text } from "@radix-ui/themes";

import { NotChecked } from "~/components/NotChecked";

import type { Route } from "./+types/about";

export const meta: Route.MetaFunction = () => [{ title: "About - CurbCut" }];

const STEPS = [
  { title: "Skill", text: "IBM Bob read WCAG 2.2 and wrote the wcag-audit skill and its policy pack." },
  { title: "Review", text: "The cc-review mode runs the engine, then four read-only Explore subagents review one WCAG principle each, in parallel." },
  { title: "Fix", text: "The cc-fixer mode can only edit the app and its fixes list. It makes the smallest change per finding." },
  { title: "Prove", text: "The cc-prover mode writes one test per fix. A fix counts only if its test fails before and passes after." },
];

export default function About() {
  return (
    <Flex direction="column" gap="6">
      <Box>
        <Heading as="h1" size="7" mb="2">
          About CurbCut
        </Heading>
        <Text as="p" color="gray">
          Accessibility issues pass code review because most reviewers are not WCAG experts. CurbCut puts that review
          into the pull request, built on IBM Bob.
        </Text>
      </Box>

      <Grid columns={{ initial: "1", sm: "2" }} gap="3">
        {STEPS.map((s, i) => (
          <Card key={s.title}>
            <Heading as="h2" size="3" mb="1">
              {i + 1}. {s.title}
            </Heading>
            <Text size="2">{s.text}</Text>
          </Card>
        ))}
      </Grid>

      <Box>
        <Heading as="h2" size="5" mb="2">
          What it claims
        </Heading>
        <Text as="p">
          CurbCut finds accessibility issues in a pull request, separates measured facts from judgment, and proves each fix
          with a test.
        </Text>
      </Box>

      <NotChecked />
    </Flex>
  );
}
