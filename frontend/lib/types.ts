/**
 * TypeScript types matching backend API models
 */

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
  tagline: string;
  stack: string[];
  verified: boolean;
  marketing_assets: MarketingAssets;
  launch_channels: LaunchChannel[];
}
