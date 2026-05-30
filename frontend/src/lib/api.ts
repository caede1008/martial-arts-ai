const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function analyzeImage(file: File) {
  const form = new FormData()
  form.append("image", file)
  const res = await fetch(`${API}/api/analyze`, { method: "POST", body: form })
  if (!res.ok) throw new Error(`${res.status}`)
  return res.json()
}