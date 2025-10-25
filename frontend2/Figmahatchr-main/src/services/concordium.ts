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
    console.log('[Concordium] 🔍 Detecting Concordium browser wallet...');
    try {
      this.provider = await detectConcordiumProvider();
      if (this.provider) {
        console.log('[Concordium] ✅ Wallet provider detected successfully');
        console.log('[Concordium] Provider details:', this.provider);
      } else {
        console.warn('[Concordium] ⚠️ Wallet provider detected but is null/undefined');
      }
      return !!this.provider;
    } catch (error) {
      console.error('[Concordium] ❌ Failed to detect Concordium wallet:', error);
      console.error('[Concordium] Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      });
      return false;
    }
  }

  /**
   * Connect to Concordium wallet and get account
   */
  async connect(): Promise<ConcordiumAccount> {
    console.log('[Concordium] 🔌 Starting wallet connection flow...');

    if (!this.provider) {
      console.log('[Concordium] No provider found, attempting to detect...');
      const detected = await this.detectWallet();
      if (!detected) {
        console.error('[Concordium] ❌ Wallet detection failed');
        throw new Error(
          'Concordium wallet not found. Please install the Concordium Browser Wallet extension.'
        );
      }
      console.log('[Concordium] ✅ Wallet detected after manual detection');
    }

    try {
      console.log('[Concordium] 📞 Requesting account access from wallet extension...');
      // Request account access
      const accountAddress = await this.provider!.connect();
      console.log('[Concordium] 📬 Received account address:', accountAddress);

      if (!accountAddress) {
        console.error('[Concordium] ❌ No account address returned');
        throw new Error('No account selected in wallet');
      }

      console.log('[Concordium] 🌐 Getting selected chain/network...');
      // Get genesis hash for network verification
      const genesisHash = await this.provider!.getSelectedChain();
      console.log('[Concordium] Genesis hash received:', genesisHash);

      this.connectedAccount = {
        address: accountAddress,
        genesisHash,
      };

      console.log('[Concordium] ✅ Wallet connected successfully!', {
        address: accountAddress,
        genesisHash: genesisHash
      });

      return this.connectedAccount;
    } catch (error: any) {
      console.error('[Concordium] ❌ Failed to connect to wallet');
      console.error('[Concordium] Error type:', error.constructor.name);
      console.error('[Concordium] Error message:', error.message);
      console.error('[Concordium] Full error:', error);
      console.error('[Concordium] Error stack:', error.stack);
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
    console.log('[Concordium] 🎫 Starting identity proof request...');
    console.log('[Concordium] Challenge:', challenge);
    console.log('[Concordium] Statement requirements:', JSON.stringify(statement, null, 2));

    if (!this.provider || !this.connectedAccount) {
      console.error('[Concordium] ❌ Cannot request proof - wallet not connected');
      console.error('[Concordium] Provider exists:', !!this.provider);
      console.error('[Concordium] Account exists:', !!this.connectedAccount);
      throw new Error('Wallet not connected');
    }

    console.log('[Concordium] ✅ Wallet is connected, proceeding with proof request');
    console.log('[Concordium] Connected account:', this.connectedAccount.address);

    try {
      console.log('[Concordium] 📤 Sending verifiable presentation request to wallet...');
      // Request verifiable presentation from wallet
      const presentation = await this.provider.requestVerifiablePresentation(
        challenge,
        statement as any // Cast to avoid type conflicts
      );

      console.log('[Concordium] 📥 Received presentation response from wallet');
      console.log('[Concordium] Presentation exists:', !!presentation);

      if (!presentation) {
        console.warn('[Concordium] ⚠️ Presentation is null/undefined - user likely cancelled');
        throw new Error('User cancelled identity proof request');
      }

      console.log('[Concordium] ✅ Presentation received successfully!');
      console.log('[Concordium] Presentation structure:', {
        type: presentation.type,
        credentialCount: presentation.verifiableCredential?.length,
        hasProof: !!presentation.proof
      });
      console.log('[Concordium] Full presentation:', JSON.stringify(presentation, null, 2));

      return presentation as VerifiablePresentation;
    } catch (error: any) {
      console.error('[Concordium] ❌ Failed to get identity proof');
      console.error('[Concordium] Error type:', error.constructor.name);
      console.error('[Concordium] Error message:', error.message);
      console.error('[Concordium] Error code:', error.code);
      console.error('[Concordium] Full error:', error);
      console.error('[Concordium] Error stack:', error.stack);
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
