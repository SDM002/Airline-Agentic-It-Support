import { Geist, JetBrains_Mono, Outfit } from "next/font/google"
import { Toaster } from "@/components/ui/sonner"
import "./globals.css"
const geist = Geist({ variable: "--font-geist", subsets: ["latin"] })
const outfit = Outfit({ variable: "--font-outfit", subsets: ["latin"] })
const mono = JetBrains_Mono({ variable: "--font-jetbrains", subsets: ["latin"] })
export const metadata = {
  title: "SkyDesk AI",
  description: "AI IT Service Desk Agent — airline IT support POC",
}
export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${geist.variable} ${outfit.variable} ${mono.variable}`}>
      <body className="min-h-dvh">
        {children}
        <Toaster />
      </body>
    </html>
  )
}
