# State Management

## Overview

This document outlines our approach to state management in the application, covering different types of state and how they are handled.

## Types of State

### 1. Server State

Managed through tRPC and React Query for data fetching and caching.

```typescript
// Example of server state management
export function PostList() {
  // Server state managed by tRPC/React Query
  const { data, isLoading, error } = api.post.getAll.useQuery();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} />;

  return (
    <div>
      {data.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

### 2. Form State

Managed using React Hook Form for complex forms.

```typescript
// Example of form state management
export function PostForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<PostFormData>();
  const mutation = api.post.create.useMutation();

  const onSubmit = handleSubmit(async (data) => {
    try {
      await mutation.mutateAsync(data);
    } catch (error) {
      console.error('Failed to create post:', error);
    }
  });

  return (
    <form onSubmit={onSubmit}>
      <input {...register('title', { required: true })} />
      {errors.title && <span>Title is required</span>}

      <textarea {...register('content', { required: true })} />
      {errors.content && <span>Content is required</span>}

      <button type="submit" disabled={mutation.isLoading}>
        {mutation.isLoading ? 'Creating...' : 'Create Post'}
      </button>
    </form>
  );
}
```

### 3. UI State

Local component state for UI-specific logic.

```typescript
export function Accordion({ items }: { items: AccordionItem[] }) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <div>
      {items.map((item, index) => (
        <div key={index}>
          <button onClick={() => setOpenIndex(index === openIndex ? null : index)}>
            {item.title}
          </button>
          {index === openIndex && (
            <div>{item.content}</div>
          )}
        </div>
      ))}
    </div>
  );
}
```

### 4. Global UI State

Managed through React Context for theme, authentication, etc.

```typescript
// contexts/UIContext.tsx
type UIState = {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
};

type UIAction =
  | { type: 'TOGGLE_THEME' }
  | { type: 'TOGGLE_SIDEBAR' };

const UIContext = createContext<{
  state: UIState;
  dispatch: Dispatch<UIAction>;
} | null>(null);

function uiReducer(state: UIState, action: UIAction): UIState {
  switch (action.type) {
    case 'TOGGLE_THEME':
      return {
        ...state,
        theme: state.theme === 'light' ? 'dark' : 'light'
      };
    case 'TOGGLE_SIDEBAR':
      return {
        ...state,
        sidebarOpen: !state.sidebarOpen
      };
    default:
      return state;
  }
}

export function UIProvider({ children }: PropsWithChildren) {
  const [state, dispatch] = useReducer(uiReducer, {
    theme: 'light',
    sidebarOpen: false
  });

  return (
    <UIContext.Provider value={{ state, dispatch }}>
      {children}
    </UIContext.Provider>
  );
}

export function useUI() {
  const context = useContext(UIContext);
  if (!context) {
    throw new Error('useUI must be used within UIProvider');
  }
  return context;
}
```

## State Management Patterns

### 1. Optimistic Updates

```typescript
export function PostList() {
  const utils = api.useUtils();
  const { data: posts } = api.post.getAll.useQuery();
  const deleteMutation = api.post.delete.useMutation({
    onMutate: async (deletedId) => {
      // Cancel outgoing refetches
      await utils.post.getAll.cancel();

      // Snapshot the previous value
      const previousPosts = utils.post.getAll.getData();

      // Optimistically update to the new value
      utils.post.getAll.setData(undefined, old =>
        old?.filter(post => post.id !== deletedId)
      );

      return { previousPosts };
    },
    onError: (err, deletedId, context) => {
      // If the mutation fails, use the context returned from onMutate to roll back
      utils.post.getAll.setData(undefined, context?.previousPosts);
    },
    onSettled: () => {
      // Always refetch after error or success
      utils.post.getAll.invalidate();
    },
  });

  return (
    <div>
      {posts?.map((post) => (
        <div key={post.id}>
          <h3>{post.title}</h3>
          <button
            onClick={() => deleteMutation.mutate(post.id)}
            disabled={deleteMutation.isLoading}
          >
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}
```

### 2. Computed State

```typescript
export function PostStats() {
  const { data: posts } = api.post.getAll.useQuery();

  // Computed values from posts
  const stats = useMemo(() => {
    if (!posts) return null;

    return {
      total: posts.length,
      published: posts.filter(p => p.status === 'published').length,
      draft: posts.filter(p => p.status === 'draft').length,
      averageLength: posts.reduce((acc, p) => acc + p.content.length, 0) / posts.length
    };
  }, [posts]);

  if (!stats) return null;

  return (
    <div>
      <div>Total Posts: {stats.total}</div>
      <div>Published: {stats.published}</div>
      <div>Drafts: {stats.draft}</div>
      <div>Average Length: {stats.averageLength.toFixed(0)} characters</div>
    </div>
  );
}
```

### 3. Persistent State

```typescript
export function useLocalStorage<T>(key: string, initialValue: T) {
  // State to store our value
  // Pass initial state function to useState so logic is only executed once
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Return a wrapped version of useState's setter function that ...
  // ... persists the new value to localStorage.
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      // Allow value to be a function so we have same API as useState
      const valueToStore = value instanceof Function ? value(storedValue) : value;

      // Save state
      setStoredValue(valueToStore);

      // Save to localStorage
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue] as const;
}

// Usage
export function ThemeToggle() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');

  return (
    <button onClick={() => setTheme(t => t === 'light' ? 'dark' : 'light')}>
      Current theme: {theme}
    </button>
  );
}
```

## Best Practices

1. **State Location**

   - Keep state as close to where it's used as possible
   - Lift state up only when necessary
   - Use context sparingly and only for truly global state

2. **Performance**

   - Use appropriate memoization techniques
   - Implement proper dependency arrays
   - Split context if different parts of the app need different updates

3. **Type Safety**

   - Define proper types for all state
   - Use discriminated unions for complex state
   - Leverage TypeScript's type inference

4. **Data Flow**
   - Maintain unidirectional data flow
   - Implement proper error boundaries
   - Handle loading and error states consistently

## Common Patterns

### 1. Loading States

```typescript
export function useLoadingState() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = async <T>(promise: Promise<T>): Promise<T> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await promise;
      return result;
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { isLoading, error, execute };
}

// Usage
export function PostAction() {
  const { isLoading, error, execute } = useLoadingState();
  const mutation = api.post.create.useMutation();

  const handleClick = async () => {
    try {
      await execute(mutation.mutateAsync({ title: 'New Post' }));
      // Success handling
    } catch (error) {
      // Error already set in useLoadingState
    }
  };

  return (
    <div>
      <button onClick={handleClick} disabled={isLoading}>
        {isLoading ? 'Creating...' : 'Create Post'}
      </button>
      {error && <div className="error">{error.message}</div>}
    </div>
  );
}
```

### 2. Form State Management

```typescript
export function useFormState<T extends object>(initialState: T) {
  const [state, setState] = useState<T>(initialState);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setState(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const reset = () => setState(initialState);

  return {
    state,
    handleChange,
    reset,
    setState
  };
}

// Usage
export function PostForm() {
  const { state, handleChange, reset } = useFormState({
    title: '',
    content: ''
  });

  const mutation = api.post.create.useMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await mutation.mutateAsync(state);
    reset();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="title"
        value={state.title}
        onChange={handleChange}
      />
      <textarea
        name="content"
        value={state.content}
        onChange={handleChange}
      />
      <button type="submit">Submit</button>
    </form>
  );
}
```
