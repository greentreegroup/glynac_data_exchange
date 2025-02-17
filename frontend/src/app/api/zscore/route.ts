import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // 发送请求到 Flask 后端 API
    const response = await fetch('http://localhost:5000/api/zscore');
    const data = await response.json();

    // 返回数据给前端
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
