import { Box, Container, Flex, Text } from "@radix-ui/themes";
import { Link, NavLink } from "react-router";

const NAV = [
  { to: "/", label: "Overview" },
  { to: "/evidence", label: "Evidence" },
  { to: "/about", label: "About" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="cc-page">
      <a className="cc-skip" href="#main">
        Skip to main content
      </a>
      <div className="cc-band" />
      <Box asChild className="cc-header" px="4" py="3">
        <header>
          <Container size="3">
            <Flex align="center" justify="between" gap="4" wrap="wrap">
              <Link to="/" className="cc-brand">
                <img src="/favicon.svg" alt="" width="28" height="28" />
                <span>CurbCut</span>
              </Link>
              <nav aria-label="Main">
                <ul className="cc-nav">
                  {NAV.map((item) => (
                    <li key={item.to}>
                      <NavLink to={item.to} end={item.to === "/"}>
                        {item.label}
                      </NavLink>
                    </li>
                  ))}
                </ul>
              </nav>
            </Flex>
          </Container>
        </header>
      </Box>
      <Box asChild px="4" py="5">
        <main id="main" tabIndex={-1}>
          <Container size="3">{children}</Container>
        </main>
      </Box>
      <Box asChild px="4" py="4" className="cc-footer">
        <footer>
          <Container size="3">
            <Text size="1" color="gray">
              CurbCut. Accessibility review that proves its fixes. Built with IBM Bob. Build {__APP_SHA__}.
            </Text>
          </Container>
        </footer>
      </Box>
    </div>
  );
}
