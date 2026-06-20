import { NextRequest, NextResponse } from "next/server"

const BACKEND_URL = "http://localhost:8000"

export async function POST(request: NextRequest) {
  const path = request.nextUrl.searchParams.get("path") || "/api/analyze"
  const contentType = request.headers.get("content-type") || ""

  let body: BodyInit
  if (contentType.includes("multipart/form-data")) {
    body = await request.formData()
  } else {
    body = await request.text()
  }

  const res = await fetch(`${BACKEND_URL}${path}`, {
    method: "POST",
    headers: contentType.includes("multipart/form-data")
      ? {}
      : { "Content-Type": contentType },
    body,
  })

  const data = await res.json()
  return NextResponse.json(data)
}