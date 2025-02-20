# Component Architecture

## Overview

This document outlines our component architecture, focusing on the organization, patterns, and best practices used throughout the application.

## Component Organization

```
src/
├── app/                    # Next.js App Router pages
│   ├── _components/       # Shared components
│   ├── [route]/          # Dynamic routes
│   └── layout.tsx        # Root layout
├── components/            # Global shared components
│   ├── ui/               # UI components
│   └── features/         # Feature-specific components
└── lib/                  # Utilities and helpers
```

## Component Types

### 1. Server Components (Default)

```typescript
// app/posts/page.tsx
export default async function PostsPage() {
  const posts = await api.post.getAll.fetch();

  return (
    <main>
      <h1>Posts</h1>
      <PostGrid posts={posts} />
      <CreatePostButton /> {/* Client Component */}
    </main>
  );
}
```

### 2. Client Components

```typescript
'use client';

// components/features/posts/CreatePostButton.tsx
export function CreatePostButton() {
  const mutation = api.post.create.useMutation();

  return (
    <button
      onClick={() => mutation.mutate({ title: 'New Post' })}
      disabled={mutation.isLoading}
    >
      {mutation.isLoading ? 'Creating...' : 'Create Post'}
    </button>
  );
}
```

### 3. Higher-Order Components (HOCs)

```typescript
// components/hoc/withAuth.tsx
export function withAuth<T extends object>(
  Component: React.ComponentType<T>
) {
  return function WithAuth(props: T) {
    const { data: session, isLoading } = useSession();

    if (isLoading) return <LoadingSpinner />;
    if (!session) return <LoginRedirect />;

    return <Component {...props} />;
  };
}
```

## Component Patterns

### 1. Compound Components

```typescript
// components/ui/Card/index.tsx
export const Card = {
  Root: function CardRoot({ children }: PropsWithChildren) {
    return (
      <div className="rounded-lg shadow-md p-4">
        {children}
      </div>
    );
  },

  Header: function CardHeader({ title, subtitle }: CardHeaderProps) {
    return (
      <div className="mb-4">
        <h3 className="text-xl font-bold">{title}</h3>
        {subtitle && <p className="text-gray-600">{subtitle}</p>}
      </div>
    );
  },

  Content: function CardContent({ children }: PropsWithChildren) {
    return <div className="prose">{children}</div>;
  },

  Footer: function CardFooter({ children }: PropsWithChildren) {
    return (
      <div className="mt-4 flex justify-end gap-2">
        {children}
      </div>
    );
  },
};

// Usage
<Card.Root>
  <Card.Header title="Post Title" subtitle="Posted on..." />
  <Card.Content>Content here...</Card.Content>
  <Card.Footer>
    <Button>Action</Button>
  </Card.Footer>
</Card.Root>
```

### 2. Render Props

```typescript
// components/features/posts/PostList.tsx
export function PostList({
  children,
  filter
}: {
  children: (post: Post) => React.ReactNode;
  filter?: PostFilter;
}) {
  const { data: posts } = api.post.getAll.useQuery({ filter });

  return (
    <div className="grid gap-4">
      {posts?.map((post) => (
        <div key={post.id}>
          {children(post)}
        </div>
      ))}
    </div>
  );
}

// Usage
<PostList filter={{ status: 'published' }}>
  {(post) => (
    <PostCard
      title={post.title}
      excerpt={post.excerpt}
      onClick={() => handleClick(post.id)}
    />
  )}
</PostList>
```

### 3. Custom Hooks

```typescript
// hooks/usePost.ts
export function usePost(id: string) {
  const { data, isLoading, error } = api.post.getById.useQuery({ id });
  const mutation = api.post.update.useMutation();

  const updatePost = async (updates: Partial<Post>) => {
    try {
      await mutation.mutateAsync({ id, ...updates });
    } catch (error) {
      console.error('Failed to update post:', error);
      throw error;
    }
  };

  return {
    post: data,
    isLoading,
    error,
    updatePost,
    isUpdating: mutation.isLoading
  };
}

// Usage in component
export function PostEditor({ id }: { id: string }) {
  const { post, updatePost, isLoading } = usePost(id);

  if (isLoading) return <LoadingSpinner />;

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      updatePost({ title: e.target.title.value });
    }}>
      {/* Form fields */}
    </form>
  );
}
```

## State Management

### 1. Local Component State

```typescript
'use client';

export function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count}
    </button>
  );
}
```

### 2. Server State

```typescript
'use client';

export function PostViewer() {
  const { data, isLoading } = api.post.getAll.useQuery();

  if (isLoading) return <LoadingSpinner />;

  return (
    <div>
      {data?.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

## Performance Optimizations

### 1. Component Memoization

```typescript
export const ExpensiveComponent = memo(
  function ExpensiveComponent({ data }: Props) {
    return (
      // Expensive render logic
    );
  },
  (prevProps, nextProps) => {
    return prevProps.data.id === nextProps.data.id;
  }
);
```

### 2. Lazy Loading

```typescript
// app/posts/[id]/page.tsx
const PostEditor = lazy(() => import('@/components/features/posts/PostEditor'));

export default function PostPage() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <PostEditor />
    </Suspense>
  );
}
```

## Error Boundaries

```typescript
// components/ErrorBoundary.tsx
'use client';

export class ErrorBoundary extends React.Component<
  PropsWithChildren<{
    fallback: React.ReactNode;
  }>,
  { hasError: boolean }
> {
  constructor(props: PropsWithChildren<{ fallback: React.ReactNode }>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }

    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<ErrorUI />}>
  <PostList />
</ErrorBoundary>
```

## Best Practices

1. **Component Organization**

   - Keep components small and focused
   - Use meaningful names
   - Organize by feature when possible

2. **Type Safety**

   - Use TypeScript for all components
   - Define proper prop types
   - Avoid any type

3. **Performance**

   - Use Server Components by default
   - Implement proper memoization
   - Lazy load when appropriate

4. **Accessibility**
   - Use semantic HTML
   - Implement ARIA attributes
   - Test with screen readers

## Common Patterns

### 1. Layout Components

```typescript
// components/layouts/DashboardLayout.tsx
export function DashboardLayout({
  children,
  sidebar
}: PropsWithChildren<{ sidebar?: React.ReactNode }>) {
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 bg-gray-100">
        {sidebar}
      </aside>
      <main className="flex-1 p-6">
        {children}
      </main>
    </div>
  );
}
```

### 2. Container Components

```typescript
// components/features/posts/PostContainer.tsx
export function PostContainer({ id }: { id: string }) {
  const { data, isLoading } = api.post.getById.useQuery({ id });

  if (isLoading) return <LoadingSpinner />;
  if (!data) return <NotFound />;

  return <PostView post={data} />;
}
```

### 3. Provider Pattern

```typescript
// contexts/ThemeContext.tsx
'use client';

const ThemeContext = createContext<{
  theme: Theme;
  setTheme: (theme: Theme) => void;
} | null>(null);

export function ThemeProvider({ children }: PropsWithChildren) {
  const [theme, setTheme] = useState<Theme>('light');

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```
