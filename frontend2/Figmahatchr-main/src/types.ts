// TypeScript types matching backend API models
export interface GenerateRequest {
  prompt: string;
  verified: boolean;
}
export interface GenerateResponse {
  job_id: string;
  status: string;
  message: string;
}
export interface BuildStep {
  id: number;
  title: string;
  status: "pending" | "in_progress" | "completed";
}
export interface LogEntry {
  timestamp: string;
  message: string;
  type: "info" | "success" | "error";
}
export interface StatusResponse {
  job_id: string;
  status: "processing" | "completed" | "failed";
  progress: number;
  steps: BuildStep[];
  logs: LogEntry[];
  project_id?: string;
  project_name?: string;
  logo?: {
    success: boolean;
    logo_url?: string;
    error?: string;
    status: string;
  };
  pitch_deck?: {
    deck_url?: string;
    slides?: any[];
    total_slides?: number;
    status: string;
    error?: string;
  };
  live_url?: string;
}
export interface MarketingAssets {
  video: {
    video_url: string;
    thumbnail_url: string;
    duration: number;
    status: string;
  };
  pitch_deck: {
    deck_url: string;
    slides: number;
    status: string;
  };
}
export interface LaunchChannel {
  name: string;
  description: string;
  priority: "high" | "medium" | "low";
}
export interface ProjectResponse {
  project_id: string;
  project_name: string;
  description: string;
  live_url: string;
  api_docs_url: string;
  download_url: string;
  tech_stack: string[];
  created_at: string;
  marketing_assets?: {
    logo?: {
      success: boolean;
      logo_url?: string;
      error?: string;
      status: string;
    };
    pitch_deck?: {
      deck_url?: string;
      slides?: any[];
      total_slides?: number;
      status: string;
      error?: string;
    };
  };
  verified?: boolean;
}

export interface CofounderRequest {
  name: string;
  skills: string[];
  goals: string;
  personality: string;
  experienceLevel?: string;
}

export interface CofounderMatch {
  name: string;
  compatibility: number;
  sharedSkills: string[];
  summary: string;
  experienceLevel?: string;
}
