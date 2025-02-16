# Performance Optimization Guide

## Overview

This document outlines performance optimization strategies and best practices implemented in our Next.js application.

## Core Optimizations

### 1. Server Components

Server Components are the default in our Next.js 13+ app, providing several performance benefits:

```typescript
// app/posts/page.tsx
export default async function PostsPage() {
  // This component runs on the server
  // Zero JS is sent to the client for this component
  const posts = await api.post.getAll.fetch();

  return (
    <main>
      <h1>Posts</h1>
      <PostGrid posts={posts} />
      {/* Client components only where interactivity is needed */}
      <CreatePostButton />
    </main>
  );
}
```

### 2. Component Code Splitting

```typescript
// Lazy loading components
const PostEditor = lazy(() => import('@/components/features/posts/PostEditor'));

export default function PostPage() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <PostEditor />
    </Suspense>
  );
}
```

## Data Fetching Optimizations

### 1. Parallel Data Fetching

```typescript
export default async function DashboardPage() {
  // Fetch data in parallel
  const [posts, users, comments] = await Promise.all([
    api.post.getAll.fetch(),
    api.user.getAll.fetch(),
    api.comment.getAll.fetch()
  ]);

  return <Dashboard posts={posts} users={users} comments={comments} />;
}
```

### 2. Data Caching

```typescript
// Query configuration with caching
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      refetchOnWindowFocus: false,
      refetchOnReconnect: false,
    },
  },
});

// Component with optimized data fetching
export function PostList() {
  const { data } = api.post.getAll.useQuery(undefined, {
    // Override default options for this query
    staleTime: 1000 * 60 * 15, // 15 minutes
  });

  return (
    <div>
      {data?.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

## Rendering Optimizations

### 1. Component Memoization

```typescript
// Memoize expensive components
export const ExpensiveComponent = memo(
  function ExpensiveComponent({ data }: Props) {
    // Expensive calculations or renders
    const processedData = useMemo(() => {
      return data.map(item => expensiveOperation(item));
    }, [data]);

    return (
      <div>
        {processedData.map(item => (
          <div key={item.id}>{item.value}</div>
        ))}
      </div>
    );
  },
  (prevProps, nextProps) => {
    // Custom comparison function
    return prevProps.data.id === nextProps.data.id;
  }
);

// Usage with proper dependencies
export function ParentComponent() {
  const handleClick = useCallback(() => {
    // Event handler logic
  }, []); // Empty deps if no dependencies

  return <ExpensiveComponent onClick={handleClick} />;
}
```

### 2. Virtual Lists

```typescript
import { VirtualList } from '@/components/ui/VirtualList';

export function LargePostList() {
  const { data: posts } = api.post.getAll.useQuery();

  return (
    <VirtualList
      items={posts ?? []}
      height={400}
      itemHeight={100}
      renderItem={(post) => (
        <PostCard key={post.id} post={post} />
      )}
    />
  );
}

// Virtual List Implementation
export function VirtualList<T>({
  items,
  height,
  itemHeight,
  renderItem,
}: VirtualListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);

  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(height / itemHeight),
    items.length
  );

  const visibleItems = items.slice(startIndex, endIndex);

  return (
    <div
      style={{ height, overflow: 'auto' }}
      onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
    >
      <div style={{ height: items.length * itemHeight }}>
        <div style={{ transform: `translateY(${startIndex * itemHeight}px)` }}>
          {visibleItems.map(renderItem)}
        </div>
      </div>
    </div>
  );
}
```

## Image Optimization

### 1. Next.js Image Component

```typescript
import Image from 'next/image';

export function PostImage({ src, alt }: { src: string; alt: string }) {
  return (
    <div className="relative aspect-video">
      <Image
        src={src}
        alt={alt}
        fill
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        className="object-cover"
        loading="lazy"
        quality={75}
      />
    </div>
  );
}
```

### 2. Responsive Images

```typescript
export function ResponsivePostImage({ post }: { post: Post }) {
  return (
    <picture>
      <source
        media="(min-width: 1024px)"
        srcSet={post.image.large}
      />
      <source
        media="(min-width: 768px)"
        srcSet={post.image.medium}
      />
      <Image
        src={post.image.small}
        alt={post.title}
        width={300}
        height={200}
        className="w-full h-auto"
      />
    </picture>
  );
}
```

## Bundle Optimization

### 1. Dynamic Imports

```typescript
// Import heavy libraries dynamically
const Chart = dynamic(() => import('react-chartjs-2'), {
  loading: () => <LoadingSpinner />,
  ssr: false // Disable SSR for client-only libraries
});

export function PostAnalytics() {
  return (
    <div>
      <h2>Post Analytics</h2>
      <Chart data={chartData} />
    </div>
  );
}
```

### 2. Module Optimization

```typescript
// Bad: Importing entire library
import { format, addDays, subDays } from "date-fns";

// Good: Import only what's needed
import format from "date-fns/format";
import addDays from "date-fns/addDays";
import subDays from "date-fns/subDays";
```

## Performance Monitoring

### 1. Web Vitals Tracking

```typescript
// app/layout.tsx
import { useReportWebVitals } from 'next/web-vitals';

export function RootLayout({ children }: { children: React.ReactNode }) {
  useReportWebVitals((metric) => {
    // Send to analytics
    console.log(metric);
  });

  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

### 2. Performance Hooks

```typescript
export function usePerformanceMonitor() {
  useEffect(() => {
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        // Log performance metrics
        console.log(`${entry.name}: ${entry.duration}ms`);
      });
    });

    observer.observe({ entryTypes: ['measure', 'paint'] });

    return () => observer.disconnect();
  }, []);
}

// Usage in component
export function MonitoredComponent() {
  usePerformanceMonitor();

  useEffect(() => {
    performance.mark('component-start');

    // Component logic

    performance.mark('component-end');
    performance.measure(
      'component-render',
      'component-start',
      'component-end'
    );
  }, []);

  return <div>Monitored Component</div>;
}
```

## Best Practices

1. **Component Design**

   - Use Server Components by default
   - Keep Client Components lean
   - Implement proper code splitting

2. **Data Management**

   - Implement efficient caching strategies
   - Use parallel data fetching
   - Optimize query configurations

3. **Rendering**

   - Memoize expensive computations
   - Implement virtual lists for large datasets
   - Use proper dependency arrays

4. **Asset Optimization**
   - Optimize images and media
   - Implement lazy loading
   - Use proper caching headers

## Common Performance Issues

### 1. Memory Leaks

```typescript
export function useMemoryLeak() {
  useEffect(() => {
    const interval = setInterval(() => {
      // Some operation
    }, 1000);

    // Always clean up
    return () => clearInterval(interval);
  }, []);
}
```

### 2. Unnecessary Rerenders

```typescript
// Bad: New object on every render
<Component data={{ id: 1 }} />

// Good: Memoized object
const data = useMemo(() => ({ id: 1 }), []);
<Component data={data} />
```

### 3. Large Bundle Sizes

```typescript
// Bad: Import entire library
import moment from "moment";

// Good: Import specific functionality
import { format } from "date-fns/format";
```
