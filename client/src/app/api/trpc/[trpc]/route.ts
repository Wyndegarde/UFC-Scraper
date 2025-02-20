/**
 * This file serves as the main API route handler for tRPC requests in a Next.js application.
 * It acts as a bridge between client-side tRPC queries/mutations and server-side procedures by:
 * - Receiving and processing all tRPC requests
 * - Setting up request context with headers
 * - Routing requests to appropriate procedures in appRouter
 * - Handling errors (with detailed logging in development)
 * - Returning results to the client
 * 
 * The handler is exported for both GET and POST methods to handle all types of tRPC requests.
 */

import { fetchRequestHandler } from "@trpc/server/adapters/fetch";
import { type NextRequest } from "next/server";

import { env } from "~/env";
import { appRouter } from "~/server/api/root";
import { createTRPCContext } from "~/server/api/trpc";

/**
 * This wraps the `createTRPCContext` helper and provides the required context for the tRPC API when
 * handling a HTTP request (e.g. when you make requests from Client Components).
 */
const createContext = async (req: NextRequest) => {
  return createTRPCContext({
    headers: req.headers,
  });
};

const handler = (req: NextRequest) =>
  fetchRequestHandler({
    endpoint: "/api/trpc",
    req,
    router: appRouter,
    createContext: () => createContext(req),
    onError:
      env.NODE_ENV === "development"
        ? ({ path, error }) => {
            console.error(
              `❌ tRPC failed on ${path ?? "<no-path>"}: ${error.message}`
            );
          }
        : undefined,
  });

export { handler as GET, handler as POST };
