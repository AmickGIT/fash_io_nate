"use client"

import { useState, useEffect } from "react"
import ProductCard from "./product-card"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"

interface ProductGridProps {
  selectedFilters?: {
    gender: string[];
    categories: string[];
    brands: string[];
    dressCode: string[];
    color: string[];
    sleeves: string[];
    fit: string[];
    neckline: string[];
  }
}

const defaultFilters = {
  gender: [],
  categories: [],
  brands: [],
  dressCode: [],
  color: [],
  sleeves: [],
  fit: [],
  neckline: [],
};

export default function ProductGrid({ selectedFilters = defaultFilters }: ProductGridProps) {
  const [products, setProducts] = useState<{ img_path: string; image_url: string }[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uniquenessLevel, setUniquenessLevel] = useState([50]) // Default to Medium
  const [isMatchStyleActive, setIsMatchStyleActive] = useState(false)

  useEffect(() => {
    if (!selectedFilters) return;
    setLoading(true)
    setError(null)
    // Build query params from selectedFilters
    const params = new URLSearchParams()
    if (selectedFilters.brands.length > 0) params.append("brand", selectedFilters.brands[0])
    if (selectedFilters.color.length > 0) params.append("color", selectedFilters.color[0])
    if (selectedFilters.sleeves.length > 0) params.append("sleeve", selectedFilters.sleeves[0])
    if (selectedFilters.fit.length > 0) params.append("fit", selectedFilters.fit[0])
    if (selectedFilters.neckline.length > 0) params.append("neckline", selectedFilters.neckline[0])
    if (selectedFilters.dressCode.length > 0) params.append("dress_code", selectedFilters.dressCode[0])
    fetch(`http://localhost:8000/api/products?${params.toString()}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch products")
        return res.json()
      })
      .then((data) => {
        setProducts(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [selectedFilters])

  const handleWishlistToggle = (productId: number) => {
    setProducts((prev) =>
      prev.map((product) => (product.id === productId ? { ...product, isWishlisted: !product.isWishlisted } : product)),
    )
  }

  const handleBuyClick = (productId: number) => {
    console.log(`Buy clicked for product ${productId}`)
    // Implement buy functionality
  }

  const handleNotInterestedClick = (productId: number) => {
    console.log(`Not interested clicked for product ${productId}`)
    // Implement not interested functionality
    setProducts((prev) => prev.filter((product) => product.id !== productId))
  }

  const toggleMatchStyle = () => {
    setIsMatchStyleActive((prev) => !prev)
  }

  const getUniquenessLabel = (value: number) => {
    if (value === 0) return "Low"
    if (value === 50) return "Medium"
    if (value === 100) return "High"
    return "" // Should not happen with step 50
  }

  return (
    <div>
      {/* Header */}
      <div className="grid grid-cols-3 items-center mb-6">
        <div className="justify-self-start">
          <h1 className="text-2xl font-semibold text-gray-900">Items - {products.length.toLocaleString()} items</h1>
        </div>
      </div>
      {/* Product Grid */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading products...</div>
      ) : error ? (
        <div className="text-center py-12 text-red-500">{error}</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((product) => (
            <ProductCard
              key={product.img_path}
              product={product}
            />
          ))}
        </div>
      )}

      {/* Load More */}
      <div className="flex justify-center mt-12">
        <button className="px-8 py-3 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors">
          Load More Products
        </button>
      </div>
    </div>
  )
}
