"use client"

import Header from "@/components/header"
import Sidebar from "@/components/sidebar"
import ProductGrid from "@/components/product-grid"
import { Suspense, useState } from "react"

interface Filters {
  gender: string[];
  categories: string[];
  brands: string[];
  dressCode: string[];
  color: string[];
  sleeves: string[];
  fit: string[];
  neckline: string[];
}

export default function Home() {
  const [selectedFilters, setSelectedFilters] = useState<Filters>({
    gender: ["women"],
    categories: [],
    brands: [],
    dressCode: [],
    color: [],
    sleeves: [],
    fit: [],
    neckline: [],
  })
  const [wardrobeCount, setWardrobeCount] = useState(0)

  const handleWardrobeUpdate = (newCount?: number) => {
    if (typeof newCount === "number") {
      setWardrobeCount(newCount)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header wardrobeCount={wardrobeCount} onWardrobeUpdate={handleWardrobeUpdate} />
      <main className="container mx-auto px-4 py-6">
        <div className="flex gap-6">
          <aside className="w-64 flex-shrink-0">
            <Sidebar selectedFilters={selectedFilters} setSelectedFilters={setSelectedFilters} />
          </aside>
          <div className="flex-1">
            <Suspense fallback={<div>Loading products...</div>}>
              <ProductGrid selectedFilters={selectedFilters} onWardrobeUpdate={handleWardrobeUpdate} />
            </Suspense>
          </div>
        </div>
      </main>
    </div>
  )
}
