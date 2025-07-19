"use client"

import { Card } from "@/components/ui/card"
import Image from "next/image"

interface ProductCardProps {
  product: { img_path: string; image_url: string }
}

export default function ProductCard({ product }: ProductCardProps) {
  return (
    <Card className="group hover:shadow-lg transition-shadow duration-300 overflow-hidden">
      <div className="relative">
        <Image
          src={product.image_url}
          alt={product.img_path}
          width={250}
          height={300}
          className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
        />
      </div>
    </Card>
  )
}
