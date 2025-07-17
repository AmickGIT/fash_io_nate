import Header from "@/components/header"

export default function RecommenderPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-12">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">AI Fashion Recommender</h1>
          <p className="text-xl text-gray-600 mb-8">
            Get personalized fashion recommendations based on your style preferences
          </p>
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
            <p className="text-gray-600">
              This feature is coming soon! Our AI will analyze your preferences and recommend the perfect outfits just
              for you.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
