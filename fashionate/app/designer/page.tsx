import Header from "@/components/header"

export default function DesignerPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-12">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Fashion Designer Studio</h1>
          <p className="text-xl text-gray-600 mb-8">Create and customize your own fashion designs</p>
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
            <p className="text-gray-600">
              Unleash your creativity! Design custom clothing items and bring your fashion ideas to life.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
