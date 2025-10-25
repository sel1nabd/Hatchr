import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const profilesPath = path.resolve(process.cwd(), 'profiles.json');

// Read profiles from local JSON
const readProfiles = () => {
  try {
    const data = fs.readFileSync(profilesPath, 'utf-8');
    return JSON.parse(data || '[]');
  } catch {
    return [];
  }
};

// Save profiles to local JSON
const saveProfiles = (profiles: any) => {
  fs.writeFileSync(profilesPath, JSON.stringify(profiles, null, 2));
};

export async function POST(request: NextRequest) {
  const body = await request.json();
  const profiles = readProfiles();
  body.id = Date.now();
  profiles.push(body);
  saveProfiles(profiles);
  return NextResponse.json({ ok: true, profile: body });
}

export async function GET() {
  const profiles = readProfiles();
  return NextResponse.json({ ok: true, profiles });
}
