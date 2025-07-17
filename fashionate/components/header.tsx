"use client"

import { Search, User, Heart, ShoppingBag } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { useState } from "react"

const navigationTabs = [
  { name: "Recommender", href: "/recommender", active: true },
  { name: "Virtual Try-On", href: "/virtual-try-on", active: false },
  { name: "Designer", href: "/designer", active: false },
]

const mainCategories = ["MEN", "WOMEN", "KIDS", "HOME", "BEAUTY", "GENZ", "STUDIO"]

export default function Header() {
  const [searchQuery, setSearchQuery] = useState("")

  return (
    <header className="bg-white shadow-sm border-b">
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

          {/* Main Navigation */}
          

          {/* Search Bar */}
          <div className="flex-1 max-w-md mx-8">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                type="text"
                placeholder="Search for products, brands and more"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 w-full"
              />
            </div>
          </div>

          {/* User Actions */}
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" className="flex flex-col items-center p-2">
              <User className="w-5 h-5" />
              <span className="text-xs mt-1">Profile</span>
            </Button>
            <Button variant="ghost" size="sm" className="flex flex-col items-center p-2 relative">
              <Heart className="w-5 h-5" />
              <span className="text-xs mt-1">Wishlist</span>
              <Badge
                variant="destructive"
                className="absolute -top-1 -right-1 w-5 h-5 rounded-full p-0 flex items-center justify-center text-xs"
              >
                3
              </Badge>
            </Button>
            <Button variant="ghost" size="sm" className="flex flex-col items-center p-2 relative">
              <ShoppingBag className="w-5 h-5" />
              <span className="text-xs mt-1">Bag</span>
              <Badge
                variant="destructive"
                className="absolute -top-1 -right-1 w-5 h-5 rounded-full p-0 flex items-center justify-center text-xs"
              >
                2
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
                  tab.active ? "text-pink-600 border-b-2 border-pink-600" : "text-gray-600 hover:text-pink-600"
                }`}
              >
                {tab.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  )
}
