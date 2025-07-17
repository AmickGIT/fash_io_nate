"use client"

import { Heart, Star } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import Image from "next/image"

interface Product {
  id: number
  brand: string
  name: string
  image: string
  rating: number
  reviews: number
  currentPrice: number
  originalPrice: number
  discount: number
  isWishlisted: boolean
}

interface ProductCardProps {
  product: Product
  onWishlistToggle: (productId: number) => void
  onBuyClick: (productId: number) => void
  onNotInterestedClick: (productId: number) => void
}

export default function ProductCard({ product, onWishlistToggle, onBuyClick, onNotInterestedClick }: ProductCardProps) {
  return (
    <Card className="group hover:shadow-lg transition-shadow duration-300 overflow-hidden">
      <div className="relative">
        <Image
          src={product.image || "/placeholder.svg"}
          alt={product.name}
          width={250}
          height={300}
          className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
        />

        {/* Wishlist Heart */}
        <button
          onClick={() => onWishlistToggle(product.id)}
          className="absolute top-3 right-3 p-2 bg-white rounded-full shadow-md hover:shadow-lg transition-shadow"
        >
          <Heart
            className={`w-5 h-5 ${
              product.isWishlisted ? "fill-red-500 text-red-500" : "text-gray-400 hover:text-red-500"
            }`}
          />
        </button>
      </div>

      <CardContent className="p-4">
        {/* Rating */}
        

        {/* Brand */}
        <h3 className="font-semibold text-gray-900 mb-1">{product.brand}</h3>

        {/* Product Name */}
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{product.name}</p>

        {/* Price */}
        

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            onClick={() => onBuyClick(product.id)}
            className="flex-1 bg-pink-600 hover:bg-pink-700 text-white"
            size="sm"
          >
            Buy
          </Button>
          <Button
            onClick={() => onNotInterestedClick(product.id)}
            variant="outline"
            className="flex-1 border-gray-300 text-gray-700 hover:bg-gray-50"
            size="sm"
          >
            Not Interested
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
