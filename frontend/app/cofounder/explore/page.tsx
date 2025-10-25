'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeftIcon, ChatBubbleLeftRightIcon, SparklesIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';

interface Profile {
  id: number;
  name: string;
  email: string;
  bio: string;
  role: string;
  skills: string[];
  startupInterests: string[];
  availability: string[];
  workStyle: string[];
  matchScore?: number;
  reason?: string;
}

export default function CofounderExplore() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null);

  useEffect(() => {
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    try {
      const response = await fetch('/api/profile');
      const data = await response.json();
      setProfiles(data.profiles || []);
    } catch (error) {
      console.error('Error fetching profiles:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const findMatches = async (profile: Profile) => {
    try {
      const response = await fetch('/api/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile })
      });
      const data = await response.json();
      setProfiles(data.matches || []);
    } catch (error) {
      console.error('Error finding matches:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto flex items-center justify-center py-20">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-gray-300 border-t-gray-900 rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="mb-8"
      >
        <Link href="/cofounder" className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors">
          <ArrowLeftIcon className="w-5 h-5" />
          Back to Cofounder Finder
        </Link>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Find Your Missing Piece</h1>
          <p className="text-gray-600 text-lg">
            Discover cofounders who complement your skills and share your vision
          </p>
        </div>

        {profiles.length === 0 ? (
          <div className="text-center py-12">
            <SparklesIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No profiles yet</h3>
            <p className="text-gray-600 mb-6">Be the first to create a profile and start finding matches!</p>
            <Link href="/cofounder/profile">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-gray-900 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors"
              >
                Create Profile
              </motion.button>
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {profiles.map((profile, index) => (
              <motion.div
                key={profile.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => setSelectedProfile(profile)}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center text-white font-bold text-lg">
                    {profile.name.charAt(0).toUpperCase()}
                  </div>
                  {profile.matchScore && (
                    <div className="bg-gray-900 text-white px-3 py-1 rounded-full text-sm font-semibold">
                      {profile.matchScore}% Match
                    </div>
                  )}
                </div>

                <h3 className="text-xl font-semibold text-gray-900 mb-2">{profile.name}</h3>
                <p className="text-gray-600 text-sm mb-3">{profile.role}</p>
                <p className="text-gray-700 text-sm mb-4 line-clamp-3">{profile.bio}</p>

                <div className="space-y-2 mb-4">
                  <div>
                    <span className="text-gray-500 text-xs font-medium">SKILLS:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {profile.skills.slice(0, 3).map(skill => (
                        <span key={skill} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">
                          {skill}
                        </span>
                      ))}
                      {profile.skills.length > 3 && (
                        <span className="text-gray-500 text-xs">+{profile.skills.length - 3} more</span>
                      )}
                    </div>
                  </div>

                  <div>
                    <span className="text-gray-500 text-xs font-medium">INTERESTS:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {profile.startupInterests.slice(0, 2).map(interest => (
                        <span key={interest} className="bg-gray-900 text-white text-xs px-2 py-1 rounded">
                          {interest}
                        </span>
                      ))}
                      {profile.startupInterests.length > 2 && (
                        <span className="text-gray-500 text-xs">+{profile.startupInterests.length - 2} more</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-gray-500 text-xs">
                    {profile.availability.join(', ')}
                  </div>
                  <button className="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-gray-800 transition-colors flex items-center gap-1">
                    <ChatBubbleLeftRightIcon className="w-4 h-4" />
                    Chat
                  </button>
                </div>

                {profile.reason && (
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <p className="text-gray-700 text-sm">
                      <span className="font-medium">Why this match:</span> {profile.reason}
                    </p>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>

      {/* Match Modal */}
      {selectedProfile && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center p-6 z-50"
          onClick={() => setSelectedProfile(null)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 bg-gray-900 rounded-full flex items-center justify-center text-white font-bold text-2xl">
                {selectedProfile.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedProfile.name}</h2>
                <p className="text-gray-600">{selectedProfile.role}</p>
                {selectedProfile.matchScore && (
                  <div className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-semibold inline-block mt-1">
                    {selectedProfile.matchScore}% Match
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">About</h3>
                <p className="text-gray-700">{selectedProfile.bio}</p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Skills & Expertise</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedProfile.skills.map(skill => (
                    <span key={skill} className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Startup Interests</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedProfile.startupInterests.map(interest => (
                    <span key={interest} className="bg-gray-900 text-white px-3 py-1 rounded-full text-sm">
                      {interest}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Availability & Work Style</h3>
                <div className="space-y-2">
                  <div>
                    <span className="text-gray-600">Availability: </span>
                    <span className="text-gray-900">{selectedProfile.availability.join(', ')}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Work Style: </span>
                    <span className="text-gray-900">{selectedProfile.workStyle.join(', ')}</span>
                  </div>
                </div>
              </div>

              {selectedProfile.reason && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2">Why This Match?</h3>
                  <p className="text-gray-700">{selectedProfile.reason}</p>
                </div>
              )}
            </div>

            <div className="flex gap-4 mt-8">
              <button className="flex-1 bg-gray-900 text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors flex items-center justify-center gap-2">
                <ChatBubbleLeftRightIcon className="w-5 h-5" />
                Start Chat
              </button>
              <button
                onClick={() => setSelectedProfile(null)}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
              >
                Close
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}
