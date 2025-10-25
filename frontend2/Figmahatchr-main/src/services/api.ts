/**
 * API Service for Hatchr Backend
 * Handles all HTTP requests to the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

interface ChallengeResponse {
  challenge: string;
  wallet_address: string;
}

interface AuthResponse {
  auth_token: string;
  user: {
    id: number;
    wallet_address: string;
    name?: string;
    age?: number;
    country_of_residence?: string;
    created_at: string;
    last_login: string;
  };
  is_new_user: boolean;
}

interface User {
  id: number;
  wallet_address: string;
  name?: string;
  age?: number;
  country_of_residence?: string;
  created_at: string;
  last_login: string;
}

class APIService {
  private authToken: string | null = null;

  constructor() {
    // Load auth token from localStorage on init
    this.authToken = localStorage.getItem('hatchr_auth_token');
  }

  /**
   * Step 1: Request a challenge for wallet signature
   */
  async requestChallenge(walletAddress: string): Promise<ChallengeResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/concordium/challenge`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        wallet_address: walletAddress,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to request challenge');
    }

    return response.json();
  }

  /**
   * Step 2: Verify the presentation and complete signup/login
   */
  async verifyPresentation(
    walletAddress: string,
    challenge: string,
    presentation: any
  ): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/concordium/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        wallet_address: walletAddress,
        challenge,
        presentation,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to verify presentation');
    }

    const data = await response.json();

    // Store auth token
    this.authToken = data.auth_token;
    localStorage.setItem('hatchr_auth_token', data.auth_token);

    return data;
  }

  /**
   * Get current authenticated user
   */
  async getCurrentUser(): Promise<User | null> {
    if (!this.authToken) {
      return null;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/auth/me?auth_token=${this.authToken}`
      );

      if (!response.ok) {
        // Token expired or invalid
        this.logout();
        return null;
      }

      return response.json();
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    if (this.authToken) {
      try {
        await fetch(`${API_BASE_URL}/api/auth/logout?auth_token=${this.authToken}`, {
          method: 'POST',
        });
      } catch (error) {
        console.error('Logout request failed:', error);
      }
    }

    this.authToken = null;
    localStorage.removeItem('hatchr_auth_token');
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.authToken;
  }

  /**
   * Get auth token
   */
  getAuthToken(): string | null {
    return this.authToken;
  }
}

export const apiService = new APIService();
