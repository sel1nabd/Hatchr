/**
 * Concordium Wallet Integration Service
 * Handles connection to Concordium browser wallet and identity verification
 */

import {
  detectConcordiumProvider,
  WalletApi,
} from '@concordium/browser-wallet-api-helpers';

export interface IdentityStatement {
  type: 'AttributeInRange' | 'AttributeInSet';
  attributeTag: string;
  lower?: string;
  upper?: string;
  set?: string[];
}

export interface ConcordiumAccount {
  address: string;
  genesisHash: string;
}

export interface IdentityAttributes {
  name?: string;
  age?: number;
  country_of_residence?: string;
  date_of_birth?: string;
}

export interface VerifiablePresentation {
  type: string;
  verifiableCredential: Array<{
    credentialSubject: Record<string, any>;
    proof: Record<string, any>;
  }>;
  proof: Record<string, any>;
}

class ConcordiumWalletService {
  private provider: WalletApi | null = null;
  private connectedAccount: ConcordiumAccount | null = null;

  /**
   * Detect and initialize Concordium browser wallet
   */
  async detectWallet(): Promise<boolean> {
    try {
      this.provider = await detectConcordiumProvider();
      return !!this.provider;
    } catch (error) {
      console.error('Failed to detect Concordium wallet:', error);
      return false;
    }
  }

  /**
   * Connect to Concordium wallet and get account
   */
  async connect(): Promise<ConcordiumAccount> {
    if (!this.provider) {
      const detected = await this.detectWallet();
      if (!detected) {
        throw new Error(
          'Concordium wallet not found. Please install the Concordium Browser Wallet extension.'
        );
      }
    }

    try {
      // Request account access
      const accountAddress = await this.provider!.connect();

      if (!accountAddress) {
        throw new Error('No account selected in wallet');
      }

      // Get genesis hash for network verification
      const genesisHash = await this.provider!.getSelectedChain();

      this.connectedAccount = {
        address: accountAddress,
        genesisHash,
      };

      return this.connectedAccount;
    } catch (error: any) {
      console.error('Failed to connect to wallet:', error);
      throw new Error(error.message || 'Failed to connect to Concordium wallet');
    }
  }

  /**
   * Request verifiable presentation with identity proofs
   * This is used for signup/login to prove identity attributes
   */
  async requestIdentityProof(
    challenge: string,
    statement: IdentityStatement[]
  ): Promise<VerifiablePresentation> {
    if (!this.provider || !this.connectedAccount) {
      throw new Error('Wallet not connected');
    }

    try {
      // Request verifiable presentation from wallet
      const presentation = await this.provider.requestVerifiablePresentation(
        challenge,
        statement as any // Cast to avoid type conflicts
      );

      if (!presentation) {
        throw new Error('User cancelled identity proof request');
      }

      return presentation as VerifiablePresentation;
    } catch (error: any) {
      console.error('Failed to get identity proof:', error);
      throw new Error(error.message || 'Failed to get identity proof from wallet');
    }
  }

  /**
   * Disconnect from wallet
   */
  async disconnect(): Promise<void> {
    if (this.provider) {
      await this.provider.disconnect();
      this.connectedAccount = null;
    }
  }

  /**
   * Get currently connected account
   */
  getConnectedAccount(): ConcordiumAccount | null {
    return this.connectedAccount;
  }

  /**
   * Listen for account changes
   */
  onAccountChanged(callback: (account: string | undefined) => void): void {
    if (this.provider) {
      this.provider.on('accountChanged', callback);
    }
  }

  /**
   * Listen for disconnect events
   */
  onDisconnected(callback: () => void): void {
    if (this.provider) {
      this.provider.on('accountDisconnected', callback);
    }
  }

  /**
   * Remove event listeners
   */
  removeAllListeners(): void {
    if (this.provider) {
      this.provider.removeAllListeners();
    }
  }
}

// Export singleton instance
export const concordiumWallet = new ConcordiumWalletService();

/**
 * Create identity statement for Hatchr signup
 * Requires: age 18+, valid country of residence
 */
export function createHatchrIdentityStatement(): IdentityStatement[] {
  // Calculate date range for 18+ years old
  const currentYear = new Date().getFullYear();
  const eighteenYearsAgo = currentYear - 18;

  return [
    {
      type: 'AttributeInRange',
      attributeTag: 'dob', // Date of birth
      upper: `${eighteenYearsAgo}1231`, // Must be born before 18 years ago
    },
    {
      type: 'AttributeInSet',
      attributeTag: 'countryOfResidence',
      // List of valid countries (example - you can modify this)
      set: [
        'US', 'CA', 'GB', 'AU', 'NZ', 'SG', // English-speaking
        'AT', 'BE', 'BG', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', // EU countries
        'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT',
        'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'HR',
      ],
    },
  ];
}
