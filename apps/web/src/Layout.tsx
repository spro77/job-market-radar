import { cn, SegmentedControl } from '@radar/ui'
import { Link, NavLink, Outlet, useLocation } from 'react-router'
import { useFilters } from './lib/filters.ts'

const NAV = [
  { to: '/', label: 'Overview' },
  { to: '/skills', label: 'Skills' },
  { to: '/salaries', label: 'Salaries' },
]

const COUNTRY_OPTIONS = [
  { value: 'all', label: 'CA + US' },
  { value: 'CA', label: 'Canada' },
  { value: 'US', label: 'US' },
]

/** Top bar with the country filter, shared by every page. Links keep the current filters. */
export function Layout() {
  const { search } = useLocation()
  const [filters, setFilters] = useFilters()

  return (
    <div className="min-h-screen bg-bg font-text text-ink">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-border bg-surface px-4 py-3 md:px-12">
        <div className="flex flex-wrap items-center gap-8">
          <Link
            to={{ pathname: '/', search }}
            className="flex items-center gap-2.5 text-ink no-underline"
          >
            <Logo />
            <span className="font-display text-lg font-semibold tracking-[-0.01em]">
              Job Market Radar
            </span>
          </Link>
          <nav aria-label="Main" className="flex flex-wrap gap-1">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={{ pathname: item.to, search }}
                end
                className={({ isActive }) =>
                  cn(
                    'inline-flex h-8 items-center rounded-md px-3 text-sm font-medium no-underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus-ring',
                    isActive
                      ? 'bg-surface-raised text-ink shadow-[inset_0_-2px_0_var(--accent)]'
                      : 'text-ink-muted hover:bg-surface-raised hover:text-ink',
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
        <SegmentedControl
          label="Country"
          options={COUNTRY_OPTIONS}
          value={filters.country ?? 'all'}
          onChange={(value) =>
            setFilters({ country: value === 'all' ? undefined : (value as 'CA' | 'US') })
          }
        />
      </header>
      <Outlet />
    </div>
  )
}

function Logo() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true">
      <circle
        cx="14"
        cy="14"
        r="12"
        fill="none"
        stroke="var(--accent)"
        strokeWidth="2"
        opacity="0.35"
      />
      <circle
        cx="14"
        cy="14"
        r="7.5"
        fill="none"
        stroke="var(--accent)"
        strokeWidth="2"
        opacity="0.65"
      />
      <circle cx="14" cy="14" r="3" fill="var(--accent)" />
      <path d="M14 14 L23 5" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}
