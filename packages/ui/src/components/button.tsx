import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { cn } from '../lib/cn'

// shadcn/ui Button with the design system's variants: primary once per view, secondary by
// default, ghost for toolbars. md = 36px, sm = 28px.
const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md border font-text font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus-ring disabled:cursor-not-allowed disabled:opacity-45 cursor-pointer',
  {
    variants: {
      variant: {
        primary: 'border-accent bg-accent text-on-accent hover:brightness-110',
        secondary: 'border-border-strong bg-surface-raised text-ink hover:border-ink-muted',
        ghost:
          'border-transparent bg-transparent text-ink-muted hover:bg-surface-raised hover:text-ink',
      },
      size: {
        md: 'h-9 px-4 text-sm',
        sm: 'h-7 px-3 text-[13px]',
      },
    },
    defaultVariants: { variant: 'secondary', size: 'md' },
  },
)

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  /** Optional 16px icon before the label. */
  icon?: ReactNode
  /** Render the child element (a link) with button styles instead of a <button>. */
  asChild?: boolean
}

export function Button({
  className,
  variant,
  size,
  icon,
  asChild,
  children,
  ...props
}: ButtonProps) {
  const classes = cn(buttonVariants({ variant, size }), className)
  if (asChild)
    return (
      <Slot className={classes} {...props}>
        {children}
      </Slot>
    )
  return (
    <button type="button" className={classes} {...props}>
      {icon && (
        <span className="inline-flex size-4 items-center justify-center" aria-hidden>
          {icon}
        </span>
      )}
      <span>{children}</span>
    </button>
  )
}
