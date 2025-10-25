import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import OpenAI from 'openai';

const openaiKey = process.env.OPENAI_API_KEY;
const openai = openaiKey ? new OpenAI({ apiKey: openaiKey }) : null;
const profilesPath = path.resolve(process.cwd(), 'profiles.json');

function readProfiles() {
  try {
    const data = fs.readFileSync(profilesPath, 'utf-8');
    return JSON.parse(data || '[]');
  } catch {
    return [];
  }
}

export async function POST(request: NextRequest) {
  const { profile } = await request.json();
  const allProfiles = readProfiles();
  // Filter out self and by common domain
  const filtered = allProfiles.filter((p: any) => p.id !== profile.id && p.startupInterests.some((domain: string) => profile.startupInterests.includes(domain)));

  // Fallback heuristic if no OpenAI key or on failure
  async function fallback() {
    const score = (a: any, b: any) => {
      const skillSetA = new Set((a.skills || []).map((s: string) => s.toLowerCase()));
      const skillSetB = new Set((b.skills || []).map((s: string) => s.toLowerCase()));
      const sharedSkills = [...skillSetA].filter((s) => skillSetB.has(s));
      const interestsA = new Set((a.startupInterests || []).map((s: string) => s.toLowerCase()));
      const interestsB = new Set((b.startupInterests || []).map((s: string) => s.toLowerCase()));
      const sharedInterests = [...interestsA].filter((s) => interestsB.has(s));
      const base = 50 + Math.min(30, sharedInterests.length * 15) + Math.min(20, sharedSkills.length * 5);
      const matchScore = Math.min(97, base);
      const reason = sharedSkills.length
        ? `Shared strengths in ${sharedSkills.slice(0, 3).join(', ')} with overlapping interests in ${sharedInterests.slice(0, 2).join(', ')}`
        : `Strong interest overlap in ${sharedInterests.slice(0, 2).join(', ')} with complementary skills.`;
      return { matchScore, reason };
    };
    const ranked = filtered
      .map((p: any) => ({ ...p, ...score(profile, p) }))
      .sort((a: any, b: any) => (b.matchScore || 0) - (a.matchScore || 0))
      .slice(0, 5);
    return ranked;
  }

  if (!openai) {
    const ranked = await fallback();
    return NextResponse.json({ ok: true, matches: ranked });
  }

  try {
    const gptPrompt = `You are an expert startup cofounder matcher.\nMatch the following profile with complementary cofounders.\nProfile: ${JSON.stringify(profile)}\nFrom the database: ${JSON.stringify(filtered)}\nReturn a ranked list (max 5) of best fits in format:\n[{id, matchScore, reason}]`;

    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You are a cofounder matchmaking assistant.' },
        { role: 'user', content: gptPrompt }
      ],
      response_format: { type: 'json_object' }
    });

    let matches;
    try {
      matches = JSON.parse(completion.choices[0].message.content || '[]');
    } catch {
      matches = [];
    }

    const fullMatches = matches
      .map((match: any) => {
        const p = filtered.find((f: any) => f.id === match.id);
        return p ? { ...p, matchScore: match.matchScore, reason: match.reason } : null;
      })
      .filter(Boolean);

    return NextResponse.json({ ok: true, matches: fullMatches });
  } catch (e) {
    const ranked = await fallback();
    return NextResponse.json({ ok: true, matches: ranked });
  }
}
