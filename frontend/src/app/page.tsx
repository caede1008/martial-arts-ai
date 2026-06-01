"use client"
import { useState } from "react"
import { analyzeImage } from "@/lib/api"
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer
} from "recharts"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

type Result = {
  filename: string
  scores: {
    reach_ratio: number
    stance_ratio: number
    center_y: number
  }
  analysis: string
  message: string
}

export default function Home() {
  const [result, setResult] = useState<Result | null>(null)
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState<string>("")
  const [error, setError] = useState<string>("")

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setPreview(URL.createObjectURL(file))
    setLoading(true)
    setError("")
    setResult(null)
    try {
      const data = await analyzeImage(file)
      if (data.error) {
        setError(data.error)
      } else {
        setResult(data)
      }
    } catch (err) {
      setError("エラーが発生しました。もう一度試してください。")
    } finally {
      setLoading(false)
    }
  }

  const chartData = result ? [
    { subject: "リーチ", value: Math.round(result.scores.reach_ratio * 100) },
    { subject: "スタンス", value: Math.round(result.scores.stance_ratio * 100) },
    { subject: "重心", value: Math.round((1 - result.scores.center_y) * 100) },
  ] : []

  const analysisLines = result
    ? result.analysis.split("\n").filter(line => line.trim() !== "")
    : []

  return (
    <main className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-2">
          格闘技AI分析
        </h1>
        <p className="text-center text-gray-500 mb-8">
          全身が映った画像をアップロードしてください
        </p>
        <div className="bg-white rounded-2xl shadow p-6 mb-6">
          <label className="block w-full cursor-pointer border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-400 transition">
            <p className="text-gray-500 mb-2">クリックして画像を選択</p>
            <p className="text-gray-400 text-sm">JPG・PNG・JFIF対応</p>
            <input
              type="file"
              accept="image/*"
              onChange={handleFile}
              className="hidden"
            />
          </label>
        </div>
        {preview && (
          <div className="bg-white rounded-2xl shadow p-6 mb-6">
            <h2 className="font-semibold text-gray-700 mb-3">アップロード画像</h2>
            <img
              src={preview}
              alt="preview"
              className="w-full max-h-64 object-contain rounded-lg"
            />
          </div>
        )}
        {loading && (
          <div className="text-center py-10">
            <p className="text-blue-500 text-lg animate-pulse">AI分析中...</p>
            <p className="text-gray-400 text-sm mt-2">骨格解析とAI分析を実行しています</p>
          </div>
        )}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-4 mb-6">
            <p className="text-red-600">{error}</p>
          </div>
        )}
        {result && (
          <>
            <div className="bg-white rounded-2xl shadow p-6 mb-6">
              <h2 className="font-semibold text-gray-700 mb-4">骨格スコア</h2>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center bg-blue-50 rounded-xl p-4">
                  <p className="text-2xl font-bold text-blue-600">
                    {Math.round(result.scores.reach_ratio * 100)}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">リーチ</p>
                </div>
                <div className="text-center bg-green-50 rounded-xl p-4">
                  <p className="text-2xl font-bold text-green-600">
                    {Math.round(result.scores.stance_ratio * 100)}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">スタンス</p>
                </div>
                <div className="text-center bg-purple-50 rounded-xl p-4">
                  <p className="text-2xl font-bold text-purple-600">
                    {Math.round((1 - result.scores.center_y) * 100)}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">重心</p>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={240}>
                <RadarChart data={chartData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="subject" />
                  <Radar
                    dataKey="value"
                    stroke="#3B82F6"
                    fill="#3B82F6"
                    fillOpacity={0.3}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-white rounded-2xl shadow p-6">
              <h2 className="font-semibold text-gray-700 mb-4">AI分析レポート</h2>
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.analysis}</ReactMarkdown>
              </div>
            </div>
          </>
        )}
      </div>
    </main>
  )
}