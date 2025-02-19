import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // request to Flask backend API
    const response = await fetch('http://localhost:5000/api/zscore');
    const data = await response.json();

    // return data to front end
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
