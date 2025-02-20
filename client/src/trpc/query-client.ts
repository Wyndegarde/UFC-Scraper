import {
  defaultShouldDehydrateQuery,
  QueryClient,
} from "@tanstack/react-query";
import SuperJSON from "superjson";

/**
 * Creates and configures a QueryClient instance for TanStack Query (React Query).
 * 
 * This configuration is optimized for Server-Side Rendering (SSR) applications and handles:
 * - Server state management and caching
 * - Data fetching optimization
 * - Complex data type serialization
 * - Server to client state transfer
 * 
 * @returns {QueryClient} Configured QueryClient instance
 */
export const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        // Prevents immediate refetching during client-side hydration
        // Data becomes stale after 30 seconds
        staleTime: 30 * 1000,
      },
      dehydrate: {
        // Uses SuperJSON to handle complex JavaScript types that JSON doesn't support
        // (e.g., Date objects, Map, Set)
        serializeData: SuperJSON.serialize,
        // Includes both default dehydration cases and queries in pending state
        // This ensures proper state transfer from server to client
        shouldDehydrateQuery: (query) =>
          defaultShouldDehydrateQuery(query) ||
          query.state.status === "pending",
      },
      hydrate: {
        // Deserializes data back to its original form with proper type preservation
        deserializeData: SuperJSON.deserialize,
      },
    },
  });
