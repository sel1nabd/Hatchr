import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

export function middleware(req: NextRequest) {
  const url = req.nextUrl;
  // Redirect everything to the Vite app running on 3001, preserving path and query
  const target = new URL(`http://localhost:3001${url.pathname}${url.search}`);
  return NextResponse.redirect(target);
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};

