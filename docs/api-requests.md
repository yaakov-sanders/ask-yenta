# API Request Guidelines

## Required: Use React Query for All API Requests

All API requests in this project **must** go through React Query to ensure:
- Consistent data fetching patterns
- Caching and performance optimization
- Automatic refetching and invalidation
- Built-in loading and error states

## Query Key Patterns

Follow these naming conventions for query keys:

- Single entity: `["entityName", id]`
- Entity collection: `["entityName"]`
- User data: `["currentUser"]`
- Filtered or paginated data: `["entityName", { filterParams }]`

## Examples

### Fetching Data

```tsx
// ✅ Correct: Using React Query
const userQuery = useQuery({
  queryKey: ["currentUser"],
  queryFn: UsersService.readUserMe,
})

// ❌ Incorrect: Direct API call
useEffect(() => {
  const fetchUser = async () => {
    const user = await UsersService.readUserMe()
    setUser(user)
  }
  fetchUser()
}, [])
```

### Mutations

```tsx
// ✅ Correct: Using React Query mutation
const createPostMutation = useMutation({
  mutationFn: (data) => PostsService.createPost(data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["posts"] })
  },
})

// ❌ Incorrect: Direct API call
const createPost = async (data) => {
  await PostsService.createPost(data)
  fetchPosts() // Manually refetching
}
```

## Error Handling

Use the provided `handleError` utility to maintain consistent error handling:

```tsx
onError: (err) => {
  handleError(err)
}
```

## Query Client Setup

The QueryClient is configured in `main.tsx` with automatic authentication error handling:

```tsx
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleApiError,
  }),
  mutationCache: new MutationCache({
    onError: handleApiError,
  }),
})
```

The `handleApiError` function automatically redirects to the login page when encountering 401/403 authentication errors:

```tsx
const handleApiError = (error: Error) => {
  if (error instanceof ApiError && [401, 403].includes(error.status)) {
    localStorage.removeItem("access_token")
    window.location.href = "/login"
  }
}
```

## Accessing the QueryClient

To access the QueryClient in your components, use the `useQueryClient` hook:

```tsx
import { useQueryClient } from "@tanstack/react-query"

const YourComponent = () => {
  const queryClient = useQueryClient()
  
  // Now you can use queryClient methods:
  const invalidateData = () => {
    queryClient.invalidateQueries({ queryKey: ["someData"] })
  }
  
  return (...)
}
``` 