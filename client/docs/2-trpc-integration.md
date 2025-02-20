# tRPC Integration Guide

## Overview

tRPC provides end-to-end typesafe APIs in our Next.js application. This document details how tRPC is integrated and used throughout the application.

## Setup Structure

### Client-Side Setup (`src/trpc/react.tsx`)

```typescript
// Key components of client-side tRPC setup
export const api = createTRPCReact<AppRouter>();
export const TRPCReactProvider = ({ children }) => {
  // Provider implementation
};
```

### Server-Side Setup (`src/trpc/server.ts`)

```typescript
// Server-side tRPC utilities
export const { trpc: api, HydrateClient } = createHydrationHelpers<AppRouter>();
```

## Key Concepts

### 1. Type Inference

```typescript
// Input type inference
type CreatePostInput = RouterInputs["post"]["create"];

// Output type inference
type PostData = RouterOutputs["post"]["getById"];
```

### 2. Query Patterns

#### Server Components

```typescript
// In a Server Component (RSC)
const data = await api.post.getById({ id: 1 });
```

#### Client Components

```typescript
// In a Client Component
const { data, isLoading } = api.post.getById.useQuery({ id: 1 });
```

### 3. Mutation Patterns

```typescript
// Define mutation hook
const createPost = api.post.create.useMutation();

// Use mutation
createPost.mutate({
  title: "New Post",
  content: "Content here",
});

// With optimistic updates
createPost.mutate(
  { title: "New Post" },
  {
    onSuccess: (data) => {
      // Handle success
    },
    onError: (error) => {
      // Handle error
    },
  },
);
```

## Advanced Features

### 1. Batching

tRPC automatically batches multiple queries into a single HTTP request:

```typescript
// These will be batched into one request
const { data: posts } = api.post.getAll.useQuery();
const { data: user } = api.user.getCurrent.useQuery();
```

### 2. Prefetching

```typescript
// Server-side prefetching
await api.post.getAll.prefetch();

// Client-side prefetching
api.post.getAll.prefetch();
```

### 3. Invalidation

```typescript
// Invalidate specific queries
const utils = api.useUtils();
utils.post.getAll.invalidate();

// Invalidate specific query keys
utils.post.getAll.invalidate({ type: "draft" });
```

## Error Handling

### 1. Global Error Handler

```typescript
export const TRPCReactProvider = ({ children }) => {
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
  // ... rest of provider implementation
};
```

### 2. Query-Level Error Handling

```typescript
const { data, error } = api.post.getById.useQuery(
  { id: 1 },
  {
    retry: false,
    onError: (error) => {
      console.error("Query error:", error);
    },
  },
);
```

### 3. Mutation Error Handling

```typescript
const mutation = api.post.create.useMutation({
  onError: (error) => {
    console.error("Mutation error:", error);
  },
});
```

## Performance Optimizations

### 1. Caching Configuration

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});
```

### 2. Selective Revalidation

```typescript
const utils = api.useUtils();

// Selective invalidation
utils.post.getAll.invalidate({ type: "published" });

