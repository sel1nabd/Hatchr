
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { detectConcordiumProvider } from "@concordium/browser-wallet-api-helpers";
import {
  ConcordiumGRPCWebClient,
  createIdentityRequestWithKeys,
} from "@concordium/web-sdk";

export default function SignupPage() {
  const router = useRouter();

  // --- STATE ---
  const [provider, setProvider] = useState<any>(null);
  const [account, setAccount] = useState<string | null>(null);
  const [identityProviders, setIdentityProviders] = useState<any[]>([]);
  const [status, setStatus] = useState<string>("idle");
  const [result, setResult] = useState<string | null>(null);
  const [connecting, setConnecting] = useState(false);

  // --- FETCH AVAILABLE IDENTITY PROVIDERS ---
  useEffect(() => {
    fetch(
      "https://wallet-proxy.testnet.concordium.com/wallet-proxy/identityProviders"
    )
      .then((res) => res.json())
      .then(setIdentityProviders)
      .catch(console.error);
  }, []);

  // --- CONNECT TO WALLET ---
  async function connectWallet() {
    if (connecting) return; // prevent multiple popups
    setConnecting(true);

    try {
      const detected = await detectConcordiumProvider();
      await detected.connect();

      const acc = await detected.getMostRecentlySelectedAccount();
      if (!acc) {
        alert(
          "No account found in your Concordium Wallet. Please create one before connecting."
        );
        setConnecting(false);
        return;
      }

      setProvider(detected);
      setAccount(acc);
      console.log("✅ Connected wallet:", acc);
    } catch (e: any) {
      if (e.message?.includes("Another prompt is already open")) {
        alert("Please close the existing Concordium popup before retrying.");
      } else {
        console.error(e);
        alert("Connection failed. Please ensure your wallet is unlocked.");
      }
    } finally {
      setConnecting(false);
    }
  }

  // --- START IDENTITY VERIFICATION ---
  async function startVerification() {
    if (!identityProviders.length) {
      alert("No identity providers available on testnet.");
      return;
    }

    // Make sure wallet is connected
    if (!provider || !account) {
      alert("Please connect your Concordium wallet first.");
      return;
    }

    const selected = identityProviders[0];
    setStatus("creating");

    try {
      const grpc = new ConcordiumGRPCWebClient(
        "grpc.testnet.concordium.com",
        20000
      );
      const cryptoParams = await grpc.getCryptographicParameters();

      // NOTE: These are dummy values; real wallets use secure keys internally
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

      const redirectUri = window.location.origin + "/signup";
      const params = new URLSearchParams({
        scope: "identity",
        response_type: "code",
        redirect_uri: redirectUri,
        state: JSON.stringify({ request }),
      });

      const startUrl = `${selected.metadata.issuanceStart}?${params}`;
      window.open(startUrl, "_blank", "width=600,height=800");

      setStatus("waiting_for_verification");
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  }

  // --- HANDLE CALLBACK FROM IDENTITY PROVIDER ---
  useEffect(() => {
    const hash = window.location.hash;
    if (!hash) return;

    const params = new URLSearchParams(hash.replace("#", ""));
    const codeUri = params.get("code_uri");
    if (!codeUri) return;

    setStatus("fetching_result");

    fetch(codeUri)
      .then((res) => res.json())
      .then((data) => {
        console.log("Concordium identity result:", data);
        setResult(data.status || "unknown");
        setStatus("done");

        // ✅ Redirect to main page on success
        if (data.status === "done") {
          setTimeout(() => router.push("/"), 2000);
        }
      })
      .catch((err) => {
        console.error(err);
        setStatus("error");
      });
  }, [router]);

  // --- UI ---
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-md p-8 border border-gray-200">
        <h1 className="text-2xl font-semibold text-gray-900 mb-4">
          Sign Up with Concordium
        </h1>
        <p className="text-gray-600 text-sm mb-8">
          Verify your decentralized identity on the Concordium Testnet to access
          the main application.
        </p>

        {/* Wallet Connect */}
        {!account ? (
          <button
            onClick={connectWallet}
            disabled={connecting}
            className={`w-full px-4 py-2 rounded-lg text-sm font-medium transition-colors ${connecting
              ? "bg-gray-400 text-white cursor-not-allowed"
              : "bg-green-600 text-white hover:bg-green-700"
              }`}
          >
            {connecting ? "Connecting..." : "Connect Concordium Wallet"}
          </button>
        ) : (
          <button
            onClick={startVerification}
            disabled={
              status === "waiting_for_verification" ||
              status === "creating" ||
              status === "fetching_result"
            }
            className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${status === "waiting_for_verification" ||
              status === "creating" ||
              status === "fetching_result"
              ? "bg-gray-400 text-white cursor-not-allowed"
              : "bg-blue-600 text-white hover:bg-blue-700"
              }`}
          >
            {status === "creating" && "Preparing verification..."}
            {status === "waiting_for_verification" && "Waiting for verification..."}
            {status === "fetching_result" && "Retrieving verification result..."}
            {status === "idle" && "Verify with Concordium"}
            {status === "error" && "Retry Verification"}
          </button>
        )}

        {/* Status + Result */}
        <div className="mt-6 text-sm text-gray-700">
          <p>Status: {status}</p>
          {result && (
            <p>
              Result:{" "}
              <span
                className={
                  result === "done" ? "text-green-600 font-medium" : "text-red-600"
                }
              >
                {result}
              </span>
            </p>
          )}
        </div>

        {/* Verified message */}
        {result === "done" && (
          <p className="mt-4 text-green-700 text-sm font-medium">
            ✅ Verified! Redirecting to main page...
          </p>
        )}
      </div>
    </div>
  );
}

