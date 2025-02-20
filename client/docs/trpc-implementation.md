# tRPC Implementation Guide

## Overview

This document details how tRPC is implemented in our repository, providing end-to-end type safety between the client and server. Our implementation uses Next.js 13+ App Router with React Server Components (RSC) support.

## Architecture

### Directory Structure

```
client/src/
├── server/
│   └── api/
│       ├── routers/        # Individual route handlers
│       ├── root.ts         # Root router configuration
│       └── trpc.ts         # tRPC initialization and context
├── trpc/
│   ├── react.tsx          # Client-side tRPC setup
│   ├── server.ts          # Server-side tRPC utilities
│   └── query-client.ts    # TanStack Query configuration
└── app/
    └── api/
        └── trpc/          # API route handlers
```

## Server-Side Setup

### 1. tRPC Initialization (`server/api/trpc.ts`)

```typescript
// Initialize tRPC with context and transformer
const t = initTRPC.context<typeof createTRPCContext>().create({
  transformer: superjson,
  errorFormatter({ shape, error }) {
    return {
      ...shape,
      data: {
        ...shape.data,
        zodError:
          error.cause instanceof ZodError ? error.cause.flatten() : null,
      },
    };
  },
});

// Create public procedure with timing middleware
const publicProcedure = t.procedure.use(timingMiddleware);

// Context creation for API requests
export const createTRPCContext = async (opts: { headers: Headers }) => {
  return {
    db,
    ...opts,
  };
};
```

### 2. Router Configuration (`server/api/root.ts`)

```typescript
// Root router configuration
export const appRouter = createTRPCRouter({
  post: postRouter,
  // Add other routers here
});

// Type definition export
export type AppRouter = typeof appRouter;

// Server-side caller creation
export const createCaller = createCallerFactory(appRouter);
```

## Client-Side Integration

### 1. Provider Setup (`trpc/react.tsx`)

```typescript
export function TRPCReactProvider({ children }: { children: React.ReactNode }) {
  const queryClient = getQueryClient();
  const [trpcClient] = useState(() => createTRPCClient());

  return (
    <QueryClientProvider client={queryClient}>
      <api.Provider client={trpcClient} queryClient={queryClient}>
        {children}
      </api.Provider>
    </QueryClientProvider>
  );
}
```

### 2. Server Component Usage

```typescript
// In a Server Component
export default async function PostsPage() {
  // Direct server-side call
  const posts = await api.post.getAll.fetch();

  return (
    <main>
      <PostList posts={posts} />
      <CreatePostButton /> {/* Client Component */}
    </main>
  );
}
```

### 3. Client Component Usage

```typescript
'use client';

export function CreatePostButton() {
  // Client-side mutation
  const mutation = api.post.create.useMutation({
    onSuccess: () => {
      // Handle success
    },
  });

  return (
    <button
      onClick={() => mutation.mutate({ title: 'New Post' })}
      disabled={mutation.isLoading}
    >
      Create Post
    </button>
  );
}
```

## Type Safety Features

### 1. Input Validation

```typescript
// In a router file
export const postRouter = createTRPCRouter({
  create: publicProcedure
    .input(
      z.object({
        title: z.string().min(1).max(100),
        content: z.string().min(1),
      }),
    )
    .mutation(async ({ input, ctx }) => {
      return ctx.db.post.create({
        data: input,
      });
    }),
});
```

### 2. Type Inference

```typescript
// Automatic type inference
type CreatePostInput = RouterInputs["post"]["create"];
type PostData = RouterOutputs["post"]["getById"];

// Usage in components
const { data } = api.post.getById.useQuery({
  id: "123", // Type-safe parameter
});
```

## Performance Optimizations

### 1. Request Batching

```typescript
// Automatic request batching
function PostWithUser() {
  // These will be batched into a single request
  const { data: post } = api.post.getById.useQuery({ id: "123" });
  const { data: user } = api.user.getById.useQuery({ id: post?.authorId });
}
```

### 2. Caching Configuration

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
    },
  },
});
```

## Error Handling

### 1. Global Error Handling

```typescript
export const TRPCReactProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [trpcClient] = useState(() =>
    api.createClient({
      links: [
        loggerLink({
          enabled: (op) =>
            process.env.NODE_ENV === "development" ||
            (op.direction === "down" && op.result instanceof Error),
        }),
      ],
    }),
  );
};
```

### 2. Procedure-Level Error Handling

```typescript
export const postRouter = createTRPCRouter({
  create: publicProcedure
    .input(
      z.object({
        title: z.string(),
      }),
    )
    .mutation({
      async resolve({ input, ctx }) {
        try {
          return await ctx.db.post.create({
            data: input,
          });
        } catch (error) {
          throw new TRPCError({
            code: "INTERNAL_SERVER_ERROR",
            message: "Failed to create post",
            cause: error,
          });
        }
      },
    }),
});
```

## Development Tools

### 1. Timing Middleware

```typescript
const timingMiddleware = t.middleware(async ({ next, path }) => {
  const start = Date.now();

  if (process.env.NODE_ENV === "development") {
    // Add artificial delay in development
    await new Promise((resolve) =>
      setTimeout(resolve, Math.random() * 400 + 100),
    );
  }

  const result = await next();
  const duration = Date.now() - start;

  console.log(`[TRPC] ${path} took ${duration}ms`);
  return result;
});
```

### 2. Development Logging

```typescript
// Enhanced error logging in development
if (process.env.NODE_ENV === "development") {
  api.createClient({
    links: [
      loggerLink({
        enabled: true,
        headers: true,
      }),
    ],
  });
}
```

## Best Practices

1. **Router Organization**

   - Group related procedures in feature-specific routers
   - Use meaningful procedure names
   - Implement proper input validation

2. **Type Safety**

   - Leverage Zod for input validation
   - Use type inference wherever possible
   - Avoid type assertions

3. **Performance**

   - Implement proper caching strategies
   - Use request batching
   - Optimize query configurations

4. **Error Handling**
   - Implement proper error boundaries
   - Use TRPCError for typed errors
   - Provide meaningful error messages

## Common Patterns

### 1. Protected Routes

```typescript
const protectedProcedure = publicProcedure.use(
  t.middleware(async ({ next, ctx }) => {
    if (!ctx.session?.user) {
      throw new TRPCError({ code: "UNAUTHORIZED" });
    }
    return next({
      ctx: {
        ...ctx,
        user: ctx.session.user,
      },
    });
  }),
);
```

### 2. Optimistic Updates

```typescript
const mutation = api.post.create.useMutation({
  onMutate: async (newPost) => {
    await utils.post.getAll.cancel();
    const previousPosts = utils.post.getAll.getData();

    utils.post.getAll.setData(undefined, (old) => [
      ...(old ?? []),
      { ...newPost, id: "temp" },
    ]);

    return { previousPosts };
  },
  onError: (err, newPost, context) => {
    utils.post.getAll.setData(undefined, context?.previousPosts);
  },
});
```

### 3. Infinite Queries

```typescript
const { data, fetchNextPage } = api.post.getInfinite.useInfiniteQuery(
  {},
  {
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  },
);
```
