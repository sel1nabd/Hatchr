'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { UserGroupIcon, SparklesIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import { CofounderForm } from "@/components/CofounderForm";
import FigmaStyleSuggestions from "@/components/FigmaStyleSuggestions";

export default function CofounderFinderPage() {
  const [activeTab, setActiveTab] = useState<'quick' | 'detailed'>('quick');

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 px-6 py-12 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 right-20 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob" />
        <div className="absolute bottom-20 left-20 w-72 h-72 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000" />
      </div>

      <div className="max-w-4xl mx-auto relative z-10">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Find Your Perfect Cofounder</h1>
          <p className="text-gray-600 text-lg">Connect with complementary founders, developers, and visionaries who share your startup dreams.</p>
        </div>

        {/* Tabs */}
        <div className="flex justify-center mb-8">
          <div className="bg-white/80 backdrop-blur-xl rounded-lg border border-white/20 shadow-sm p-1">
            <button
              onClick={() => setActiveTab('quick')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${activeTab === 'quick' ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow' : 'text-gray-700 hover:text-gray-900'}`}
            >
              Quick Match
            </button>
            <button
              onClick={() => setActiveTab('detailed')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${activeTab === 'detailed' ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow' : 'text-gray-700 hover:text-gray-900'}`}
            >
              Detailed Profile
            </button>
          </div>
        </div>

        {/* Quick Match Tab */}
        {activeTab === 'quick' && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
            <div className="grid md:grid-cols-3 gap-6 mb-2">
              <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-white/20 p-6 text-center shadow">
                <UserGroupIcon className="w-10 h-10 text-gray-700 mx-auto mb-3" />
                <h3 className="text-base font-semibold text-gray-900 mb-1">AI-Powered Matching</h3>
                <p className="text-gray-600 text-sm">Find complementary cofounders based on skills and roles.</p>
              </div>
              <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-white/20 p-6 text-center shadow">
                <SparklesIcon className="w-10 h-10 text-gray-700 mx-auto mb-3" />
                <h3 className="text-base font-semibold text-gray-900 mb-1">Smart Compatibility</h3>
                <p className="text-gray-600 text-sm">Match by domain, work style, and experience level.</p>
              </div>
              <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-white/20 p-6 text-center shadow">
                <ArrowRightIcon className="w-10 h-10 text-gray-700 mx-auto mb-3" />
                <h3 className="text-base font-semibold text-gray-900 mb-1">Built for Builders</h3>
                <p className="text-gray-600 text-sm">Connect with coders, operators, and visionaries ready to ship.</p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/cofounder/profile" className="w-full sm:w-auto">
                <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-3 rounded-lg font-semibold shadow">
                  Create Profile
                </motion.button>
              </Link>
              <Link href="/cofounder/explore" className="w-full sm:w-auto">
                <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="w-full border border-slate-300 bg-white text-gray-900 px-8 py-3 rounded-lg font-semibold hover:border-indigo-300">
                  Explore Matches
                </motion.button>
              </Link>
            </div>

            <div className="mt-8">
              <FigmaStyleSuggestions />
            </div>
          </motion.div>
        )}

        {/* Detailed Profile Tab */}
        {activeTab === 'detailed' && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex justify-center">
            <div className="max-w-2xl w-full bg-white/80 backdrop-blur-xl rounded-2xl border border-white/20 p-6 shadow">
              <CofounderForm />
            </div>
          </motion.div>
        )}
      </div>

      <style>{`
        @keyframes blob { 0%,100%{ transform: translate(0,0) scale(1);} 33%{ transform: translate(30px,-50px) scale(1.1);} 66%{ transform: translate(-20px,20px) scale(0.9);} }
        .animate-blob { animation: blob 7s infinite; }
        .animation-delay-2000 { animation-delay: 2s; }
      `}</style>
    </div>
  );
}
