/**
 * API Client for Hatchr Backend
 * Handles all API calls with logging and error handling
 */

import type {
  GenerateRequest,
  GenerateResponse,
  StatusResponse,
  ProjectResponse,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

/**
 * Logger utility for monitoring API calls
 */
class APILogger {
  private static log(level: "info" | "success" | "error", message: string, data?: any) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [API ${level.toUpperCase()}] ${message}`;

    if (level === "error") {
      console.error(logMessage, data || "");
    } else {
      console.log(logMessage, data || "");
    }
  }

  static info(message: string, data?: any) {
    this.log("info", message, data);
  }

  static success(message: string, data?: any) {
    this.log("success", message, data);
  }

  static error(message: string, error?: any) {
    this.log("error", message, error);
  }
}

/**
 * Generic fetch wrapper with error handling and logging
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  APILogger.info(`${options.method || "GET"} ${endpoint}`);

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      APILogger.error(`HTTP ${response.status} ${endpoint}`, errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    APILogger.success(`${options.method || "GET"} ${endpoint} completed`);

    return data as T;
  } catch (error) {
    APILogger.error(`Request failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * API Client
 */
export const api = {
  /**
   * Start generating a startup
   */
  async generateStartup(request: GenerateRequest): Promise<GenerateResponse> {
    APILogger.info("Starting startup generation", { prompt: request.prompt, verified: request.verified });

    return apiFetch<GenerateResponse>("/api/generate", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  /**
   * Poll job status
   */
  async getStatus(jobId: string): Promise<StatusResponse> {
    return apiFetch<StatusResponse>(`/api/status/${jobId}`);
  },

  /**
   * Get project details
   */
  async getProject(projectId: string): Promise<ProjectResponse> {
    APILogger.info(`Fetching project details: ${projectId}`);
    return apiFetch<ProjectResponse>(`/api/project/${projectId}`);
  },

  /**
   * Get Lovable build URL
   */
  async getLovableUrl(projectId: string): Promise<{ lovable_url: string; project_name: string }> {
    APILogger.info(`Fetching Lovable URL for project: ${projectId}`);
    return apiFetch(`/api/lovable-url/${projectId}`);
  },

  /**
   * Deploy project to Vercel
   */
  async deployProject(projectId: string): Promise<{ status: string; message: string; deployment_url: string }> {
    APILogger.info(`Deploying project: ${projectId}`);
    return apiFetch(`/api/deploy/${projectId}`, {
      method: "POST",
    });
  },
};

export { APILogger };
