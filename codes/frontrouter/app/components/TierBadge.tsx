import {
  CheckCircledIcon,
  CrossCircledIcon,
  EyeNoneIcon,
  EyeOpenIcon,
  QuestionMarkCircledIcon,
  TargetIcon,
} from "@radix-ui/react-icons";
import { Badge } from "@radix-ui/themes";

export type BadgeKind =
  | "proven"
  | "flagged"
  | "out_of_reach"
  | "not_scanned"
  | "verified"
  | "not_proving"
  | "still_failing"
  | "error";

// Colour is never the only signal: every badge carries an icon and a word.
const STYLE: Record<BadgeKind, { label: string; color: "red" | "amber" | "gray" | "green" | "orange"; Icon: typeof TargetIcon }> = {
  proven: { label: "Proven", color: "red", Icon: TargetIcon },
  flagged: { label: "Flagged", color: "amber", Icon: EyeOpenIcon },
  out_of_reach: { label: "Out of reach", color: "gray", Icon: EyeNoneIcon },
  not_scanned: { label: "Not scanned", color: "gray", Icon: QuestionMarkCircledIcon },
  verified: { label: "Verified fix", color: "green", Icon: CheckCircledIcon },
  not_proving: { label: "Test not proving", color: "orange", Icon: QuestionMarkCircledIcon },
  still_failing: { label: "Still failing", color: "red", Icon: CrossCircledIcon },
  error: { label: "Test error", color: "gray", Icon: CrossCircledIcon },
};

export function TierBadge({ kind }: { kind: BadgeKind }) {
  const { label, color, Icon } = STYLE[kind];
  return (
    <Badge color={color} variant="soft" size="2" highContrast>
      <Icon aria-hidden="true" />
      {label}
    </Badge>
  );
}
