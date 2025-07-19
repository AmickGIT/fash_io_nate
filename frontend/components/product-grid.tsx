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

  const handleBuyClick = (img_path: string) => {
    console.log(`Buy clicked for image ${img_path}`)
    // Implement buy functionality
  }

  const handleNotInterestedClick = (img_path: string) => {
    console.log(`Not interested clicked for image ${img_path}`)
    setProducts((prev) => prev.filter((product) => product.img_path !== img_path))
  }

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
        <div className="justify-self-center">
          <Button
            onClick={toggleMatchStyle}
            variant="outline"
            className={`px-8 py-2 h-9 rounded-full text-sm font-medium transition-all duration-200 border-2 ${
              isMatchStyleActive
                ? "bg-pink-600 border-pink-600 text-white hover:bg-pink-700 hover:border-pink-700 shadow-md"
                : "bg-white border-gray-300 text-gray-700 hover:border-pink-300 hover:text-pink-600 hover:bg-pink-50"
            }`}
          >
            Match my Style
          </Button>
        </div>
        <div className="justify-self-end flex items-center gap-4 w-64">
          <Label htmlFor="uniqueness-bar" className="text-sm text-gray-600 whitespace-nowrap">
            Uniqueness:
          </Label>
          <Slider
            id="uniqueness-bar"
            min={0}
            max={100}
            step={50}
            value={uniquenessLevel}
            onValueChange={setUniquenessLevel}
            className="text-left w-4/12"
          />
          <span className="text-sm text-gray-600 text-right">{getUniquenessLabel(uniquenessLevel[0])}</span>
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
              onBuyClick={handleBuyClick}
              onNotInterestedClick={handleNotInterestedClick}
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
