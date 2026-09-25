import { Text } from "@radix-ui/themes";
import { Link } from "react-router";

export function Breadcrumbs({ items }: { items: { label: string; to?: string }[] }) {
  return (
    <nav aria-label="Breadcrumb" className="cc-crumbs">
      <ol>
        {items.map((item, i) => (
          <li key={item.label}>
            {item.to ? <Link to={item.to}>{item.label}</Link> : <Text aria-current="page">{item.label}</Text>}
            {i < items.length - 1 && (
              <Text color="gray" aria-hidden="true">
                {" / "}
              </Text>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
