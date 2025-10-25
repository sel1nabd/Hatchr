/**
 * Signup Page with Concordium Wallet Authentication
 * Users connect their Concordium wallet to sign up or log in
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, Wallet, CheckCircle2, AlertCircle, Shield } from 'lucide-react';
import {
  concordiumWallet,
  createHatchrIdentityStatement,
  type ConcordiumAccount,
} from '../services/concordium';
import { apiService } from '../services/api';

type AuthStep = 'idle' | 'connecting' | 'requesting_proof' | 'verifying' | 'success' | 'error';

export function SignupPage() {
  const navigate = useNavigate();
  const [authStep, setAuthStep] = useState<AuthStep>('idle');
  const [error, setError] = useState<string | null>(null);
  const [account, setAccount] = useState<ConcordiumAccount | null>(null);
  const [isNewUser, setIsNewUser] = useState<boolean>(false);

  useEffect(() => {
    // Check if already authenticated
    const checkAuth = async () => {
      const user = await apiService.getCurrentUser();
      if (user) {
        // Already logged in, redirect to main page
        navigate('/');
      }
    };

    checkAuth();

    // Setup wallet event listeners
    concordiumWallet.onAccountChanged((newAccount) => {
      if (newAccount) {
        setAccount({ address: newAccount, genesisHash: '' });
      } else {
        setAccount(null);
      }
    });

    concordiumWallet.onDisconnected(() => {
      setAccount(null);
      setAuthStep('idle');
    });

    return () => {
      concordiumWallet.removeAllListeners();
    };
  }, [navigate]);

  const handleConnectWallet = async () => {
    setError(null);
    setAuthStep('connecting');

    try {
      // Step 1: Connect to wallet
      const connectedAccount = await concordiumWallet.connect();
      setAccount(connectedAccount);

      // Step 2: Request challenge from backend
      setAuthStep('requesting_proof');
      const { challenge } = await apiService.requestChallenge(connectedAccount.address);

      // Step 3: Request identity proof from wallet
      const identityStatement = createHatchrIdentityStatement();
      const presentation = await concordiumWallet.requestIdentityProof(
        challenge,
        identityStatement
      );

      // Step 4: Verify presentation with backend
      setAuthStep('verifying');
      const authResponse = await apiService.verifyPresentation(
        connectedAccount.address,
        challenge,
        presentation
      );

      // Success!
      setIsNewUser(authResponse.is_new_user);
      setAuthStep('success');

      // Redirect to main page after 2 seconds
      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (err: any) {
      console.error('Authentication error:', err);
      setError(err.message || 'Failed to authenticate with Concordium wallet');
      setAuthStep('error');
    }
  };

  const getStepMessage = () => {
    switch (authStep) {
      case 'connecting':
        return 'Connecting to Concordium wallet...';
      case 'requesting_proof':
        return 'Requesting identity verification...';
      case 'verifying':
        return 'Verifying your identity...';
      case 'success':
        return isNewUser ? 'Account created successfully!' : 'Welcome back!';
      default:
        return null;
    }
  };

  const isLoading = ['connecting', 'requesting_proof', 'verifying'].includes(authStep);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold">Welcome to Hatchr</CardTitle>
          <CardDescription>
            Connect your Concordium wallet to sign up or log in securely
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Info about identity verification */}
          <Alert>
            <Shield className="h-4 w-4" />
            <AlertDescription className="text-sm">
              Your identity is verified using zero-knowledge proofs. We only verify that you're 18+
              without exposing your personal data.
            </AlertDescription>
          </Alert>

          {/* Status message */}
          {authStep !== 'idle' && authStep !== 'error' && (
            <Alert className="bg-blue-50 border-blue-200">
              <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
              <AlertDescription className="text-blue-800">{getStepMessage()}</AlertDescription>
            </Alert>
          )}

          {/* Success message */}
          {authStep === 'success' && (
            <Alert className="bg-green-50 border-green-200">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">{getStepMessage()}</AlertDescription>
            </Alert>
          )}

          {/* Error message */}
          {authStep === 'error' && error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Connected account */}
          {account && authStep !== 'success' && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Connected Account</p>
              <p className="text-sm font-mono break-all">{account.address}</p>
            </div>
          )}

          {/* Connect button */}
          <Button
            onClick={handleConnectWallet}
            disabled={isLoading || authStep === 'success'}
            className="w-full"
            size="lg"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {getStepMessage()}
              </>
            ) : authStep === 'success' ? (
              <>
                <CheckCircle2 className="mr-2 h-4 w-4" />
                Redirecting...
              </>
            ) : (
              <>
                <Wallet className="mr-2 h-4 w-4" />
                Connect Concordium Wallet
              </>
            )}
          </Button>

          {/* Help text */}
          <div className="text-center text-sm text-gray-500 space-y-2">
            <p>
              Don't have a Concordium wallet?{' '}
              <a
                href="https://chrome.google.com/webstore/detail/concordium-wallet/mnnkpffndmickbiakofclnpoiajlegmg"
                target="_blank"
                rel="noopener noreferrer"
                className="text-purple-600 hover:underline"
              >
                Install the extension
              </a>
            </p>
          </div>

          {/* Requirements */}
          <div className="border-t pt-4">
            <p className="text-xs text-gray-500 mb-2 font-semibold">Requirements:</p>
            <ul className="text-xs text-gray-500 space-y-1">
              <li>✓ Must be 18 years or older</li>
              <li>✓ Concordium identity verification</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
