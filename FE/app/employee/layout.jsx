import { Suspense } from "react"
import { Shell } from "@/components/shell"

// Suspense: Shell reads the route (usePathname/useParams), which is dynamic under cacheComponents.
export default function EmployeeLayout({ children }) {
  return (
    <Suspense>
      <Shell roles={["employee"]}>{children}</Shell>
    </Suspense>
  )
}
