import { type KeyboardEvent, type ReactNode, useState } from 'react'
import { cn } from '../lib/cn'

export interface SegmentedOption {
  value: string
  label: ReactNode
}

export interface SegmentedControlProps {
  options: SegmentedOption[]
  /** Accessible name of the group: "Country". */
  label: string
  /** Controlled value; the normal case, because filters live in the URL. */
  value?: string
  defaultValue?: string
  onChange?: (value: string) => void
}

/** Picks one of two to five short options. A radiogroup: Tab enters, ← → move. */
export function SegmentedControl({
  options,
  label,
  value,
  defaultValue,
  onChange,
}: SegmentedControlProps) {
  const [own, setOwn] = useState(defaultValue ?? options[0]?.value)
  const current = value ?? own

  function pick(next: string) {
    if (value == null) setOwn(next)
    onChange?.(next)
  }

  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const step = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0
    if (!step) return
    event.preventDefault()
    const i = options.findIndex((o) => o.value === current)
    const next = options[(i + step + options.length) % options.length]
    if (!next) return
    pick(next.value)
    event.currentTarget.querySelector<HTMLElement>(`[data-value="${next.value}"]`)?.focus()
  }

  return (
    <div
      role="radiogroup"
      aria-label={label}
      onKeyDown={onKeyDown}
      className="inline-flex gap-0.5 rounded-md border border-border bg-surface-sunken p-[3px]"
    >
      {options.map((o) => {
        const on = o.value === current
        return (
          // biome-ignore lint/a11y/useSemanticElements: radio inputs in a fieldset cannot look like this
          <button
            key={o.value}
            type="button"
            role="radio"
            aria-checked={on}
            tabIndex={on ? 0 : -1}
            data-value={o.value}
            onClick={() => pick(o.value)}
            className={cn(
              'h-7 cursor-pointer rounded-[6px] border-0 px-3 font-text text-[13px] font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus-ring',
              on
                ? 'bg-surface-raised text-ink shadow-[var(--shadow-sm),inset_0_0_0_1px_var(--border)]'
                : 'bg-transparent text-ink-muted hover:text-ink',
            )}
          >
            {o.label}
          </button>
        )
      })}
    </div>
  )
}
