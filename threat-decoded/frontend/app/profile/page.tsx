"use client";

import { useEffect, useState } from "react";
import NavBar from "@/components/NavBar";
import ScoreCard from "@/components/ScoreCard";
import { getProfile, UserProfile } from "@/lib/api";

// For the hackathon demo, use a default user ID from the seed data
const DEMO_USER_ID = "user_1";

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getProfile(DEMO_USER_ID)
      .then(setProfile)
      .catch(() => setError("Could not load profile. Make sure the backend is running and seeded."));
  }, []);

  return (
    <>
      <NavBar />
      <main className="min-h-screen bg-white">
        <div className="max-w-lg mx-auto px-6 py-12">
          {error && (
            <div className="text-center py-20">
              <p className="text-td-fraud text-sm">{error}</p>
            </div>
          )}
          {!error && !profile && (
            <div className="text-center py-20">
              <div className="flex items-center justify-center gap-2 text-td-muted text-sm">
                <div className="w-4 h-4 border-2 border-td-green border-t-transparent rounded-full animate-spin" />
                Loading profile&hellip;
              </div>
            </div>
          )}
          {profile && <ScoreCard profile={profile} />}
        </div>
      </main>
    </>
  );
}
