import * as TabsPrimitive from '@radix-ui/react-tabs'
import type { ComponentProps } from 'react'
import { cn } from '../lib/cn'

// shadcn/ui Tabs on Radix, drawn like the design system's SegmentedControl. Use Tabs when the
// choice swaps a panel (a chart's measure); SegmentedControl when it sets a value (a filter).

export function Tabs(props: ComponentProps<typeof TabsPrimitive.Root>) {
  return <TabsPrimitive.Root {...props} />
}

export function TabsList({ className, ...props }: ComponentProps<typeof TabsPrimitive.List>) {
  return (
    <TabsPrimitive.List
      className={cn(
        'inline-flex gap-0.5 rounded-md border border-border bg-surface-sunken p-[3px]',
        className,
      )}
      {...props}
    />
  )
}

export function TabsTrigger({ className, ...props }: ComponentProps<typeof TabsPrimitive.Trigger>) {
  return (
    <TabsPrimitive.Trigger
      className={cn(
        'h-7 cursor-pointer rounded-[6px] border-0 bg-transparent px-3 font-text text-[13px] font-medium text-ink-muted hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus-ring',
        'data-[state=active]:bg-surface-raised data-[state=active]:text-ink data-[state=active]:shadow-[var(--shadow-sm),inset_0_0_0_1px_var(--border)]',
        className,
      )}
      {...props}
    />
  )
}

export function TabsContent({ className, ...props }: ComponentProps<typeof TabsPrimitive.Content>) {
  return <TabsPrimitive.Content className={cn('outline-none', className)} {...props} />
}
