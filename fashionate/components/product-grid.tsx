"use client"

import { useState } from "react"
import ProductCard from "./product-card"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"

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
  const [uniquenessValue, setUniquenessValue] = useState([50]) // Default value for slider

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

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <nav className="text-sm text-gray-600 mb-2">Home / Clothing / Dresses</nav>
          <h1 className="text-2xl font-semibold text-gray-900">Dresses - {products.length.toLocaleString()} items</h1>
        </div>
        <div className="flex items-center gap-4 w-64">
          {" "}
          {/* Added w-64 for slider width */}
          <Label htmlFor="uniqueness-bar" className="text-sm text-gray-600 whitespace-nowrap">
            Uniqueness Bar:
          </Label>
          <Slider
            id="uniqueness-bar"
            min={0}
            max={100}
            step={1}
            value={uniquenessValue}
            onValueChange={setUniquenessValue}
            className="w-full"
          />
          <span className="text-sm text-gray-600">{uniquenessValue[0]}%</span>
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
