"use client";

import { motion } from "framer-motion";
import SubmitForm from "@/components/SubmitForm";
import NavBar from "@/components/NavBar";

export default function HomePage() {
  return (
    <>
      <NavBar />
      <main className="min-h-screen bg-white">
        <div className="max-w-xl mx-auto px-4 sm:px-6 py-12 sm:py-20">
          <motion.div
            className="text-center mb-10"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <div className="mb-6">
              <span className="inline-block w-3 h-3 rounded-full bg-td-green mr-2" />
              <span className="text-td-green font-semibold text-sm uppercase tracking-widest">
                TD Threat Decoded
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold text-td-dark mb-4 leading-tight text-balance">
              Got a suspicious message claiming to be from TD?
            </h1>
            <p className="text-base sm:text-lg text-td-muted">
              Don&apos;t wonder &mdash; ask TD. And we&apos;ll reward you for staying sharp.
            </p>
          </motion.div>
          <SubmitForm />
        </div>
      </main>
    </>
  );
}
