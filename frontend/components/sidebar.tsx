"use client"

import { useState, useEffect, Dispatch, SetStateAction } from "react"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ChevronDown, ChevronUp } from "lucide-react"
import { API_BASE } from "@/lib/constants"

interface SidebarProps {
  selectedFilters: {
    gender: string[];
    categories: string[];
    brands: string[];
    dressCode: string[];
    color: string[];
    sleeves: string[];
    fit: string[];
    neckline: string[];
  };
  onFilterChange: Dispatch<SetStateAction<{
    gender: string[];
    categories: string[];
    brands: string[];
    dressCode: string[];
    color: string[];
    sleeves: string[];
    fit: string[];
    neckline: string[];
  }>>;
  onClearSearch?: () => void;
}


export default function Sidebar({
  selectedFilters,
  onFilterChange,
  onClearSearch,
}: SidebarProps) {
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

  const [brandOptions, setBrandOptions] = useState<Array<{ id: string; label: string; count: number }>>([])
  const [brandsLoading, setBrandsLoading] = useState(true)
  const [brandsError, setBrandsError] = useState<string | null>(null)

  useEffect(() => {
    setBrandsLoading(true)
    fetch(`${API_BASE}/api/brands`)
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

  // Dress Code
  const [dressCodeOptions, setDressCodeOptions] = useState<{ label: string; count: number }[]>([])
  const [dressCodeLoading, setDressCodeLoading] = useState(true)
  const [dressCodeError, setDressCodeError] = useState<string | null>(null)
  useEffect(() => {
    setDressCodeLoading(true)
    fetch(`${API_BASE}/api/dress-codes`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch dress codes")
        return res.json()
      })
      .then((data) => {
        setDressCodeOptions(data)
        setDressCodeLoading(false)
      })
      .catch((err) => {
        setDressCodeError(err.message)
        setDressCodeLoading(false)
      })
  }, [])

  // Color
  const [colorOptions, setColorOptions] = useState<{ label: string; count: number }[]>([])
  const [colorLoading, setColorLoading] = useState(true)
  const [colorError, setColorError] = useState<string | null>(null)
  useEffect(() => {
    setColorLoading(true)
    fetch(`${API_BASE}/api/colors`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch colors")
        return res.json()
      })
      .then((data) => {
        setColorOptions(data)
        setColorLoading(false)
      })
      .catch((err) => {
        setColorError(err.message)
        setColorLoading(false)
      })
  }, [])

  // Sleeve
  const [sleeveOptions, setSleeveOptions] = useState<{ label: string; count: number }[]>([])
  const [sleeveLoading, setSleeveLoading] = useState(true)
  const [sleeveError, setSleeveError] = useState<string | null>(null)
  useEffect(() => {
    setSleeveLoading(true)
    fetch(`${API_BASE}/api/sleeves`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch sleeves")
        return res.json()
      })
      .then((data) => {
        setSleeveOptions(data)
        setSleeveLoading(false)
      })
      .catch((err) => {
        setSleeveError(err.message)
        setSleeveLoading(false)
      })
  }, [])

  // Fit
  const [fitOptions, setFitOptions] = useState<{ label: string; count: number }[]>([])
  const [fitLoading, setFitLoading] = useState(true)
  const [fitError, setFitError] = useState<string | null>(null)
  useEffect(() => {
    setFitLoading(true)
    fetch(`${API_BASE}/api/fits`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch fits")
        return res.json()
      })
      .then((data) => {
        setFitOptions(data)
        setFitLoading(false)
      })
      .catch((err) => {
        setFitError(err.message)
        setFitLoading(false)
      })
  }, [])

  // Neckline
  const [necklineOptions, setNecklineOptions] = useState<{ label: string; count: number }[]>([])
  const [necklineLoading, setNecklineLoading] = useState(true)
  const [necklineError, setNecklineError] = useState<string | null>(null)
  useEffect(() => {
    setNecklineLoading(true)
    fetch(`${API_BASE}/api/necklines`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch necklines")
        return res.json()
      })
      .then((data) => {
        setNecklineOptions(data)
        setNecklineLoading(false)
      })
      .catch((err) => {
        setNecklineError(err.message)
        setNecklineLoading(false)
      })
  }, [])

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  const handleFilterChange = (section: keyof typeof selectedFilters, value: string, checked: boolean) => {
    onFilterChange((prev) => ({
      ...prev,
      [section]: checked ? [...prev[section], value] : prev[section].filter((item) => item !== value),
    }))
  }

  const clearAllFilters = () => {
    onFilterChange({
      gender: ["women"],
      categories: [],
      brands: [],
      dressCode: [],
      color: [],
      sleeves: [],
      fit: [],
      neckline: [],
    });
    if (onClearSearch) onClearSearch();
  };

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
          <div
            className={
              "space-y-3" +
              (brandOptions.length > 10 ? " max-h-72 overflow-y-auto pr-1 custom-scrollbar" : "")
            }
          >
            {brandsLoading ? (
              <div className="text-sm text-gray-500">Loading brands...</div>
            ) : brandsError ? (
              <div className="text-sm text-red-500">{brandsError}</div>
            ) : brandOptions.length === 0 ? (
              <div className="text-sm text-gray-500">No brands found.</div>
            ) : (
              brandOptions.map((option, idx) => (
                <div key={option.label + '-' + option.count + '-' + idx} className="flex items-center space-x-2">
                  <Checkbox
                    id={option.label}
                    checked={selectedFilters?.brands.includes(option.label)}
                    onCheckedChange={(checked) => handleFilterChange("brands", option.label, checked as boolean)}
                  />
                  <label htmlFor={option.label} className="text-sm text-gray-700 cursor-pointer flex-1">
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
          <div
            className={
              "space-y-3" +
              (dressCodeOptions.length > 5 ? " max-h-36 overflow-y-auto pr-1 custom-scrollbar" : "")
            }
          >
            {dressCodeLoading ? (
              <div className="text-sm text-gray-500">Loading dress codes...</div>
            ) : dressCodeError ? (
              <div className="text-sm text-red-500">{dressCodeError}</div>
            ) : dressCodeOptions.length === 0 ? (
              <div className="text-sm text-gray-500">No dress codes found.</div>
            ) : (
              dressCodeOptions.map((option, idx) => (
                <div key={option.label + '-' + option.count + '-' + idx} className="flex items-center space-x-2">
                  <Checkbox
                    id={option.label}
                    checked={selectedFilters?.dressCode.includes(option.label)}
                    onCheckedChange={(checked) => handleFilterChange("dressCode", option.label, checked as boolean)}
                  />
                  <label htmlFor={option.label} className="text-sm text-gray-700 cursor-pointer">
                    {toCamelCase(option.label)}
                  </label>
                </div>
              ))
            )}
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
          <div
            className={
              "space-y-3" +
              (colorOptions.length > 5 ? " max-h-36 overflow-y-auto pr-1 custom-scrollbar" : "")
            }
          >
            {colorLoading ? (
              <div className="text-sm text-gray-500">Loading colors...</div>
            ) : colorError ? (
              <div className="text-sm text-red-500">{colorError}</div>
            ) : colorOptions.length === 0 ? (
              <div className="text-sm text-gray-500">No colors found.</div>
            ) : (
              colorOptions.map((option, idx) => (
                <div key={option.label + '-' + option.count + '-' + idx} className="flex items-center space-x-2">
                  <Checkbox
                    id={option.label}
                    checked={selectedFilters?.color.includes(option.label)}
                    onCheckedChange={(checked) => handleFilterChange("color", option.label, checked as boolean)}
                  />
                  <label htmlFor={option.label} className="text-sm text-gray-700 cursor-pointer">
                    {toCamelCase(option.label)}
                  </label>
                </div>
              ))
            )}
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
          <div
            className={
              "space-y-3" +
              (sleeveOptions.length > 5 ? " max-h-36 overflow-y-auto pr-1 custom-scrollbar" : "")
            }
          >
            {sleeveLoading ? (
              <div className="text-sm text-gray-500">Loading sleeves...</div>
            ) : sleeveError ? (
              <div className="text-sm text-red-500">{sleeveError}</div>
            ) : sleeveOptions.length === 0 ? (
              <div className="text-sm text-gray-500">No sleeves found.</div>
            ) : (
              sleeveOptions.map((option, idx) => (
                <div key={option.label + '-' + option.count + '-' + idx} className="flex items-center space-x-2">
                  <Checkbox
                    id={option.label}
                    checked={selectedFilters?.sleeves.includes(option.label)}
                    onCheckedChange={(checked) => handleFilterChange("sleeves", option.label, checked as boolean)}
                  />
                  <label htmlFor={option.label} className="text-sm text-gray-700 cursor-pointer">
                    {toCamelCase(option.label)}
                  </label>
                </div>
              ))
            )}
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
          <div
            className={
              "space-y-3" +
              (fitOptions.length > 5 ? " max-h-36 overflow-y-auto pr-1 custom-scrollbar" : "")
            }
          >
            {fitLoading ? (
              <div className="text-sm text-gray-500">Loading fits...</div>
            ) : fitError ? (
              <div className="text-sm text-red-500">{fitError}</div>
            ) : fitOptions.length === 0 ? (
              <div className="text-sm text-gray-500">No fits found.</div>
            ) : (
              fitOptions.map((option, idx) => (
                <div key={option.label + '-' + option.count + '-' + idx} className="flex items-center space-x-2">
                  <Checkbox
                    id={option.label}
                    checked={selectedFilters?.fit.includes(option.label)}
                    onCheckedChange={(checked) => handleFilterChange("fit", option.label, checked as boolean)}
                  />
                  <label htmlFor={option.label} className="text-sm text-gray-700 cursor-pointer">
                    {toCamelCase(option.label)}
                  </label>
                </div>
              ))
            )}
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
          <div
            className={
              "space-y-3" +
              (necklineOptions.length > 5 ? " max-h-36 overflow-y-auto pr-1 custom-scrollbar" : "")
            }
          >
            {necklineLoading ? (
              <div className="text-sm text-gray-500">Loading necklines...</div>
            ) : necklineError ? (
              <div className="text-sm text-red-500">{necklineError}</div>
            ) : necklineOptions.length === 0 ? (
              <div className="text-sm text-gray-500">No necklines found.</div>
            ) : (
              necklineOptions.map((option, idx) => (
                <div key={option.label + '-' + option.count + '-' + idx} className="flex items-center space-x-2">
                  <Checkbox
                    id={option.label}
                    checked={selectedFilters?.neckline.includes(option.label)}
                    onCheckedChange={(checked) => handleFilterChange("neckline", option.label, checked as boolean)}
                  />
                  <label htmlFor={option.label} className="text-sm text-gray-700 cursor-pointer">
                    {toCamelCase(option.label)}
                  </label>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
}
