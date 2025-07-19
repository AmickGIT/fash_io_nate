"use client"

import { useState, useEffect } from "react"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ChevronDown, ChevronUp } from "lucide-react"

const genderOptions = [
  { id: "women", label: "Women", checked: true },
  { id: "men", label: "Men", checked: false },
  { id: "kids", label: "Kids", checked: false },
]

const categoryOptions = [
  { id: "dresses", label: "Dresses", count: 190947 },
  { id: "ethnic-dresses", label: "Ethnic Dresses", count: 13619 },
  { id: "tops", label: "Tops", count: 45230 },
  { id: "jeans", label: "Jeans", count: 23456 },
]

const brandOptions = [
  { id: "trendyol", label: "Trendyol", count: 7251 },
  { id: "stylecast", label: "StyleCast", count: 6840 },
  { id: "lulu-sky", label: "LULU & SKY", count: 6268 },
  { id: "dressberry", label: "DressBerry", count: 5586 },
  { id: "jc-collection", label: "JC Collection", count: 5189 },
  { id: "baesd", label: "BAESD", count: 4190 },
  { id: "tokyo-talkies", label: "Tokyo Talkies", count: 3818 },
]

const dressCodeOptions = [
  { id: "casual", label: "Casual" },
  { id: "formal", label: "Formal" },
  { id: "party", label: "Party Wear" },
  { id: "business", label: "Business" },
  { id: "vacation", label: "Vacation" },
]

const colorOptions = [
  { id: "black", label: "Black" },
  { id: "white", label: "White" },
  { id: "red", label: "Red" },
  { id: "blue", label: "Blue" },
  { id: "green", label: "Green" },
  { id: "pink", label: "Pink" },
  { id: "yellow", label: "Yellow" },
]

const sleeveOptions = [
  { id: "full-sleeve", label: "Full Sleeve" },
  { id: "half-sleeve", label: "Half Sleeve" },
  { id: "sleeveless", label: "Sleeveless" },
  { id: "3-4-sleeve", label: "3/4 Sleeve" },
]

const fitOptions = [
  { id: "regular", label: "Regular Fit" },
  { id: "slim", label: "Slim Fit" },
  { id: "loose", label: "Loose Fit" },
  { id: "bodycon", label: "Bodycon" },
]

const necklineOptions = [
  { id: "round-neck", label: "Round Neck" },
  { id: "v-neck", label: "V Neck" },
  { id: "boat-neck", label: "Boat Neck" },
  { id: "hal-neck", label: "Hal Neck" },
]

