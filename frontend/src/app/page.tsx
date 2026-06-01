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
  const [file, setFile] = useState<File | null>(null)

  // 基礎データ
  const [height, setHeight] = useState("")
  const [weight, setWeight] = useState("")
  const [age, setAge] = useState("")
  const [background, setBackground] = useState("")
  const [strongMove, setStrongMove] = useState("")

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
    setError("")
  }

  async function handleSubmit() {
    if (!file) {
      setError("画像を選択してください。")
      return
    }
    setLoading(true)
    setError("")
    setResult(null)

    try {
      const formData = new FormData()
      formData.append("image", file)
      formData.append("height", height || "0")
      formData.append("weight", weight || "0")
      formData.append("age", age || "0")
      formData.append("background", background)
      formData.append("strong_move", strongMove)

      const res = await fetch("http://localhost:8000/api/analyze", {
        method: "POST",
        body: formData,
      })
      const data = await res.json()
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

  return (
    <main className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-2xl mx-auto">

        {/* タイトル */}
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-2">
          格闘技AI分析
        </h1>
        <p className="text-center text-gray-500 mb-8">
          画像と基礎データを入力して分析を開始してください
        </p>

        {/* 画像アップロード */}
        <div className="bg-white rounded-2xl shadow p-6 mb-6">
          <h2 className="font-semibold text-gray-700 mb-3">画像アップロード</h2>
          <label className="block w-full cursor-pointer border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-400 transition">
            <p className="text-gray-500 mb-2">クリックして画像を選択</p>
            <p className="text-gray-400 text-sm">全身が映ったJPG・PNG・JFIF</p>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </label>
          {preview && (
            <img
              src={preview}
              alt="preview"
              className="w-full max-h-64 object-contain rounded-lg mt-4"
            />
          )}
        </div>

        {/* 基礎データ入力 */}
        <div className="bg-white rounded-2xl shadow p-6 mb-6">
          <h2 className="font-semibold text-gray-700 mb-4">基礎データ</h2>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <label className="text-sm text-gray-500 mb-1 block">身長 (cm)</label>
              <input
                type="number"
                value={height}
                onChange={e => setHeight(e.target.value)}
                placeholder="170"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400"
              />
            </div>
            <div>
              <label className="text-sm text-gray-500 mb-1 block">体重 (kg)</label>
              <input
                type="number"
                value={weight}
                onChange={e => setWeight(e.target.value)}
                placeholder="70"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400"
              />
            </div>
            <div>
              <label className="text-sm text-gray-500 mb-1 block">年齢</label>
              <input
                type="number"
                value={age}
                onChange={e => setAge(e.target.value)}
                placeholder="25"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400"
              />
            </div>
          </div>
          <div className="mb-4">
            <label className="text-sm text-gray-500 mb-1 block">バックボーン</label>
            <input
              type="text"
              value={background}
              onChange={e => setBackground(e.target.value)}
              placeholder="例：柔道10年、空手5年"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400"
            />
          </div>
          <div>
            <label className="text-sm text-gray-500 mb-1 block">得意技</label>
            <input
              type="text"
              value={strongMove}
              onChange={e => setStrongMove(e.target.value)}
              placeholder="例：内股、右ストレート"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400"
            />
          </div>
        </div>

        {/* 分析ボタン */}
        <button
          onClick={handleSubmit}
          disabled={loading || !file}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-semibold py-3 rounded-2xl transition mb-6"
        >
          {loading ? "AI分析中..." : "分析開始"}
        </button>

        {/* ローディング */}
        {loading && (
          <div className="text-center py-6">
            <p className="text-blue-500 animate-pulse">骨格解析とAI分析を実行しています...</p>
          </div>
        )}

        {/* エラー */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-4 mb-6">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* 結果 */}
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
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {result.analysis}
                </ReactMarkdown>
              </div>
            </div>
          </>
        )}
      </div>
    </main>
  )
}