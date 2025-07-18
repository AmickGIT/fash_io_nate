"use client"

import { useState } from "react"
import ProductCard from "./product-card"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"

// Mock product data
const mockProducts = [
  {
    id: 1,
    brand: "anayna",
    name: "Women Fit & Flared Dresses",
    image: "/placeholder.svg?height=300&width=250",
    rating: 4.3,
    reviews: 1200,
    currentPrice: 883,
    originalPrice: 3840,
    discount: 77,
    isWishlisted: false,
  },
  {
    id: 2,
    brand: "Claura",
    name: "Women Fit & Flare Midi Dress",
    image: "/placeholder.svg?height=300&width=250",
    rating: 4.3,
    reviews: 2700,
    currentPrice: 724,
    originalPrice: 2899,
    discount: 75,
    isWishlisted: true,
  },
  {
    id: 3,
    brand: "Antheaa",
    name: "Women Embellished Maxi Dress",
    image: "/placeholder.svg?height=300&width=250",
    rating: 4.3,
    reviews: 271,
    currentPrice: 2029,
    originalPrice: 3499,
    discount: 42,
    isWishlisted: false,
  },
  {
    id: 4,
    brand: "OCTICS",
    name: "Floral Fit & Flare Dress",
    image: "/placeholder.svg?height=300&width=250",
    rating: 4.3,
    reviews: 2400,
    currentPrice: 945,
    originalPrice: 4299,
    discount: 78,
    isWishlisted: false,
  },
  {
    id: 5,
    brand: "Stylum",
    name: "Floral Print Fit & Flare Maxi Dress",
    image: "/placeholder.svg?height=300&width=250",
    rating: 4.2,
    reviews: 3500,
    currentPrice: 757,
    originalPrice: 2899,
    discount: 74,
    isWishlisted: true,
  },
  {
    id: 6,
    brand: "FashionForward",
    name: "Elegant Evening Dress",
    image: "/placeholder.svg?height=300&width=250",
    rating: 4.5,
    reviews: 1800,
    currentPrice: 1299,
    originalPrice: 4999,
    discount: 74,
    isWishlisted: false,
  },
]

export default function ProductGrid() {
  const [products, setProducts] = useState(mockProducts)
  const [uniquenessLevel, setUniquenessLevel] = useState([50]) // Default to Medium
  const [isMatchStyleActive, setIsMatchStyleActive] = useState(false)

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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {products.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            onWishlistToggle={handleWishlistToggle}
            onBuyClick={handleBuyClick}
            onNotInterestedClick={handleNotInterestedClick}
          />
        ))}
      </div>

      {/* Load More */}
      <div className="flex justify-center mt-12">
        <button className="px-8 py-3 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors">
          Load More Products
        </button>
      </div>
    </div>
  )
}
