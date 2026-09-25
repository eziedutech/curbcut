import { InfoCircledIcon } from "@radix-ui/react-icons";
import { IconButton, Tooltip } from "@radix-ui/themes";

export function InfoTip({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <Tooltip content={children} className="cc-infotip">
      <IconButton size="1" variant="ghost" color="gray" aria-label={`About ${label}`}>
        <InfoCircledIcon />
      </IconButton>
    </Tooltip>
  );
}
