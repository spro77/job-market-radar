import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router'
import './index.css'
import { router } from './router.tsx'

// Aggregates change once a day and the API caches for an hour: refetching on every focus
// would only repeat the same answer.
const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 10 * 60_000, refetchOnWindowFocus: false } },
})

const root = document.getElementById('root')
if (!root) throw new Error('#root is missing from index.html')

createRoot(root).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
)
