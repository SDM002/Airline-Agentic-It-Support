"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import { Loader2, LogIn, PlaneTakeoff } from "lucide-react"
import { HOME } from "@/components/shell"
import { Button } from "@/components/ui/button"
import { login } from "@/lib/api"

const field =
  "mt-1.5 w-full rounded-md border border-border bg-card px-3 py-2 text-heading outline-none focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2 focus-visible:ring-offset-background"

export default function LoginPage() {
  const router = useRouter()
  const [employeeId, setEmployeeId] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError("")
    try {
      const user = await login(employeeId.trim().toUpperCase(), password)
      router.push(HOME[user.role])
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <main className="grid min-h-dvh lg:grid-cols-[1.1fr_1fr]">
      <section className="flex flex-col justify-between border-b border-border p-8 sm:p-12 lg:border-r lg:border-b-0">
        <div className="flex items-center gap-2 font-heading text-lg font-bold tracking-tighter text-heading">
          <PlaneTakeoff className="size-5 text-primary" />
          SkyDesk<span className="text-primary">AI</span>
        </div>
        <div className="my-16 max-w-xl">
          <p className="mb-4 font-mono text-xs text-primary">{"// saffron air · it service desk"}</p>
          <h1 className="text-4xl sm:text-6xl">Airline IT issues, triaged before you finish typing.</h1>
          <p className="mt-6 text-muted-foreground">
            Describe the problem in plain language. The agent classifies it, pulls the right SOP, suggests a fix,
            routes the ticket, and waits for a human on anything sensitive.
          </p>
        </div>
        <p className="font-mono text-xs text-muted-foreground">synthetic data · demo only</p>
      </section>

      <section className="flex items-center p-8 sm:p-12">
        <form onSubmit={submit} className="w-full max-w-md">
          <h2 className="text-2xl">Sign in</h2>
          <p className="mt-1 text-sm text-muted-foreground">Use your employee ID and password.</p>

          <label className="mt-8 block text-sm text-heading">
            Employee ID
            <input
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              autoComplete="username"
              required
              data-testid="login-id-input"
              className={field}
            />
          </label>
          <label className="mt-4 block text-sm text-heading">
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
              data-testid="login-password-input"
              className={field}
            />
          </label>

          {error && <p className="mt-4 text-sm text-destructive" role="alert">{error}</p>}

          <Button type="submit" disabled={busy} className="mt-6 w-full" data-testid="login-submit-button">
            {busy ? <Loader2 className="animate-spin" /> : <LogIn />} Sign in
          </Button>
        </form>
      </section>
    </main>
  )
}
