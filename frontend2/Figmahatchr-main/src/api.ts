// This file provides API functions for the UI in Figmahatchr-main

import type {
  GenerateRequest,
  GenerateResponse,
  StatusResponse,
  ProjectResponse,
  CofounderRequest,
  CofounderMatch,
} from "./types";

const API_BASE_URL: string = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }
    return await response.json();
  } catch (error) {
    throw error;
  }
}

export const api = {
  async generateStartup(request: GenerateRequest): Promise<GenerateResponse> {
    return apiFetch<GenerateResponse>("/api/generate", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },
  async getStatus(jobId: string): Promise<StatusResponse> {
    return apiFetch<StatusResponse>(`/api/status/${jobId}`);
  },
  async getProject(projectId: string): Promise<ProjectResponse> {
    return apiFetch<ProjectResponse>(`/api/project/${projectId}`);
  },
  getDownloadUrl(projectId: string): string {
    return `${API_BASE_URL}/api/download/${projectId}`;
  },
  async deployProject(projectId: string): Promise<{ status: string; message: string; deployment_url: string }> {
    return apiFetch(`/api/deploy/${projectId}`, {
      method: "POST",
    });
  },
  async matchCofounders(profile: CofounderRequest): Promise<CofounderMatch[]> {
    const { experienceLevel, ...rest } = profile;
    const payload = {
      ...rest,
      ...(experienceLevel ? { experience_level: experienceLevel } : {}),
    };
    const result = await apiFetch<{
      matches: Array<{
        name: string;
        compatibility: number;
        summary: string;
        shared_skills?: string[];
        experience_level?: string;
      }>;
    }>("/api/cofounders/match", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return result.matches.map((match) => ({
      name: match.name,
      compatibility: match.compatibility,
      summary: match.summary,
      sharedSkills: match.shared_skills ?? [],
      experienceLevel: match.experience_level,
    }));
  },
};
