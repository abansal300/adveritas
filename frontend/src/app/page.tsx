"use client";
import { useEffect, useState } from "react";

export default function Home() {
  const [status, setStatus] = useState<string>("Loading...");

  useEffect(() => {
    fetch("http://localhost:8000/health")
      .then(r => r.json())
      .then(j => setStatus(JSON.stringify(j)))
      .catch(() => setStatus("API not reachable"));
  }, []);

  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-bold mb-4">AdVeritas</h1>
      <p className="font-mono">Backend status: {status}</p>
    </main>
  );
}