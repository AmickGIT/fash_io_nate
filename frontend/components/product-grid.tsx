"use client"

import { useState, useEffect, useMemo, useCallback } from "react"
import ProductCard from "./product-card"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Eye, CheckCircle } from "lucide-react"
import { CardContent } from "@/components/ui/card"
import { API_BASE } from "@/lib/constants"

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
  };
  searchQuery: string;
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

export default function ProductGrid({ selectedFilters = defaultFilters, onWardrobeUpdate, searchQuery }: ProductGridProps & { onWardrobeUpdate?: (wardrobeCount: number) => void }) {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uniquenessLevel, setUniquenessLevel] = useState([50]) // Default to Medium
  const [localuniquenessLevel, setLocaluniquenessLevel] = useState([50]) // Default to Medium
  const [isMatchStyleActive, setIsMatchStyleActive] = useState(false)
  const [nextOffset, setNextOffset] = useState<number | null>(null)
  const [showSuccess, setShowSuccess] = useState(false)

  const handleBuyClick = async (img_path: string, id?: number) => {
    try {
      if (!id) return;
      const res = await fetch(`${API_BASE}/api/buy`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
      });
      const data = await res.json();
      if (data.success) {
        setProducts((prev) => prev.filter((product) => product.id !== id));
        setShowSuccess(true);
        if (onWardrobeUpdate) onWardrobeUpdate(data.wardrobe_count);
      } else {
        console.error("Buy failed", data.error);
      }
    } catch (err) {
      console.error("Buy error", err instanceof Error ? err.message : String(err));
    }
  }

  const handleNotInterestedClick = async (img_path: string, id?: number) => {
    try {
      if (!id) return;
      const res = await fetch(`${API_BASE}/api/not_interested`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
      });
      const data = await res.json();
      if (data.success) {
        setProducts((prev) => prev.filter((product) => product.id !== id));
        console.log(`Not interested clicked for image ${img_path}`);
      } else {
        console.error("Not interested failed", data.error);
      }
    } catch (err) {
      console.error("Not interested error", err instanceof Error ? err.message : String(err));
    }
  }

  const handleViewOrder = () => {
    setShowSuccess(false);
  }

  const selectedFiltersString = useMemo(() => JSON.stringify(selectedFilters), [selectedFilters]);
  const uniqueness = uniquenessLevel[0];
  const buildParams = useCallback(
    (loadMore = false) => {
      const params = new URLSearchParams();
      selectedFilters.brands.forEach(b => params.append("brand", b));
      selectedFilters.color.forEach(c => params.append("color", c));
      selectedFilters.sleeves.forEach(s => params.append("sleeve", s));
      selectedFilters.fit.forEach(f => params.append("fit", f));
      selectedFilters.neckline.forEach(n => params.append("neckline", n));
      selectedFilters.dressCode.forEach(d => params.append("dress_code", d));

      params.set("limit", "20");
      if (searchQuery) params.set("search_query", searchQuery);
      if (isMatchStyleActive) {
        params.set("match_style", "true");
        params.set("uniqueness", String(uniqueness));
      }
      if (loadMore && nextOffset != null) {
        params.set("offset", String(nextOffset));
      }
      return params;
    },
    [
      selectedFilters,
      searchQuery,
      isMatchStyleActive,
      uniqueness,
      nextOffset
    ]
  );

  const loadProducts = useCallback(
    async (loadMore = false) => {
      setLoading(true);
      setError(null);
      try {
        const params = buildParams(loadMore);
        const res = await fetch(`${API_BASE}/api/products?${params.toString()}`);
        const data = await res.json();
        if (res.status === 400 && data.error?.includes("wardrobe")) {
          alert(data.error);
          setIsMatchStyleActive(false);
          return;
        }
        if (!res.ok) throw new Error(data.error || "Something went wrong");

        setProducts(prev =>
          loadMore ? [...prev, ...(data.items || [])] : data.items || []
        );
        setNextOffset(data.next_offset);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    },
    [buildParams]
  );

  useEffect(() => {
    async function reload() {
      await loadProducts(false);
    }
    reload();
  }, [selectedFiltersString, isMatchStyleActive, uniqueness, searchQuery]);


  

  const handleMatchStyleClick = () => {
    setIsMatchStyleActive((prev) => !prev)
  }

  const getUniquenessLabel = (value: number) => {
    if (value === 0) return "Low"
    if (value === 50) return "Medium"
    if (value === 100) return "High"
    return ""
  }

  return (
    <div>
      {/* Success Popup */}
      {showSuccess && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity" onClick={handleViewOrder} />
          <div className="bg-white rounded-lg shadow-lg max-w-sm w-full mx-4 relative z-10">
            <CardContent className="p-6">
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
              </div>
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Purchase Successful!</h2>
              </div>
              <div className="space-y-3">
                <Button
                  onClick={handleViewOrder}
                  className="w-full bg-pink-600 hover:bg-pink-700 text-white font-medium py-3"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Continue Shopping
                </Button>
              </div>
            </CardContent>
          </div>
        </div>
      )}
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
        {isMatchStyleActive && (
          <div className="justify-self-end flex items-center gap-4 w-64">
            <Label htmlFor="uniqueness-bar" className="text-sm text-gray-600 whitespace-nowrap">
              Uniqueness:
            </Label>
            <Slider
              id="uniqueness-bar"
              min={0}
              max={100}
              step={50}
              value={localuniquenessLevel}
              onValueChange={setLocaluniquenessLevel}
              onValueCommit={(val) => { setUniquenessLevel(val); }}
              className="text-left w-4/12"
            />
            <span className="text-sm text-gray-600 text-right">{getUniquenessLabel(uniqueness)}</span>
          </div>
        )}
      </div>
      {loading && products.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-pink-200 border-t-pink-600 rounded-full animate-spin mb-4"></div>
          <p className="text-gray-500">Loading products...</p>
        </div>
      ) : error ? (
        <div className="text-center py-12 text-red-500">{error}</div>
      ) : (
        <div className="relative"> {/* Add relative positioning */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {products.map((product) => (
              <ProductCard
                key={product.img_path}
                product={product}
                onBuyClick={(img_path) => handleBuyClick(img_path, product.id)}
                onNotInterestedClick={(img_path) => handleNotInterestedClick(img_path, product.id)}
              />
            ))}
          </div>
          
          {/* Loading overlay centered over the grid */}
          {loading && products.length > 0 && (
            <div className="absolute inset-0 z-40 flex items-center justify-center backdrop-blur-sm">
              <div className="bg-white rounded-lg shadow-lg border px-4 py-3 sm:px-6 sm:py-4 flex items-center gap-2 sm:gap-3 mx-4">
                <div className="w-5 h-5 sm:w-6 sm:h-6 border-4 border-pink-200 border-t-pink-600 rounded-full animate-spin"></div>
              </div>
            </div>
          )}
  </div>
      )}
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
