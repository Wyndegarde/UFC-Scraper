# Data Fetching Patterns

## Overview

This document outlines the various data fetching patterns used in our Next.js application, focusing on the integration between Server Components, Client Components, and tRPC.

## Core Patterns

### 1. Server Component Data Fetching

```typescript
// In a Server Component (*.tsx)
export default async function PostPage() {
  // Direct server-side fetch
  const post = await api.post.getById({ id: 1 });

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
      {/* Client components for interactive elements */}
      <LikeButton postId={post.id} />
    </article>
  );
}
```

### 2. Client Component Data Fetching

```typescript
'use client';

export function LikeButton({ postId }: { postId: number }) {
  // Client-side query with hooks
  const { data, isLoading } = api.post.getLikes.useQuery({ postId });
  const likeMutation = api.post.like.useMutation();

  if (isLoading) return <LoadingSpinner />;

  return (
    <button onClick={() => likeMutation.mutate({ postId })}>
      Likes: {data?.count ?? 0}
    </button>
  );
}
```

## Advanced Patterns

### 1. Parallel Data Fetching

```typescript
// Server Component parallel fetching
export default async function DashboardPage() {
  // Fetch multiple data sources in parallel
  const [posts, users, comments] = await Promise.all([
    api.post.getAll.fetch(),
    api.user.getAll.fetch(),
    api.comment.getAll.fetch()
  ]);

  return (
    <Dashboard
      posts={posts}
      users={users}
      comments={comments}
    />
  );
}
```

### 2. Streaming Data with Suspense

```typescript
export default function PostsPage() {
  return (
    <Suspense fallback={<LoadingUI />}>
      <Posts />
    </Suspense>
  );
}

async function Posts() {
  const posts = await api.post.getAll.fetch();
  return <PostsList posts={posts} />;
}
```

### 3. Infinite Loading

```typescript
'use client';

export function InfinitePostsList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage
  } = api.post.getInfinite.useInfiniteQuery(
    {},
    {
      getNextPageParam: (lastPage) => lastPage.nextCursor,
    }
  );

  return (
    <div>
      {data?.pages.map((page) => (
        page.posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))
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

## Caching Strategies

### 1. Server-Side Caching

```typescript
// In your API route
export async function GET() {
  const cachedData = await cache.get("key");
  if (cachedData) return cachedData;

  const data = await fetchData();
  await cache.set("key", data, 60 * 5); // 5 minutes

  return data;
}
```

### 2. Client-Side Caching

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Global defaults
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
    },
  },
});

// Per-query configuration
const { data } = api.post.getById.useQuery(
  { id },
  {
    staleTime: 1000 * 60 * 15, // 15 minutes
    cacheTime: 1000 * 60 * 60, // 1 hour
  },
);
```

## Error Handling

### 1. Server-Side Error Handling

```typescript
export default async function PostPage({
  params: { id }
}: {
  params: { id: string }
}) {
  try {
    const post = await api.post.getById({ id });
    return <PostContent post={post} />;
  } catch (error) {
    // Log error to monitoring service
    logError(error);

    // Return error UI
    return <ErrorUI error={error} />;
  }
}
```

### 2. Client-Side Error Handling

```typescript
'use client';

export function PostEditor({ postId }: { postId: number }) {
  const { data, error, isError } = api.post.getById.useQuery(
    { id: postId },
    {
      retry: false,
      onError: (error) => {
        // Log to monitoring service
        logError(error);
      },
    }
  );

  if (isError) {
    return <ErrorMessage error={error} />;
  }

  return <Editor post={data} />;
}
```

## Performance Optimization

### 1. Prefetching

```typescript
// Server-side prefetching
export default async function PostsPage() {
  // Prefetch next page
  await api.post.getAll.prefetch({ page: 2 });

  const posts = await api.post.getAll.fetch({ page: 1 });
  return <PostsList posts={posts} />;
}

// Client-side prefetching
export function PostsList({ posts }: { posts: Post[] }) {
  const utils = api.useUtils();

  // Prefetch on hover
  const prefetchPost = (id: number) => {
    utils.post.getById.prefetch({ id });
  };

  return (
    <ul>
      {posts.map((post) => (
        <li
          key={post.id}
          onMouseEnter={() => prefetchPost(post.id)}
        >
          <PostPreview post={post} />
        </li>
      ))}
    </ul>
  );
}
```

### 2. Optimistic Updates

```typescript
export function CreatePost() {
  const utils = api.useUtils();
  const mutation = api.post.create.useMutation({
    onMutate: async (newPost) => {
      // Cancel outgoing refetches
      await utils.post.getAll.cancel();

      // Snapshot previous value
      const previousPosts = utils.post.getAll.getData();

      // Optimistically update
      utils.post.getAll.setData(undefined, (old) => [
        ...old,
        { ...newPost, id: "temp-id" },
      ]);

      return { previousPosts };
    },
    onError: (err, newPost, context) => {
      // Revert on error
      utils.post.getAll.setData(undefined, context.previousPosts);
    },
    onSettled: () => {
      // Refetch after error or success
      utils.post.getAll.invalidate();
    },
  });
}
```

## Best Practices

1. **Data Fetching Strategy Selection**

   - Use Server Components for initial data fetch
   - Use Client Components for interactive features
   - Implement proper loading states

2. **Error Handling**

   - Implement error boundaries
   - Provide fallback UI
   - Log errors appropriately

3. **Performance**

   - Use appropriate caching strategies
   - Implement prefetching
   - Optimize bundle size

4. **Type Safety**
   - Leverage tRPC's type inference
   - Implement proper validation
   - Maintain consistent types

## Common Pitfalls

1. **Over-fetching**

   - Solution: Use proper query parameters
   - Implement field selection
   - Use pagination where appropriate

2. **Unnecessary Rerenders**

   - Solution: Implement proper memoization
   - Use appropriate dependency arrays
   - Split components appropriately

3. **Race Conditions**
   - Solution: Cancel outdated requests
   - Implement proper loading states
   - Use optimistic updates carefully
