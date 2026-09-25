import { Card, Heading, Text } from "@radix-ui/themes";

// Shown wherever results are shown: what a reader should not conclude.
export function NotChecked() {
  return (
    <Card className="cc-notchecked">
      <Heading as="h2" size="4" mb="2">
        What CurbCut does not check
      </Heading>
      <ul className="cc-list">
        <li>
          <Text>It does not certify WCAG conformance. Testing with disabled people cannot be replaced.</Text>
        </li>
        <li>
          <Text>It does not judge real screen reader experience, cognitive load, or caption quality.</Text>
        </li>
        <li>
          <Text>Flagged findings are IBM Bob's judgment and can be wrong.</Text>
        </li>
        <li>
          <Text>Benchmark numbers come from a demo app with planted issues. Other code bases may differ.</Text>
        </li>
      </ul>
    </Card>
  );
}
