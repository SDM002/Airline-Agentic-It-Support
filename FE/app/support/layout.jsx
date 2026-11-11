import { Suspense } from "react"
import { Shell } from "@/components/shell"

// Suspense: Shell reads the route (usePathname/useParams), which is dynamic under cacheComponents.
export default function SupportLayout({ children }) {
  return (
    <Suspense>
      <Shell roles={["it_support", "manager"]}>{children}</Shell>
    </Suspense>
  )
}
