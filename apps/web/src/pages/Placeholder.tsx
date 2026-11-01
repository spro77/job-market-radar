/** A page that exists in the navigation but has no screen yet. */
export function Placeholder({ title }: { title: string }) {
  return (
    <main className="mx-auto flex max-w-336 flex-col gap-2 px-4 py-8 md:px-12">
      <h1 className="m-0 font-display text-[40px] leading-11 font-semibold tracking-[-0.015em]">
        {title}
      </h1>
      <p className="m-0 text-[15px] text-ink-muted">This screen is coming in a later step.</p>
    </main>
  )
}
