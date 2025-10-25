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
    console.log('[API] 🎯 Requesting challenge from backend...');
    console.log('[API] Backend URL:', API_BASE_URL);
    console.log('[API] Wallet address:', walletAddress);
    console.log('[API] Full endpoint:', `${API_BASE_URL}/api/auth/concordium/challenge`);

    const requestBody = {
      wallet_address: walletAddress,
    };
    console.log('[API] Request body:', JSON.stringify(requestBody, null, 2));

    try {
      console.log('[API] 📤 Sending POST request...');
      const response = await fetch(`${API_BASE_URL}/api/auth/concordium/challenge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('[API] 📥 Received response');
      console.log('[API] Response status:', response.status);
      console.log('[API] Response ok:', response.ok);
      console.log('[API] Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        console.error('[API] ❌ Response not OK');
        let errorDetail;
        try {
          errorDetail = await response.json();
          console.error('[API] Error response body:', JSON.stringify(errorDetail, null, 2));
        } catch (parseError) {
          console.error('[API] Could not parse error response as JSON');
          const errorText = await response.text();
          console.error('[API] Error response text:', errorText);
          errorDetail = { detail: errorText };
        }
        throw new Error(errorDetail.detail || 'Failed to request challenge');
      }

      const data = await response.json();
      console.log('[API] ✅ Challenge received successfully!');
      console.log('[API] Challenge data:', JSON.stringify(data, null, 2));

      return data;
    } catch (error: any) {
      console.error('[API] ❌ Request failed with exception');
      console.error('[API] Error type:', error.constructor.name);
      console.error('[API] Error message:', error.message);
      console.error('[API] Full error:', error);
      console.error('[API] Is TypeError:', error instanceof TypeError);
      console.error('[API] Is network error:', error.message?.includes('fetch') || error.message?.includes('Failed to fetch'));

      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.error('[API] 🚨 NETWORK ERROR - Backend is not reachable!');
        console.error('[API] Check:');
        console.error('[API]   1. Backend is running on port 8001');
        console.error('[API]   2. CORS is properly configured');
        console.error('[API]   3. Firewall is not blocking the connection');
        console.error('[API]   4. API_BASE_URL is correct:', API_BASE_URL);
      }

      throw error;
    }
  }

  /**
   * Step 2: Verify the presentation and complete signup/login
   */
  async verifyPresentation(
    walletAddress: string,
    challenge: string,
    presentation: any
  ): Promise<AuthResponse> {
    console.log('[API] 🔐 Verifying presentation with backend...');
    console.log('[API] Wallet address:', walletAddress);
    console.log('[API] Challenge:', challenge);
    console.log('[API] Presentation structure:', {
      type: presentation?.type,
      credentialCount: presentation?.verifiableCredential?.length,
      hasProof: !!presentation?.proof
    });

    const requestBody = {
      wallet_address: walletAddress,
      challenge,
      presentation,
    };
    console.log('[API] Full request body:', JSON.stringify(requestBody, null, 2));

    try {
      console.log('[API] 📤 Sending verification request...');
      const response = await fetch(`${API_BASE_URL}/api/auth/concordium/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('[API] 📥 Received verification response');
      console.log('[API] Response status:', response.status);
      console.log('[API] Response ok:', response.ok);

      if (!response.ok) {
        console.error('[API] ❌ Verification failed');
        let errorDetail;
        try {
          errorDetail = await response.json();
          console.error('[API] Error response:', JSON.stringify(errorDetail, null, 2));
        } catch (parseError) {
          const errorText = await response.text();
          console.error('[API] Error response text:', errorText);
          errorDetail = { detail: errorText };
        }
        throw new Error(errorDetail.detail || 'Failed to verify presentation');
      }

      const data = await response.json();
      console.log('[API] ✅ Verification successful!');
      console.log('[API] Response data:', {
        hasAuthToken: !!data.auth_token,
        authTokenLength: data.auth_token?.length,
        isNewUser: data.is_new_user,
        userId: data.user?.id,
        userWallet: data.user?.wallet_address
      });
      console.log('[API] Full response:', JSON.stringify(data, null, 2));

      // Store auth token
      console.log('[API] 💾 Storing auth token in localStorage...');
      this.authToken = data.auth_token;
      localStorage.setItem('hatchr_auth_token', data.auth_token);
      console.log('[API] ✅ Auth token stored successfully');

      return data;
    } catch (error: any) {
      console.error('[API] ❌ Verification request failed');
      console.error('[API] Error:', error);
      throw error;
    }
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
