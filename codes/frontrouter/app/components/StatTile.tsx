import { Card, Flex, Text } from "@radix-ui/themes";

import { InfoTip } from "./InfoTip";

export function StatTile({ label, value, info }: { label: string; value: number | string; info: string }) {
  return (
    <Card className="cc-stat">
      <Flex align="center" gap="1">
        <Text size="2" color="gray">
          {label}
        </Text>
        <InfoTip label={label}>{info}</InfoTip>
      </Flex>
      <Text as="p" size="7" weight="bold">
        {value}
      </Text>
    </Card>
  );
}
