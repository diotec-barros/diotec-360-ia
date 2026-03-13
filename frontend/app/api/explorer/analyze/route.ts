import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { code, language } = await request.json();

    if (!code || !language) {
      return NextResponse.json(
        { error: 'Código e linguagem são obrigatórios' },
        { status: 400 }
      );
    }

    // Call backend Judge API
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    const response = await fetch(`${backendUrl}/api/v3/explorer/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, language }),
    });

    if (!response.ok) {
      throw new Error('Erro ao analisar código');
    }

    const result = await response.json();
    return NextResponse.json(result);
    
  } catch (error) {
    console.error('Explorer API error:', error);
    return NextResponse.json(
      { error: 'Erro ao processar análise' },
      { status: 500 }
    );
  }
}
