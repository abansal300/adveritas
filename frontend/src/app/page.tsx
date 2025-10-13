"use client";
import { useState, useEffect } from "react";

// API URL - use environment variable in production, localhost in development
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [videoId, setVideoId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setVideoId(null);

    try {
      const formData = new FormData();
      formData.append("source_url", url);
      formData.append("title", "Fact Check Video");

      const res = await fetch(`${API_URL}/videos/ingest`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Failed to ingest video");

      const data = await res.json();
      setVideoId(data.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="border-b bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            AdVeritas
          </h1>
          <p className="text-slate-600 text-sm mt-1">AI-Powered Fact Checking for Video Content</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Input Form */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-xl font-semibold mb-4 text-slate-800">Analyze a Video</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-slate-700 mb-2">
                YouTube URL
              </label>
              <input
                type="text"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                disabled={loading}
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading || !url}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-md"
            >
              {loading ? "Processing..." : "Analyze Video"}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              <p className="font-medium">Error:</p>
              <p className="text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* Video Results */}
        {videoId && <VideoResults videoId={videoId} setVideoId={setVideoId} />}
      </main>
    </div>
  );
}

function VideoResults({ videoId, setVideoId }: { videoId: number; setVideoId: (id: number | null) => void }) {
  const [video, setVideo] = useState<any>(null);
  const [claims, setClaims] = useState<any[]>([]);
  const [selectedClaim, setSelectedClaim] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchVideo = async () => {
    const res = await fetch(`${API_URL}/videos/${videoId}`);
    const data = await res.json();
    setVideo(data);
    return data;
  };

  const fetchClaims = async () => {
    const res = await fetch(`${API_URL}/claims/video/${videoId}`);
    const data = await res.json();
    setClaims(data);
    return data;
  };

  const extractClaims = async () => {
    setLoading(true);
    try {
      await fetch(`${API_URL}/claims/video/${videoId}/extract`, {
        method: "POST",
      });

      // Poll for claims
      const interval = setInterval(async () => {
        const data = await fetchClaims();
        if (data.length > 0) {
          clearInterval(interval);
          setLoading(false);
        }
      }, 2000);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  useEffect(() => {
    if (videoId) {
      fetchVideo();
      fetchClaims();

      // Poll for video status updates
      const interval = setInterval(() => {
        fetchVideo();
        fetchClaims();
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [videoId]);

  const statusColor = video?.status === "TRANSCRIBED" ? "green" :
    video?.status === "PROCESSING" ? "yellow" : "gray";

  return (
    <div className="space-y-6">
      {/* Video Info */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-slate-800">Video Status</h2>
          <span className={`px-3 py-1 rounded-full text-sm font-medium bg-${statusColor}-100 text-${statusColor}-700`}>
            {video?.status || "Loading..."}
          </span>
        </div>

        {/* Thumbnail and Info Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          {video?.thumbnail_url && (
            <div className="md:col-span-1">
              <img
                src={video.thumbnail_url}
                alt={video.title || "Video thumbnail"}
                className="w-full rounded-lg shadow-md"
              />
            </div>
          )}
          <div className={`${video?.thumbnail_url ? 'md:col-span-2' : 'md:col-span-3'} space-y-2 text-sm text-slate-600`}>
            <p><strong>Title:</strong> {video?.title || "N/A"}</p>
            <p><strong>URL:</strong> <a href={video?.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">{video?.source_url}</a></p>
            {video?.duration && (
              <p><strong>Duration:</strong> {Math.floor(video.duration / 60)}:{String(Math.floor(video.duration % 60)).padStart(2, '0')}</p>
            )}
          </div>
        </div>

        {video?.status === "TRANSCRIBED" && claims.length === 0 && (
          <button
            onClick={extractClaims}
            disabled={loading}
            className="mt-4 w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
          >
            {loading ? "Extracting Claims..." : "Extract Claims"}
          </button>
        )}

        {video?.status === "QUEUED" && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700">
            <p className="font-medium">Processing...</p>
            <p className="text-sm">This video is being transcribed. Check back in a few minutes.</p>
            <button
              onClick={() => setVideoId(4)}
              className="mt-2 text-sm bg-yellow-600 text-white px-3 py-1 rounded hover:bg-yellow-700"
            >
              Test with Video ID 4 (Ready)
            </button>
          </div>
        )}
      </div>

      {/* Claims List */}
      {claims.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-slate-800">Claims Found ({claims.length})</h2>
          <div className="space-y-3">
            {claims.map((claim) => (
              <div
                key={claim.id}
                onClick={() => setSelectedClaim(claim.id)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition ${selectedClaim === claim.id
                  ? "border-blue-500 bg-blue-50"
                  : "border-slate-200 hover:border-blue-300"
                  }`}
              >
                <p className="text-slate-800">{claim.claim_text}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Claim Details */}
      {selectedClaim && <ClaimDetails claimId={selectedClaim} />}
    </div>
  );
}

function ClaimDetails({ claimId }: { claimId: number }) {
  const [evidence, setEvidence] = useState<any[]>([]);
  const [verdict, setVerdict] = useState<any>(null);
  const [loadingEvidence, setLoadingEvidence] = useState(false);
  const [loadingVerdict, setLoadingVerdict] = useState(false);

  const fetchEvidence = async () => {
    const res = await fetch(`${API_URL}/evidence/claim/${claimId}`);
    const data = await res.json();
    setEvidence(data);
    return data;
  };

  const fetchVerdict = async () => {
    const res = await fetch(`${API_URL}/verdicts/claim/${claimId}`);
    const data = await res.json();
    if (data.ok) {
      setVerdict(data);
    }
    return data;
  };

  const triggerEvidence = async () => {
    setLoadingEvidence(true);
    await fetch(`${API_URL}/evidence/claim/${claimId}/fetch`, {
      method: "POST",
    });

    const interval = setInterval(async () => {
      const data = await fetchEvidence();
      if (data.length > 0) {
        clearInterval(interval);
        setLoadingEvidence(false);
      }
    }, 2000);
  };

  const triggerVerdict = async () => {
    setLoadingVerdict(true);
    await fetch(`${API_URL}/verdicts/claim/${claimId}/generate`, {
      method: "POST",
    });

    const interval = setInterval(async () => {
      const data = await fetchVerdict();
      if (data.ok) {
        clearInterval(interval);
        setLoadingVerdict(false);
      }
    }, 3000);
  };

  useEffect(() => {
    fetchEvidence();
    fetchVerdict();
  }, [claimId]);

  const verdictColor = verdict?.label === "TRUE" ? "green" :
    verdict?.label === "FALSE" ? "red" :
      verdict?.label === "PARTLY_TRUE" ? "yellow" : "gray";

  return (
    <div className="space-y-6">
      {/* Evidence */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-800">Evidence</h3>
          {evidence.length === 0 && (
            <button
              onClick={triggerEvidence}
              disabled={loadingEvidence}
              className="bg-purple-600 text-white text-sm font-medium py-2 px-4 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition"
            >
              {loadingEvidence ? "Fetching..." : "Fetch Evidence"}
            </button>
          )}
        </div>

        {evidence.length > 0 ? (
          <div className="space-y-4">
            {evidence.map((item) => (
              <div key={item.id} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                <h4 className="font-semibold text-slate-800 mb-1">{item.title}</h4>
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:underline mb-2 block"
                >
                  {item.url}
                </a>
                <p className="text-sm text-slate-600">{item.snippet}</p>
                <p className="text-xs text-slate-500 mt-2">
                  Similarity: {(item.similarity * 100).toFixed(1)}%
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-500 text-sm">No evidence fetched yet</p>
        )}
      </div>

      {/* Verdict */}
      {evidence.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-800">Verdict</h3>
            {!verdict && (
              <button
                onClick={triggerVerdict}
                disabled={loadingVerdict}
                className="bg-green-600 text-white text-sm font-medium py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 transition"
              >
                {loadingVerdict ? "Generating..." : "Generate Verdict"}
              </button>
            )}
          </div>

          {verdict ? (
            <div className={`p-6 bg-${verdictColor}-50 border-2 border-${verdictColor}-200 rounded-lg`}>
              <div className="flex items-center justify-between mb-4">
                <span className={`text-2xl font-bold text-${verdictColor}-700`}>
                  {verdict.label.replace("_", " ")}
                </span>
                <span className={`text-lg font-semibold text-${verdictColor}-600`}>
                  {(verdict.confidence * 100).toFixed(0)}% confidence
                </span>
              </div>
              <p className="text-slate-700">{verdict.rationale}</p>
            </div>
          ) : (
            <p className="text-slate-500 text-sm">
              {loadingVerdict ? "Generating verdict (may take 30-60 seconds)..." : "No verdict generated yet"}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
