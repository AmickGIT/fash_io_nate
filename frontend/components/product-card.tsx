"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Image from "next/image"

interface ProductCardProps {
  product: { img_path: string; image_url: string }
  onBuyClick: (img_path: string) => void
  onNotInterestedClick: (img_path: string) => void
}

export default function ProductCard({ product, onBuyClick, onNotInterestedClick }: ProductCardProps) {
  return (
    <Card className="group hover:shadow-lg transition-shadow duration-300 overflow-hidden">
      <div className="relative flex flex-col items-center justify-center">
        <Image
          src={product.image_url}
          alt={product.img_path}
          width={189} // 758/4
          height={256} // 1024/4
          className="object-cover rounded-t"
        />
      </div>
      <CardContent className="p-4 flex flex-col items-center">
        <div className="flex gap-2 w-full">
          <Button
            onClick={() => onBuyClick(product.img_path)}
            className="flex-1 bg-pink-600 hover:bg-pink-700 text-white"
            size="sm"
          >
            Buy
          </Button>
          <Button
            onClick={() => onNotInterestedClick(product.img_path)}
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
