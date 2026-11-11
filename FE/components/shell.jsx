"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { useEffect, useSyncExternalStore } from "react"
import { LogOut, PlaneTakeoff } from "lucide-react"
import { Button } from "@/components/ui/button"
import { getSession, logout } from "@/lib/api"
import { cn } from "@/lib/utils"

export const HOME = { employee: "/employee/chat", it_support: "/support/dashboard", manager: "/support/approvals" }
const ROLE_LABEL = { employee: "Employee", it_support: "IT Support", manager: "Manager" }
const NAV = {
  employee: [["/employee/chat", "Chat"], ["/employee/my-tickets", "My tickets"]],
  it_support: [["/support/dashboard", "Dashboard"], ["/support/tickets", "Tickets"], ["/support/approvals", "Approvals"]],
  manager: [["/support/approvals", "Approvals"]],
}
const ring = "outline-none focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
const noop = () => () => {}

/** Current session: undefined while rendering on the server, null when logged out. */
export function useSession() {
  return useSyncExternalStore(noop, getSession, () => undefined)
}

/** Floating header + client-side role guard. The backend enforces the same roles on every API call. */
export function Shell({ roles, children }) {
  const router = useRouter()
  const path = usePathname()
  const session = useSession()
  const role = session?.role
  const allowed = roles.includes(role) && NAV[role]?.some(([href]) => path.startsWith(href))

  useEffect(() => {
    if (session === null) router.replace("/login")
    else if (session && !allowed) router.replace(HOME[session.role])
  }, [router, session, allowed])

  if (!allowed) return null

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-border bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-8 px-4 sm:px-8">
          <Link href={HOME[role]} data-testid="header-brand-link" className={cn("flex h-14 items-center gap-2 rounded-md font-heading text-lg font-bold tracking-tighter text-heading", ring)}>
            <PlaneTakeoff className="size-5 text-primary" />
            SkyDesk<span className="text-primary">AI</span>
          </Link>
          <nav className="order-last -mx-4 flex w-[calc(100%+2rem)] overflow-x-auto border-t border-border px-4 sm:order-none sm:mx-0 sm:w-auto sm:border-0 sm:px-0">
            {NAV[role].map(([href, label]) => (
              <Link
                key={href}
                href={href}
                data-testid={`nav-${label.toLowerCase().replace(" ", "-")}-link`}
                className={cn(
                  "flex h-11 items-center border-b-2 px-3 text-sm whitespace-nowrap transition-colors duration-200 sm:h-14",
                  path.startsWith(href) ? "border-sky-600 text-heading" : "border-transparent text-muted-foreground hover:text-heading",
                  ring,
                )}
              >
                {label}
              </Link>
            ))}
          </nav>
          <div className="ml-auto flex h-14 items-center gap-3">
            <div className="hidden text-right leading-tight md:block">
              <div className="text-sm text-heading">{session.name}</div>
              <div className="text-xs text-muted-foreground">{session.title}</div>
            </div>
            <span data-testid="header-role-badge" className="rounded-sm border border-primary/40 px-2 py-0.5 font-mono text-xs text-primary">
              {ROLE_LABEL[role]}
            </span>
            <Button
              variant="ghost"
              size="icon"
              aria-label="Log out"
              data-testid="header-logout-button"
              onClick={() => {
                logout()
                router.replace("/login")
              }}
            >
              <LogOut />
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-8 sm:py-12">{children}</main>
    </>
  )
}
