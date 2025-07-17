import Header from "@/components/header"
import Sidebar from "@/components/sidebar"
import ProductGrid from "@/components/product-grid"
import { Suspense } from "react"

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-6">
        <div className="flex gap-6">
          <aside className="w-64 flex-shrink-0">
            <Sidebar />
          </aside>
          <div className="flex-1">
            <Suspense fallback={<div>Loading products...</div>}>
              <ProductGrid />
            </Suspense>
          </div>
        </div>
      </main>
    </div>
  )
}
