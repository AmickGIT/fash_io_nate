"use client"

import Header from "@/components/header"
import Sidebar from "@/components/sidebar"
import ProductGrid from "@/components/product-grid"
import { Suspense, useState } from "react"

export default function RecommenderPage() {
  const [selectedFilters, setSelectedFilters] = useState<{
    gender: string[];
    categories: string[];
    brands: string[];
    dressCode: string[];
    color: string[];
    sleeves: string[];
    fit: string[];
    neckline: string[];
  }>({
    gender: ["women"],
    categories: [],
    brands: [],
    dressCode: [],
    color: [],
    sleeves: [],
    fit: [],
    neckline: [],
  })
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-6">
        <div className="flex gap-6">
          <aside className="w-64 flex-shrink-0">
            <Sidebar selectedFilters={selectedFilters} setSelectedFilters={setSelectedFilters} />
          </aside>
          <div className="flex-1">
            <Suspense fallback={<div>Loading products...</div>}>
              <ProductGrid selectedFilters={selectedFilters} />
            </Suspense>
          </div>
        </div>
      </main>
    </div>
  )
}
