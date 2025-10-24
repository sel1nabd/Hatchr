"use client";

import { useState, useEffect } from "react";
import {
  detectConcordiumProvider,
} from "@concordium/browser-wallet-api-helpers";
import {
  ConcordiumGRPCWebClient,
  createIdentityRequestWithKeys,
} from "@concordium/web-sdk";

export default function ConcordiumVerify() {
  const [provider, setProvider] = useState<any>(null);
  const [account, setAccount] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("idle");
  const [identityProviders, setIdentityProviders] = useState<any[]>([]);

  useEffect(() => {
    // Load identity providers from Concordium mainnet
    fetch("https://wallet-proxy.mainnet.concordium.software/wallet-proxy/identityProviders")
      .then((res) => res.json())
      .then(setIdentityProviders)
      .catch(console.error);
  }, []);

  async function connectWallet() {
    try {
      const detected = await detectConcordiumProvider();
      await detected.connect();
      const account = await detected.getMostRecentlySelectedAccount();
      setProvider(detected);
      setAccount(account);
      console.log("Connected to Concordium wallet:", account);
    } catch (e) {
      alert("Please install and unlock the Concordium Browser Wallet.");
    }
  }

  async function startVerification() {
    if (!identityProviders.length) {
      alert("No identity providers available.");
      return;
    }
    const selected = identityProviders[0];
    setStatus("creating");

    try {
      const grpc = new ConcordiumGRPCWebClient(
        "grpc.mainnet.concordium.software",
        20000
      );
      const cryptoParams = await grpc.getCryptographicParameters();

      // Demo key placeholders (wallet normally provides these)
      const fakeHex = "1".repeat(64);

      const input = {
        arsInfos: selected.arsInfos,
        arThreshold: 1,
        ipInfo: selected.ipInfo,
        globalContext: cryptoParams,
        idCredSec: fakeHex,
        prfKey: fakeHex,
        blindingRandomness: fakeHex,
      };

      const request = createIdentityRequestWithKeys(input);
      const redirectUri = `${window.location.origin}/identity/callback`;
      const params = new URLSearchParams({
        scope: "identity",
        response_type: "code",
        redirect_uri: redirectUri,
        state: JSON.stringify({ request }),
      });

      window.location.href = `${selected.metadata.issuanceStart}?${params}`;
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
      <h3 className="text-sm font-medium text-gray-700 mb-2">
        Concordium Identity Verification
      </h3>
      {!account ? (
        <button
          onClick={connectWallet}
          className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700"
        >
          Connect Concordium Wallet
        </button>
      ) : (
        <button
          onClick={startVerification}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          Verify with Concordium
        </button>
      )}
      <p className="text-xs text-gray-500 mt-2">Status: {status}</p>
    </div>
  );
}
