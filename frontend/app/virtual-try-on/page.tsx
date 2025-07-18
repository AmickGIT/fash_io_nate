import Header from "@/components/header"

export default function VirtualTryOnPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-12">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Virtual Try-On</h1>
          <p className="text-xl text-gray-600 mb-8">Try on clothes virtually using AR technology</p>
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
            <p className="text-gray-600">
              Experience the future of online shopping! Use your camera to see how clothes look on you before making a
              purchase.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
