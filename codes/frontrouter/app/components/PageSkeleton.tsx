import { Box, Flex, Grid, Skeleton } from "@radix-ui/themes";

// Mirrors the report layout: a title, a row of tiles, then cards.
export function PageSkeleton() {
  return (
    <Box aria-busy="true" aria-label="Loading">
      <Skeleton height="32px" width="45%" mb="4" />
      <Grid columns={{ initial: "2", sm: "5" }} gap="3" mb="5">
        {Array.from({ length: 5 }, (_, i) => (
          <Skeleton key={i} height="84px" />
        ))}
      </Grid>
      <Flex direction="column" gap="3">
        {Array.from({ length: 3 }, (_, i) => (
          <Skeleton key={i} height="120px" />
        ))}
      </Flex>
    </Box>
  );
}
