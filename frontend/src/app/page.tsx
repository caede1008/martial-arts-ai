"use client"
import { useState } from "react"
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer
} from "recharts"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import styles from "./martial.module.css"

type Result = {
  filename: string
  scores: {
    reach_ratio: number
    stance_ratio: number
    center_y: number
  }
  cnn_result: {
    scores: {
      bjj: number
      boxing: number
      muaythai: number
      wrestling: number
    }
    top_class: string
    top_score: number
  }
  analysis: string
  message: string
}

const SPORT_CONFIG = [
  { key: "bjj",       label: "BJJ（柔術）", color: "#9b59b6", icon: "🥋" },
  { key: "boxing",    label: "ボクシング",   color: "#3498db", icon: "🥊" },
  { key: "muaythai",  label: "ムエタイ",     color: "#e74c3c", icon: "🦵" },
  { key: "wrestling", label: "レスリング",   color: "#2ecc71", icon: "🤼" },
]

export default function Home() {
  const [result, setResult] = useState<Result | null>(null)
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState<string>("")
  const [error, setError] = useState<string>("")
  const [file, setFile] = useState<File | null>(null)
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
    if (!file) { setError("画像を選択してください。"); return }
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
        method: "POST", body: formData,
      })
      const data = await res.json()
      if (data.error) setError(data.error)
      else setResult(data)
    } catch {
      setError("エラーが発生しました。もう一度試してください。")
    } finally {
      setLoading(false)
    }
  }

  const chartData = result ? [
    { subject: "リーチ",   value: Math.round(result.scores.reach_ratio * 100) },
    { subject: "スタンス", value: Math.round(result.scores.stance_ratio * 100) },
    { subject: "重心",     value: Math.round((1 - result.scores.center_y) * 100) },
  ] : []

  return (
    <div className={styles.wrap}>

      {/* ヘッダー */}
      <div className={styles.header}>
        <h1 className={styles.headerTitle}>
          格闘技<span className={styles.headerAccent}>AI</span>分析
        </h1>
        <p className={styles.headerSub}>画像と基礎データを入力して分析を開始してください</p>
      </div>

      <div className={styles.container}>

        {/* 画像アップロード */}
        <div className={styles.card}>
          <div className={styles.cardLabel}>
            <div className={styles.cardLabelBar} />
            <span className={styles.cardLabelText}>画像アップロード</span>
          </div>
          <div className={preview ? styles.uploadGridWithPreview : styles.uploadGrid}>
            <label className={styles.uploadArea}>
              <div className={styles.uploadIcon}>📷</div>
              <p className={styles.uploadText}>クリックして画像を選択</p>
              <p className={styles.uploadSub}>全身が映ったJPG・PNG・JFIF</p>
              <input type="file" accept="image/*" onChange={handleFileSelect} style={{ display: "none" }} />
            </label>
            {preview && (
              <img src={preview} alt="preview" className={styles.previewImage} />
            )}
          </div>
        </div>

        {/* 基礎データ */}
        <div className={styles.card}>
          <div className={styles.cardLabel}>
            <div className={styles.cardLabelBar} />
            <span className={styles.cardLabelText}>基礎データ</span>
          </div>
          <div className={styles.inputGrid3}>
            {[
              { label: "身長", unit: "cm", value: height, set: setHeight, placeholder: "178" },
              { label: "体重", unit: "kg", value: weight, set: setWeight, placeholder: "70"  },
              { label: "年齢", unit: "歳", value: age,    set: setAge,    placeholder: "25"  },
            ].map(({ label, unit, value, set, placeholder }) => (
              <div key={label} className={styles.dataCell}>
                <label className={styles.inputLabel}>{label}</label>
                <div className={styles.dataValue}>
                  <input
                    type="number"
                    value={value}
                    onChange={e => set(e.target.value)}
                    placeholder={placeholder}
                    className={styles.inputLarge}
                  />
                  <span className={styles.dataUnit}>{unit}</span>
                </div>
              </div>
            ))}
          </div>
          <div className={styles.inputGrid2}>
            <div className={styles.dataCell}>
              <label className={styles.inputLabel}>バックボーン</label>
              {background ? (
                <div className={styles.dataValueText} onClick={() => setBackground("")}>{background}</div>
              ) : (
                <input type="text" value={background} onChange={e => setBackground(e.target.value)} placeholder="例：柔道10年" className={styles.input} />
              )}
            </div>
            <div className={styles.dataCell}>
              <label className={styles.inputLabel}>得意技</label>
              {strongMove ? (
                <div className={styles.dataValueText} onClick={() => setStrongMove("")}>{strongMove}</div>
              ) : (
                <input type="text" value={strongMove} onChange={e => setStrongMove(e.target.value)} placeholder="例：内股" className={styles.input} />
              )}
            </div>
          </div>
        </div>
        {/* 分析ボタン */}
        <button
          onClick={handleSubmit}
          disabled={loading || !file}
          className={`${styles.submitBtn} ${loading || !file ? styles.submitBtnDisabled : styles.submitBtnActive}`}
        >
          {loading ? "AI分析中..." : "分析開始 →"}
        </button>

        {loading && <p className={styles.loadingText}>骨格解析とAI分析を実行しています...</p>}
        {error && <div className={styles.errorBox}>{error}</div>}

        {/* 結果 */}
        {result && (
          <>
            {/* 骨格スコア */}
            <div className={styles.card}>
              <div className={styles.cardLabel}>
                <div className={styles.cardLabelBar} />
                <span className={styles.cardLabelText}>骨格スコア</span>
              </div>
              <div className={styles.scoreGrid}>
                <div className={styles.scoreCards}>
                  {[
                    { label: "リーチ",   value: Math.round(result.scores.reach_ratio * 100),       color: "#3498db" },
                    { label: "スタンス", value: Math.round(result.scores.stance_ratio * 100),      color: "#2ecc71" },
                    { label: "重心",     value: Math.round((1 - result.scores.center_y) * 100),   color: "#9b59b6" },
                  ].map(({ label, value, color }) => (
                    <div key={label} className={styles.scoreCard}>
                      <div className={styles.scoreNum} style={{ color }}>{value}</div>
                      <div className={styles.scoreSub}>{label}</div>
                    </div>
                  ))}
                </div>
                <ResponsiveContainer width="100%" height={160}>
                  <RadarChart data={chartData}>
                    <PolarGrid stroke="#222" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: "#666", fontSize: 11 }} />
                    <Radar dataKey="value" stroke="#e53e3e" fill="#e53e3e" fillOpacity={0.25} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* CNN競技適性 */}
            <div className={styles.card}>
              <div className={styles.cardLabel}>
                <div className={styles.cardLabelBar} />
                <span className={styles.cardLabelText}>競技適性スコア（CNN判定）</span>
              </div>
              <p className={styles.cnnSub}>体型・視覚的特徴から判定した適性の近似値</p>
              {SPORT_CONFIG.map(({ key, label, color, icon }) => {
                const score = result.cnn_result.scores[key as keyof typeof result.cnn_result.scores]
                const isTop = result.cnn_result.top_class === key
                return (
                  <div key={key} className={styles.barRow}>
                    <div className={styles.barTop}>
                      <div className={styles.barLeft}>
                        <span className={styles.barIcon}>{icon}</span>
                        <span className={isTop ? styles.barLabelTop : styles.barLabel}>{label}</span>
                        {isTop && <span className={styles.barBadge}>最高適性</span>}
                      </div>
                      <span className={styles.barPct} style={{ color: isTop ? color : "#666" }}>
                        {Math.round(score * 100)}%
                      </span>
                    </div>
                    <div className={styles.barTrack}>
                      <div
                        className={styles.barFill}
                        style={{ width: `${Math.round(score * 100)}%`, background: color, opacity: isTop ? 1 : 0.4 }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>

            {/* AI分析レポート */}
            <div className={styles.card}>
              <div className={styles.cardLabel}>
                <div className={styles.cardLabelBar} />
                <span className={styles.cardLabelText}>AI分析レポート</span>
              </div>
              <div className={styles.reportContent}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {result.analysis}
                </ReactMarkdown>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}