// Selective updates
utils.post.getAll.setData({ type: "published" }, (old) => {
  // Update cached data
  return updatedData;
});
```

## Best Practices

1. **Type Safety**

   - Always use type inference
   - Avoid type assertions
   - Maintain strict TypeScript configuration

2. **Error Handling**

   - Implement proper error boundaries
   - Use appropriate error handling strategies
   - Provide user-friendly error messages

3. **Performance**

   - Configure appropriate cache times
   - Use prefetching when possible
   - Implement optimistic updates

4. **Development**
   - Use the logger in development
   - Implement proper error tracking
   - Maintain consistent naming conventions

## Common Patterns

### 1. Infinite Queries

```typescript
const { data, fetchNextPage } = api.post.getInfinite.useInfiniteQuery(
  {},
  {
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  },
);
```

### 2. Optimistic Updates

```typescript
const utils = api.useUtils();
const mutation = api.post.create.useMutation({
  onMutate: async (newPost) => {
    await utils.post.getAll.cancel();
    const previousPosts = utils.post.getAll.getData();

    utils.post.getAll.setData(undefined, (old) => [...old, newPost]);

    return { previousPosts };
  },
  onError: (err, newPost, context) => {
    utils.post.getAll.setData(undefined, context.previousPosts);
  },
});
```

### 3. Real-time Updates

```typescript
const { data } = api.post.getAll.useQuery(undefined, {
  refetchInterval: 1000, // Poll every second
});
```

## Real-Time Features

### 1. Subscription Patterns

tRPC supports real-time updates through subscriptions:

```typescript
// Server-side procedure definition
export const postRouter = router({
  onPostUpdate: publicProcedure
    .subscription(async function* ({ ctx }) {
      while (true) {
        // Check for updates
        const updates = await ctx.db.post.findUpdates();
        if (updates) yield updates;
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }),
});

// Client-side usage
function PostWatcher() {
  const { data, isError } = api.post.onPostUpdate.useSubscription(undefined, {
    onData(post) {
      console.log('Post updated:', post);
    },
    onError(err) {
      console.error('Subscription error:', err);
    },
  });

  return (
    <div>
      {data && <PostUpdate post={data} />}
    </div>
  );
}
```

### 2. Polling

For simpler real-time needs, you can implement polling:

```typescript
function LivePostFeed() {
  const { data } = api.post.getAll.useQuery(undefined, {
    // Refetch every 5 seconds
    refetchInterval: 5000,
    // Only poll when the window is focused
    refetchIntervalInBackground: false,
  });

  return (
    <PostList posts={data} />
  );
}
```

## Advanced Error Handling

### 1. Custom Error Classes

```typescript
// server/errors.ts
export class CustomTRPCError extends TRPCError {
  constructor(code: TRPC_ERROR_CODE_KEY, message: string, cause?: unknown) {
    super({ code, message, cause });
  }
}

// Usage in procedures
export const userRouter = router({
  updateProfile: protectedProcedure
    .input(updateProfileSchema)
    .mutation(async ({ input, ctx }) => {
      try {
        // Update logic
      } catch (error) {
        throw new CustomTRPCError(
          "BAD_REQUEST",
          "Failed to update profile",
          error,
        );
      }
    }),
});
```

### 2. Error Boundaries

```typescript
// components/TRPCErrorBoundary.tsx
class TRPCErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return <ErrorDisplay error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

## Testing

### 1. Unit Testing Procedures

```typescript
// tests/procedures/post.test.ts
import { createInnerTRPCContext } from "../src/server/trpc";
import { appRouter } from "../src/server/router";
import { expect, describe, it } from "vitest";

describe("Post procedures", () => {
  it("should create a post", async () => {
    const ctx = createInnerTRPCContext({ session: mockSession });
    const caller = appRouter.createCaller(ctx);

    const post = await caller.post.create({
      title: "Test Post",
      content: "Test Content",
    });

    expect(post).toMatchObject({
      title: "Test Post",
      content: "Test Content",
    });
  });
});
```

### 2. Integration Testing

```typescript
// tests/integration/post-workflow.test.ts
import { createTRPCClient } from "@trpc/client";
import { expect, describe, it } from "vitest";

describe("Post Workflow", () => {
  const client = createTRPCClient<AppRouter>({
    url: "http://localhost:3000/api/trpc",
  });

  it("should handle full post lifecycle", async () => {
    // Create post
    const post = await client.post.create.mutate({
      title: "Integration Test",
      content: "Testing the full workflow",
    });

    // Verify creation
    expect(post.id).toBeDefined();

    // Update post
    const updated = await client.post.update.mutate({
      id: post.id,
      title: "Updated Title",
    });

    expect(updated.title).toBe("Updated Title");

    // Delete post
    await client.post.delete.mutate({ id: post.id });

    // Verify deletion
    await expect(client.post.getById.query({ id: post.id })).rejects.toThrow();
  });
});
```

## Performance Optimization

### 1. Query Deduplication

```typescript
function PostPage({ id }: { id: string }) {
  // These identical queries will be deduped automatically
  const { data: postHeader } = api.post.getById.useQuery({ id });
  const { data: postContent } = api.post.getById.useQuery({ id });
  const { data: postFooter } = api.post.getById.useQuery({ id });

  return (
    <article>
      <PostHeader post={postHeader} />
      <PostContent post={postContent} />
      <PostFooter post={postFooter} />
    </article>
  );
}
```

### 2. Selective Cache Updates

```typescript
function PostList() {
  const utils = api.useUtils();
  const updatePost = api.post.update.useMutation({
    onSuccess: (updatedPost) => {
      // Update all queries that include this post
      utils.post.getAll.setData(undefined, (oldPosts) => {
        return oldPosts?.map((post) =>
          post.id === updatedPost.id ? updatedPost : post,
        );
      });

      // Update the individual post query
      utils.post.getById.setData({ id: updatedPost.id }, updatedPost);
    },
  });
}
```

### 3. Infinite Query Optimization

```typescript
function InfinitePostList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage
  } = api.post.getInfinite.useInfiniteQuery(
    { limit: 10 },
    {
      getNextPageParam: (lastPage) => lastPage.nextCursor,
      keepPreviousData: true,
      onSuccess: (data) => {
        if (data.pages[data.pages.length - 1].nextCursor) {
          queryClient.prefetchInfiniteQuery(
            api.post.getInfinite.getQueryKey({ limit: 10 }),
            () => api.post.getInfinite.fetch({ limit: 10 })
          );
        }
      },
    }
  );

  return (
    <div>
      {data?.pages.map((page, i) => (
        <React.Fragment key={i}>
          {page.items.map(post => (
            <PostCard key={post.id} post={post} />
          ))}
        </React.Fragment>
      ))}
      {hasNextPage && (
        <button
          onClick={() => fetchNextPage()}
          disabled={isFetchingNextPage}
        >
          {isFetchingNextPage ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  );
}
```

## Security Considerations

### 1. Input Validation

```typescript
// schemas/post.ts
import { z } from "zod";

export const createPostSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(100, "Title must be less than 100 characters"),
  content: z
    .string()
    .min(1, "Content is required")
    .max(10000, "Content must be less than 10000 characters"),
  tags: z.array(z.string()).max(5, "Maximum 5 tags allowed"),
});

// router/post.ts
export const postRouter = router({
  create: protectedProcedure
    .input(createPostSchema)
    .mutation(async ({ input, ctx }) => {
      // Input is now fully typed and validated
      return ctx.db.post.create({
        data: input,
      });
    }),
});
```

### 2. Rate Limiting

```typescript
import rateLimit from "express-rate-limit";
import { TRPCError } from "@trpc/server";

const createRateLimit = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
});

export const middleware = t.middleware(async ({ ctx, next }) => {
  if (process.env.NODE_ENV === "production") {
    try {
      await createRateLimit(ctx.req, ctx.res);
    } catch {
      throw new TRPCError({
        code: "TOO_MANY_REQUESTS",
        message: "Too many requests, please try again later",
      });
    }
  }
  return next();
});
```

## Troubleshooting

Common issues and their solutions:

1. **Type Inference Issues**

   - Ensure proper type exports
   - Check for circular dependencies
   - Verify tRPC router configuration

2. **Performance Issues**

   - Review caching configuration
   - Check for unnecessary revalidation
   - Monitor network requests

3. **Hydration Errors**
   - Verify server/client state matches
   - Check for proper provider setup
   - Review component boundaries
