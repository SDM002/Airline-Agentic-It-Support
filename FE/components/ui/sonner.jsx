"use client"
import { Toaster as Sonner } from "sonner"
// Single light theme (no next-themes).
export function Toaster(props) {
  return (
    <Sonner
      theme="light"
      position="bottom-right"
      toastOptions={{
        style: { background: "#ffffff", border: "1px solid #9fd0ee", color: "#1e293b", borderRadius: 6 },
      }}
      {...props}
    />
  )
}
