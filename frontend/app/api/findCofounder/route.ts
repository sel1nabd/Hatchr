import { NextResponse } from "next/server";
import path from "path";
import fs from "fs/promises";
import OpenAI from "openai";

const OPENAI_API_KEY = process.env.OPENAI_API_KEY || "xsk-proj-n65-Y-uguSoRKOJAn5nzSx4ae8Z5qyDGi6MESZ9mQRSWgmbZHV2h2tXkPOPignfiLAJz1nQIOHT3BlbkFJ-H92DdA0WFDhVNTY-4n-KEdnUZipAXRawMSrm6nn4LKGvQsSJCK00_0fSld_yip4XEu5Qb-cgA";
const openai = new OpenAI({ apiKey: OPENAI_API_KEY });

type FounderProfile = {
  name: string;
  skills: string[];
  goals: string;
  personality: string;
  experienceLevel?: string;
  embedding?: number[];
};

type MatchResult = {
  name: string;
  compatibility: number;
  reason: string;
};

const DATA_FILE_PATH = path.join(process.cwd(), "data", "mockFounders.json");

function embedContent(profile: FounderProfile) {
  return [
    ...(profile.skills ?? []),
    profile.goals ?? "",
    profile.personality ?? "",
    profile.experienceLevel ?? ""
  ].join(" ");
}

async function getEmbedding(text: string): Promise<number[] | null> {
  try {
    const res = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: text,
    });
    // openai.embeddings.create returns { data: [{ embedding: ... }] }
    return res.data[0].embedding as number[];
  } catch (e) {
    console.error("Embedding fetch failed", e);
    return null;
  }
}

function sharedSkillsScore(a: string[], b: string[]): { shared: string[]; score: number } {
  const al = new Set(a.map((s) => s.toLowerCase()));
  const shared = b.filter((s) => al.has(s.toLowerCase()));
  return { shared, score: shared.length };
}

function fallbackRank(user: FounderProfile, founders: FounderProfile[]): MatchResult[] {
  const ranked = founders.map((f) => {
    const { shared, score } = sharedSkillsScore(user.skills, f.skills || []);
    // Simple score: shared skills plus soft match on goals/personality
    let soft = 0;
    if ((user.goals || "").toLowerCase().includes((f.goals || "").split(" ")[0]?.toLowerCase() || "")) soft += 1;
    if ((user.personality || "").toLowerCase().includes((f.personality || "").split(" ")[0]?.toLowerCase() || "")) soft += 1;
    const compatibility = Math.min(96, 60 + (score * 10) + soft * 5);
    const reason = buildReason(user, f, compatibility / 100);
    return { name: f.name, compatibility, reason } as MatchResult;
  });
  return ranked.sort((a, b) => b.compatibility - a.compatibility).slice(0, 3);
}

function cosineSimilarity(a: number[], b: number[]): number {
  if (!a || !b || a.length !== b.length) return 0;
  let dot = 0, magA = 0, magB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    magA += a[i] * a[i];
    magB += b[i] * b[i];
  }
  return magA && magB ? dot / (Math.sqrt(magA) * Math.sqrt(magB)) : 0;
}

function buildReason(user: FounderProfile, match: FounderProfile, score: number) {
  const userSkillSet = new Set(user.skills.map((s) => s.toLowerCase()));
  const sharedSkills = match.skills.filter((skill) => userSkillSet.has(skill.toLowerCase()));
  if (sharedSkills.length > 0) return `Shared focus on ${sharedSkills.join(", ")} with aligned goals in ${match.goals}`;
  if (score > 0.6) return `Complementary strengths for ${match.goals} with compatible working style`;
  return `Fresh perspective for your goals with experience in ${match.skills.slice(0, 2).join(", ")}`;
}

async function loadFounders(): Promise<FounderProfile[]> {
  try {
    const data = await fs.readFile(DATA_FILE_PATH, "utf8");
    return JSON.parse(data) as FounderProfile[];
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") {
      await fs.mkdir(path.dirname(DATA_FILE_PATH), { recursive: true });
      await fs.writeFile(DATA_FILE_PATH, "[]", "utf8");
      return [];
    }
    console.error("Failed to read mockFounders.json", error);
    throw new Error("Unable to read founder data");
  }
}

async function saveFounders(profiles: FounderProfile[]) {
  await fs.writeFile(DATA_FILE_PATH, JSON.stringify(profiles, null, 2), "utf8");
}

function parseSkills(input: unknown): string[] {
  if (Array.isArray(input)) {
    return input.map((item) => typeof item === "string" ? item.trim() : String(item ?? "").trim()).filter(Boolean);
  }
  if (typeof input === "string") {
    return input.split(/[,|\n]/).map((skill) => skill.trim()).filter(Boolean);
  }
  return [];
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const userProfile: FounderProfile = {
      name: (body.name ?? "").trim(),
      skills: parseSkills(body.skills),
      goals: (body.goals ?? "").trim(),
      personality: (body.personality ?? "").trim(),
      experienceLevel: typeof body.experienceLevel === "string" ? body.experienceLevel.trim() : undefined,
    };
    if (!userProfile.name || userProfile.skills.length === 0 || !userProfile.goals || !userProfile.personality) {
      return NextResponse.json({ error: "Missing required fields in request" }, { status: 400 });
    }
    // fetch embedding for new user
    const userText = embedContent(userProfile);
    userProfile.embedding = await getEmbedding(userText);
    const founders = await loadFounders();
    // ensure all founders have embeddings (best-effort)
    for (const founder of founders) {
      if (!founder.embedding) {
        const text = embedContent(founder);
        founder.embedding = await getEmbedding(text);
      }
    }
    // save user in DB
    const updatedFounders = [...founders, userProfile];
    await saveFounders(updatedFounders);
    // If embeddings are available, use them; otherwise fallback to heuristic
    let matches: MatchResult[];
    const canEmbed = Boolean(userProfile.embedding) && founders.some((f) => Array.isArray(f.embedding));
    if (canEmbed) {
      matches = founders
        .filter((f) => f.embedding && userProfile.embedding)
        .map((founder) => {
          const similarity = cosineSimilarity(userProfile.embedding!, founder.embedding!);
          return {
            founder,
            compatibility: Math.round(similarity * 100),
            reason: buildReason(userProfile, founder, similarity),
          };
        })
        .sort((a, b) => b.compatibility - a.compatibility)
        .slice(0, 3)
        .map(({ founder, compatibility, reason }) => ({
          name: founder.name,
          compatibility,
          reason,
        }));
    } else {
      matches = fallbackRank(userProfile, founders);
    }
    return NextResponse.json({ matches });
  } catch (error) {
    console.error("Error processing co-founder request", error);
    return NextResponse.json({ error: "Failed to process co-founder search" }, { status: 500 });
  }
}
// To use: set your OpenAI key in a .env.local file as OPENAI_API_KEY=sk-xxx
