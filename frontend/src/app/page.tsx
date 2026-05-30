"use client"
import { useState } from "react"
import { analyzeImage } from "@/lib/api"

export default function Home() {
  const [result, setResult] = useState<string>("")
  const [loading, setLoading] = useState(false)

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    try {
      const data = await analyzeImage(file)
      setResult(JSON.stringify(data, null, 2))
    } catch (err) {
      setResult(String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="p-8 max-w-lg mx-auto">
      <h1 className="text-2xl font-medium mb-6">格闘技AI分析</h1>
      <input type="file" accept="image/*" onChange={handleFile} className="mb-4" />
      {loading && <p className="text-gray-500">送信中...</p>}
      {result && <pre className="bg-gray-100 p-4 rounded text-sm">{result}</pre>}
    </main>
  )
}