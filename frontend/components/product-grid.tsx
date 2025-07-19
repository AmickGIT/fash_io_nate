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

interface Product {
  id: number;
  img_path: string;
  image_url: string;
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
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uniquenessLevel, setUniquenessLevel] = useState([50]) // Default to Medium
  const [isMatchStyleActive, setIsMatchStyleActive] = useState(false)
  const [nextOffset, setNextOffset] = useState<number | null>(null)

  const handleBuyClick = async (img_path: string, id?: number) => {
    try {
      if (!id) return;
      const res = await fetch("http://localhost:8000/api/buy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
      });
      const data = await res.json();
      if (data.success) {
        setProducts((prev) => prev.filter((product) => product.id !== id));
      } else {
        console.error("Buy failed", data.error);
      }
    } catch (err) {
      console.error("Buy error", err);
    }
  }

  const handleNotInterestedClick = (img_path: string) => {
    console.log(`Not interested clicked for image ${img_path}`)
    setProducts((prev) => prev.filter((product) => product.img_path !== img_path))
  }

  const buildParams = (loadMore = false) => {
    const params = new URLSearchParams()
    selectedFilters.brands.forEach(b => params.append("brand", b));
    selectedFilters.color.forEach(c => params.append("color", c));
    selectedFilters.sleeves.forEach(s => params.append("sleeve", s));
    selectedFilters.fit.forEach(f => params.append("fit", f));
    selectedFilters.neckline.forEach(n => params.append("neckline", n));
    selectedFilters.dressCode.forEach(d => params.append("dress_code", d));
    params.set("limit", "20")
    if (isMatchStyleActive) {
      params.set("match_style", "true")
    }
    if (loadMore && nextOffset != null) {
      params.set("offset", String(nextOffset))
    }
    return params
  }

  const loadProducts = async (loadMore = false) => {
    setLoading(true)
    setError(null)
    try {
      const params = buildParams(loadMore)
      const res = await fetch(`http://localhost:8000/api/products?${params.toString()}`)
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      setProducts(prev => loadMore ? [...prev, ...data.items] : data.items)
      setNextOffset(data.next_offset)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Initial load or when filters or match style changes
  useEffect(() => {
    loadProducts(false)
    // eslint-disable-next-line
  }, [JSON.stringify(selectedFilters), isMatchStyleActive])

  const handleMatchStyleClick = () => {
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
            onClick={handleMatchStyleClick}
            variant={isMatchStyleActive ? "default" : "outline"}
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
      {loading && products.length === 0 ? (
        <div className="text-center py-12 text-gray-500">Loading products...</div>
      ) : error ? (
        <div className="text-center py-12 text-red-500">{error}</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((product) => (
            <ProductCard
              key={product.img_path}
              product={product}
              onBuyClick={(img_path) => handleBuyClick(img_path, product.id)}
              onNotInterestedClick={handleNotInterestedClick}
            />
          ))}
        </div>
      )}

      {/* Load More */}
      {nextOffset != null && !loading && (
        <div className="flex justify-center mt-12">
          <button
            className="px-8 py-3 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors"
            onClick={() => loadProducts(true)}
          >
            Load More Products
          </button>
        </div>
      )}
    </div>
  )
}
