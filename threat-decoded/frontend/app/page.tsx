"use client";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-2xl mx-auto px-6 py-20 text-center">
        <div className="mb-8">
          <span className="inline-block w-3 h-3 rounded-full bg-td-green mr-2" />
          <span className="text-td-green font-semibold text-sm uppercase tracking-widest">TD Threat Decoded</span>
        </div>
        <h1 className="text-4xl font-bold text-td-dark mb-4">
          Got a suspicious message claiming to be from TD?
        </h1>
        <p className="text-xl text-td-muted mb-12">
          Don't wonder — ask TD. And we'll reward you for staying sharp.
        </p>
        <p className="text-td-muted text-sm">[SubmitForm component — Phase 3]</p>
      </div>
    </main>
  );
}
