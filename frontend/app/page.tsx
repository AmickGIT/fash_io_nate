"use client"

import { useState } from 'react';
import Header from "@/components/header";
import ProductGrid from "@/components/product-grid";
import Sidebar from "@/components/sidebar";

interface Filters {
  gender: string[];
  categories: string[];
  brands: string[];
  dressCode: string[];
  color: string[];
  sleeves: string[];
  fit: string[];
  neckline: string[];
}

export default function Home() {
  const [selectedFilters, setSelectedFilters] = useState<Filters>({
    gender: [],
    categories: [],
    brands: [],
    dressCode: [],
    color: [],
    sleeves: [],
    fit: [],
    neckline: [],
  });

  const [wardrobeCount, setWardrobeCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    setSubmittedQuery(value);
  };

  const handleClearSearch = () => {
    setSearchQuery("");
    setSubmittedQuery("");
  };

  const handleWardrobeUpdate = (newCount?: number) => {
    if (typeof newCount === 'number') {
      setWardrobeCount(newCount);
    }
  };

  return (
    <div className="bg-gray-50 min-h-screen">
      <Header
        wardrobeCount={wardrobeCount}
        onWardrobeUpdate={handleWardrobeUpdate}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onSearch={handleSearch}
        onClearSearch={handleClearSearch}
      />
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <Sidebar selectedFilters={selectedFilters} onFilterChange={setSelectedFilters} onClearSearch={handleClearSearch} />
          </div>
          <div className="lg:col-span-3">
            <ProductGrid
              selectedFilters={selectedFilters}
              onWardrobeUpdate={handleWardrobeUpdate}
              searchQuery={submittedQuery}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
