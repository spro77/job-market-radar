import { createBrowserRouter } from 'react-router'
import { Layout } from './Layout.tsx'
import { Overview } from './pages/Overview.tsx'
import { Placeholder } from './pages/Placeholder.tsx'

// Data router. Static Web Apps rewrites every path to index.html, so deep links work.
export const router = createBrowserRouter([
  {
    path: '/',
    Component: Layout,
    children: [
      { index: true, Component: Overview },
      { path: 'skills', element: <Placeholder title="Skills" /> },
      { path: 'salaries', element: <Placeholder title="Salaries" /> },
      { path: '*', element: <Placeholder title="Page not found" /> },
    ],
  },
])
