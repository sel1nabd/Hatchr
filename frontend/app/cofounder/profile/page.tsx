'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeftIcon, CheckIcon } from '@heroicons/react/24/outline';

const ROLES = [
  'Founder', 'CEO', 'CTO', 'CMO', 'Developer', 'Designer', 
  'Product Manager', 'Marketing Lead', 'Sales Lead', 'Operations'
];

const SKILLS = [
  'React', 'Node.js', 'Python', 'Machine Learning', 'Finance', 'Growth Marketing',
  'UX/UI Design', 'Product Strategy', 'Sales', 'Operations', 'Blockchain',
  'Mobile Development', 'Data Science', 'Content Marketing', 'Business Development'
];

const STARTUP_INTERESTS = [
  'Fintech', 'AI/ML', 'HealthTech', 'Web3', 'EdTech', 'E-commerce',
  'SaaS', 'Gaming', 'Social Media', 'Real Estate', 'Climate Tech', 'Cybersecurity'
];

const AVAILABILITY = ['Full-time', 'Part-time', 'Remote', 'Hybrid', 'Contract'];

const WORK_STYLES = [
  'Visionary', 'Executor', 'Communicator', 'Analytical', 'Creative', 'Strategic'
];

export default function CofounderProfileCreation() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    bio: '',
    role: '',
    skills: [] as string[],
    startupInterests: [] as string[],
    availability: [] as string[],
    workStyle: [] as string[]
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleMultiSelect = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field as keyof typeof prev].includes(value)
        ? (prev[field as keyof typeof prev] as string[]).filter(item => item !== value)
        : [...(prev[field as keyof typeof prev] as string[]), value]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch('/api/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        router.push('/cofounder/explore');
      }
    } catch (error) {
      console.error('Error saving profile:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="mb-8"
      >
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeftIcon className="w-5 h-5" />
          Back
        </button>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg border border-gray-200 shadow-sm p-8"
      >
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Create Your Cofounder Profile</h1>
        <p className="text-gray-600 mb-8">Tell us about yourself and what you're looking for in a cofounder.</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-medium mb-2">Name</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent"
                placeholder="Your full name"
              />
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-2">Email</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent"
                placeholder="your@email.com"
              />
            </div>
          </div>

          {/* Bio */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">Bio</label>
            <textarea
              required
              value={formData.bio}
              onChange={(e) => setFormData(prev => ({ ...prev, bio: e.target.value }))}
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent"
              placeholder="Tell us about your background, experience, and what drives you..."
            />
          </div>

          {/* Role */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">Primary Role</label>
            <select
              required
              value={formData.role}
              onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent"
            >
              <option value="">Select your role</option>
              {ROLES.map(role => (
                <option key={role} value={role}>{role}</option>
              ))}
            </select>
          </div>

          {/* Skills */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">Skills & Expertise</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {SKILLS.map(skill => (
                <button
                  key={skill}
                  type="button"
                  onClick={() => handleMultiSelect('skills', skill)}
                  className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                    formData.skills.includes(skill)
                      ? 'bg-gray-900 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {skill}
                </button>
              ))}
            </div>
          </div>

          {/* Startup Interests */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">Startup Interests</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {STARTUP_INTERESTS.map(interest => (
                <button
                  key={interest}
                  type="button"
                  onClick={() => handleMultiSelect('startupInterests', interest)}
                  className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                    formData.startupInterests.includes(interest)
                      ? 'bg-gray-900 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {interest}
                </button>
              ))}
            </div>
          </div>

          {/* Availability */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">Availability</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {AVAILABILITY.map(avail => (
                <button
                  key={avail}
                  type="button"
                  onClick={() => handleMultiSelect('availability', avail)}
                  className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                    formData.availability.includes(avail)
                      ? 'bg-gray-900 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {avail}
                </button>
              ))}
            </div>
          </div>

          {/* Work Style */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">Work Style</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {WORK_STYLES.map(style => (
                <button
                  key={style}
                  type="button"
                  onClick={() => handleMultiSelect('workStyle', style)}
                  className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                    formData.workStyle.includes(style)
                      ? 'bg-gray-900 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {style}
                </button>
              ))}
            </div>
          </div>

          <motion.button
            type="submit"
            disabled={isSubmitting}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full bg-gray-900 text-white py-4 rounded-lg font-semibold hover:bg-gray-800 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isSubmitting ? 'Creating Profile...' : 'Create Profile'}
            {!isSubmitting && <CheckIcon className="w-5 h-5" />}
          </motion.button>
        </form>
      </motion.div>
    </div>
  );
}
