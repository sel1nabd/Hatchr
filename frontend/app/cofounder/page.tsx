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
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Find Your Perfect Cofounder</h1>
        <p className="text-gray-600 text-lg">
          Connect with complementary founders, developers, and visionaries who share your startup dreams.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex justify-center mb-8">
        <div className="bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('quick')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'quick'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Quick Match
          </button>
          <button
            onClick={() => setActiveTab('detailed')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'detailed'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Detailed Profile
          </button>
        </div>
      </div>

      {/* Quick Match Tab */}
      {activeTab === 'quick' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          {/* Features */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
              <UserGroupIcon className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Matching</h3>
              <p className="text-gray-600 text-sm">
                GPT-4 analyzes profiles and finds complementary cofounders based on skills and roles.
              </p>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
              <SparklesIcon className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Compatibility</h3>
              <p className="text-gray-600 text-sm">
                Match by startup domain, work style, availability, and complementary expertise areas.
              </p>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
              <ArrowRightIcon className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Built for Dreamers</h3>
              <p className="text-gray-600 text-sm">
                Connect with coders, builders, and visionaries ready to turn ideas into reality.
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/cofounder/profile">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-full sm:w-auto bg-gray-900 text-white px-8 py-4 rounded-lg font-semibold hover:bg-gray-800 transition-colors flex items-center justify-center gap-2"
              >
                Create Profile
                <ArrowRightIcon className="w-5 h-5" />
              </motion.button>
            </Link>
            <Link href="/cofounder/explore">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-full sm:w-auto border-2 border-gray-900 text-gray-900 px-8 py-4 rounded-lg font-semibold hover:bg-gray-900 hover:text-white transition-colors"
              >
                Explore Matches
              </motion.button>
            </Link>
          </div>

          {/* Integrated Figma-style suggestions */}
          <div className="mt-10">
            <FigmaStyleSuggestions />
          </div>
        </motion.div>
      )}

      {/* Detailed Profile Tab */}
      {activeTab === 'detailed' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-center"
        >
          <div className="max-w-2xl w-full">
            <CofounderForm />
          </div>
        </motion.div>
      )}
    </div>
  );
}
