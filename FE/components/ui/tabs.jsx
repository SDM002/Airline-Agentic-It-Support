"use client"
import * as React from "react"
import { cn } from "cn"
import { Tabs as TabsPrimitive } from "radix-ui"
// Flat, VS Code-style tabs: no pills, blue underline on the active tab.
function Tabs({ className, ...props }) {
  return <TabsPrimitive.Root data-slot="tabs" className={cn("flex flex-col", className)} {...props} />
}
function TabsList({ className, ...props }) {
  return (
    <TabsPrimitive.List
      data-slot="tabs-list"
      className={cn("flex w-full overflow-x-auto border-b border-border", className)}
      {...props}
    />
  )
}
function TabsTrigger({ className, ...props }) {
  return (
    <TabsPrimitive.Trigger
      data-slot="tabs-trigger"
      className={cn(
        "-mb-px inline-flex items-center gap-2 border-b-2 border-transparent px-4 py-2.5 text-sm whitespace-nowrap text-muted-foreground transition-colors duration-200 outline-none hover:text-heading focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2 focus-visible:ring-offset-background data-[state=active]:border-sky-600 data-[state=active]:text-heading [&_svg]:size-4",
        className,
      )}
      {...props}
    />
  )
}
function TabsContent({ className, ...props }) {
  return (
    <TabsPrimitive.Content data-slot="tabs-content" className={cn("pt-6 text-sm outline-none", className)} {...props} />
  )
}
export { Tabs, TabsList, TabsTrigger, TabsContent }
