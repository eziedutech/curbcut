import { ExclamationTriangleIcon } from "@radix-ui/react-icons";
import { Callout } from "@radix-ui/themes";

export function Notice({ title, detail }: { title: string; detail: string }) {
  return (
    <Callout.Root color="gray" role="status">
      <Callout.Icon>
        <ExclamationTriangleIcon />
      </Callout.Icon>
      <Callout.Text>
        <strong>{title}.</strong> {detail}
      </Callout.Text>
    </Callout.Root>
  );
}