export default function Sidebar() {
  const [expandedSections, setExpandedSections] = useState({
    gender: true,
    categories: true,
    brands: true,
    dressCode: false,
    color: false,
    sleeves: false,
    fit: false,
    neckline: false,
  })

  const [selectedFilters, setSelectedFilters] = useState<{
    gender: string[];
    categories: string[];
    brands: string[];
    dressCode: string[];
    color: string[];
    sleeves: string[];
    fit: string[];
    neckline: string[];
  }>({
    gender: ["women"],
    categories: [],
    brands: [],
    dressCode: [],
    color: [],
    sleeves: [],
    fit: [],
    neckline: [],
  })

  const [brandOptions, setBrandOptions] = useState<Array<{ id: string; label: string; count: number }>>([])
  const [brandsLoading, setBrandsLoading] = useState(true)
  const [brandsError, setBrandsError] = useState<string | null>(null)

  useEffect(() => {
    setBrandsLoading(true)
    fetch("http://localhost:8000/api/brands")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch brands")
        return res.json()
      })
      .then((data) => {
        setBrandOptions(data)
        setBrandsLoading(false)
      })
      .catch((err) => {
        setBrandsError(err.message)
        setBrandsLoading(false)
      })
  }, [])

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  const handleFilterChange = (section: keyof typeof selectedFilters, value: string, checked: boolean) => {
    setSelectedFilters((prev) => ({
      ...prev,
      [section]: checked ? [...prev[section], value] : prev[section].filter((item) => item !== value),
    }))
  }

  const clearAllFilters = () => {
    setSelectedFilters({
      gender: ["women"],
      categories: [],
      brands: [],
      dressCode: [],
      color: [],
      sleeves: [],
      fit: [],
      neckline: [],
    })
  }

  function toCamelCase(str: string) {
    return str.replace(/(^|\s|-)\w/g, match => match.toUpperCase());
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 leading-3">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">FILTERS</h2>
        <Button variant="ghost" size="sm" onClick={clearAllFilters} className="text-pink-600 hover:text-pink-700">
          CLEAR ALL
        </Button>
      </div>

      {/* Gender Filter */}

      {/* Categories Filter */}

      <Separator className="my-4" />

      {/* Brand Filter */}
      <div className="mb-6">
        <button
          onClick={() => toggleSection("brands")}
          className="flex items-center justify-between w-full text-left font-medium text-gray-900 mb-3"
        >
          BRAND
          {expandedSections.brands ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        {expandedSections.brands && (
          <div className="space-y-3 max-h-72 overflow-y-auto pr-1 custom-scrollbar">
            {brandsLoading ? (
              <div className="text-sm text-gray-500">Loading brands...</div>
            ) : brandsError ? (
              <div className="text-sm text-red-500">{brandsError}</div>
            ) : brandOptions.length === 0 ? (
              <div className="text-sm text-gray-500">No brands found.</div>
            ) : (
              brandOptions.map((option) => (
                <div key={option.id} className="flex items-center space-x-2">
                  <Checkbox
                    id={option.id}
                    checked={selectedFilters.brands.includes(option.id)}
                    onCheckedChange={(checked) => handleFilterChange("brands", option.id, checked as boolean)}
                  />
                  <label htmlFor={option.id} className="text-sm text-gray-700 cursor-pointer flex-1">
                    {toCamelCase(option.label)}
                  </label>
                  <span className="text-xs text-gray-500">({option.count})</span>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      <Separator className="my-4" />


      {/* Dress Code Filter */}
      <div className="mb-6">
        <button
          onClick={() => toggleSection("dressCode")}
          className="flex items-center justify-between w-full text-left font-medium text-gray-900 mb-3"
        >
          DRESS CODE
          {expandedSections.dressCode ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        {expandedSections.dressCode && (
          <div className="space-y-3">
            {dressCodeOptions.map((option) => (
              <div key={option.id} className="flex items-center space-x-2">
                <Checkbox
                  id={option.id}
                  checked={selectedFilters.dressCode.includes(option.id)}
                  onCheckedChange={(checked) => handleFilterChange("dressCode", option.id, checked as boolean)}
                />
                <label htmlFor={option.id} className="text-sm text-gray-700 cursor-pointer">
                  {option.label}
                </label>
              </div>
            ))}
          </div>
        )}
      </div>

      <Separator className="my-4" />

      {/* Color Filter */}
      <div className="mb-6">
        <button
          onClick={() => toggleSection("color")}
          className="flex items-center justify-between w-full text-left font-medium text-gray-900 mb-3"
        >
          COLOR
          {expandedSections.color ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        {expandedSections.color && (
          <div className="space-y-3">
            {colorOptions.map((option) => (
              <div key={option.id} className="flex items-center space-x-2">
                <Checkbox
                  id={option.id}
                  checked={selectedFilters.color.includes(option.id)}
                  onCheckedChange={(checked) => handleFilterChange("color", option.id, checked as boolean)}
                />
                <label htmlFor={option.id} className="text-sm text-gray-700 cursor-pointer">
                  {option.label}
                </label>
              </div>
            ))}
          </div>
        )}
      </div>

      <Separator className="my-4" />

      
      {/* Sleeve Type Filter */}
      <div className="mb-6">
        <button
          onClick={() => toggleSection("sleeves")}
          className="flex items-center justify-between w-full text-left font-medium text-gray-900 mb-3"
        >
          SLEEVE TYPE
          {expandedSections.sleeves ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        {expandedSections.sleeves && (
          <div className="space-y-3">
            {sleeveOptions.map((option) => (
              <div key={option.id} className="flex items-center space-x-2">
                <Checkbox
                  id={option.id}
                  checked={selectedFilters.sleeves.includes(option.id)}
                  onCheckedChange={(checked) => handleFilterChange("sleeves", option.id, checked as boolean)}
                />
                <label htmlFor={option.id} className="text-sm text-gray-700 cursor-pointer">
                  {option.label}
                </label>
              </div>
            ))}
          </div>
        )}
      </div>

      <Separator className="my-4" />

      {/* Fit Filter */}
      <div className="mb-6">
        <button
          onClick={() => toggleSection("fit")}
          className="flex items-center justify-between w-full text-left font-medium text-gray-900 mb-3"
        >
          FIT
          {expandedSections.fit ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        {expandedSections.fit && (
          <div className="space-y-3">
            {fitOptions.map((option) => (
              <div key={option.id} className="flex items-center space-x-2">
                <Checkbox
                  id={option.id}
                  checked={selectedFilters.fit.includes(option.id)}
                  onCheckedChange={(checked) => handleFilterChange("fit", option.id, checked as boolean)}
                />
                <label htmlFor={option.id} className="text-sm text-gray-700 cursor-pointer">
                  {option.label}
                </label>
              </div>
            ))}
          </div>
        )}
      </div>

      <Separator className="my-4" />

      {/* Neckline Filter */}
      <div className="mb-6">
        <button
          onClick={() => toggleSection("neckline")}
          className="flex items-center justify-between w-full text-left font-medium text-gray-900 mb-3"
        >
          NECKLINE
          {expandedSections.neckline ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        {expandedSections.neckline && (
          <div className="space-y-3">
            {necklineOptions.map((option) => (
              <div key={option.id} className="flex items-center space-x-2">
                <Checkbox
                  id={option.id}
                  checked={selectedFilters.neckline.includes(option.id)}
                  onCheckedChange={(checked) => handleFilterChange("neckline", option.id, checked as boolean)}
                />
                <label htmlFor={option.id} className="text-sm text-gray-700 cursor-pointer">
                  {option.label}
                </label>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
