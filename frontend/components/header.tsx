"use client"

import { Search, ShoppingBag, X } from "lucide-react"
import Image from "next/image"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { useState, useEffect, useCallback, SetStateAction, Dispatch } from "react"
import { usePathname } from "next/navigation"
import { API_BASE } from "@/lib/constants"

const navigationTabs = [
  { name: "Recommender", href: "/" },
  { name: "Style Transfer", href:"https://fashionatedesign.streamlit.app/" }
]

interface WardrobeItem {
  img_path: string;
  image_url: string;
  payload?: { bought?: boolean };
}

interface HeaderProps {
  wardrobeCount?: number;
  onWardrobeUpdate?: (newCount?: number) => void;
  searchQuery: string;
  setSearchQuery: Dispatch<SetStateAction<string>>;
  onSearch: (query: string) => void;
  onClearSearch: () => void;
}

export default function Header({ wardrobeCount = 0, onWardrobeUpdate, searchQuery, onSearch, onClearSearch }: HeaderProps) {
  const [showWardrobe, setShowWardrobe] = useState(false)
  const [wardrobeItems, setWardrobeItems] = useState<WardrobeItem[]>([])
  const pathname = usePathname() // Get the current path

  // Local state for the search input
  const [inputValue, setInputValue] = useState(searchQuery)
  useEffect(() => {
    setInputValue(searchQuery)
  }, [searchQuery])

  // Fetch wardrobe items and update count
  const fetchWardrobe = useCallback(() => {
    fetch(`${API_BASE}/api/wardrobe?limit=10000`)
      .then(res => res.json())
      .then((data: WardrobeItem[]) => {
        const items = Array.isArray(data) ? data : []
        setWardrobeItems(items)
        onWardrobeUpdate?.(items.length)
      })
      .catch(() => {
        setWardrobeItems([])
        onWardrobeUpdate?.(0)
      })
  }, [onWardrobeUpdate])

  // Fetch on mount
  useEffect(() => {
    fetchWardrobe()
  }, [fetchWardrobe])

  // Fetch when wardrobe panel toggles open
  useEffect(() => {
    if (showWardrobe) {
      fetchWardrobe()
    }
  }, [showWardrobe, fetchWardrobe])

  return (
    <header className="bg-white shadow-sm border-b relative">
      {/* Main Header */}
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center">
            <div className="w-10 h-10 bg-gradient-to-r from-pink-500 to-orange-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">F</span>
            </div>
            <span className="ml-2 text-xl font-bold text-gray-800">fashionate</span>
          </Link>

          {/* Search Bar */}
          <div className="flex-1 max-w-md mx-8">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                type="text"
                placeholder="Search for products, brands and more"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    onSearch(inputValue)
                  }
                }}
                className="pl-10 pr-10 w-full"
              />
              {inputValue && (
                <button
                  onClick={() => {
                    setInputValue("")
                    onClearSearch()
                  }}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* User Actions */}
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              className="flex flex-col items-center p-2 relative"
              onClick={() => setShowWardrobe(!showWardrobe)}
            >
              <ShoppingBag className="w-5 h-5" />
              <span className="text-xs mt-1">Wardrobe</span>
              <Badge
                variant="destructive"
                className="absolute -top-1 -right-1 w-5 h-5 rounded-full p-0 flex items-center justify-center text-xs"
              >
                {wardrobeCount}
              </Badge>
            </Button>
          </div>
        </div>
      </div>

      {/* Secondary Navigation */}
      <div className="border-t bg-gray-50">
        <div className="container mx-auto px-4">
          <nav className="flex items-center space-x-8 h-12">
            {navigationTabs.map((tab) => (
              <Link
                key={tab.name}
                href={tab.href}
                className={`text-sm font-medium transition-colors ${
                  pathname === tab.href
                    ? "text-pink-600 border-b-2 border-pink-600"
                    : "text-gray-600 hover:text-pink-600"
                }`}
              >
                {tab.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>
      {showWardrobe && (
        <div className="absolute top-full left-0 right-0 bg-white shadow-lg border-t z-50">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">My Wardrobe</h2>
              <Button
                variant="outline"
                size="sm"
                className="text-pink-600 border-pink-600 hover:bg-pink-50 bg-transparent"
              >
                Add New Item
              </Button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4 max-h-96 overflow-y-auto">
              {wardrobeItems.length === 0 ? (
                <div className="text-gray-400 text-xs col-span-full">No wardrobe items found.</div>
              ) : (
                wardrobeItems.map((item: WardrobeItem) => (
                  <div key={item.img_path} className="bg-gray-50 rounded-lg p-3 hover:shadow-md transition-shadow flex flex-col items-center">
                    <div className="relative w-full" style={{ aspectRatio: '189/256' }}>
                      <Image
                        src={item.image_url}
                        alt={item.img_path}
                        fill
                        style={{ objectFit: 'cover' }}
                        className="rounded-t"
                      />
                    </div>
                    <p className="text-xs text-gray-600 truncate w-full">{item.img_path}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
