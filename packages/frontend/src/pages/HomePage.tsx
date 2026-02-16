import React from 'react';
import { FiUsers, FiUpload, FiTrendingUp } from 'react-icons/fi';

export const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Welcome to Genealogy</h1>
          <p className="text-xl text-gray-600">
            Import and manage your family history with AI-powered data extraction
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-lg shadow-md p-8">
            <div className="flex items-center justify-center w-12 h-12 bg-indigo-600 rounded-md text-white mb-4">
              <FiUpload size={24} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Multiple Input Methods</h3>
            <p className="text-gray-600">
              Import data through text, voice, images, PDFs, or CardDAV contacts. Use Telegram bot for quick additions.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-8">
            <div className="flex items-center justify-center w-12 h-12 bg-indigo-600 rounded-md text-white mb-4">
              <FiUsers size={24} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Family Tree Management</h3>
            <p className="text-gray-600">
              Organize your family information with GEDCOM-based structure. Track relationships, events, and sources.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-8">
            <div className="flex items-center justify-center w-12 h-12 bg-indigo-600 rounded-md text-white mb-4">
              <FiTrendingUp size={24} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Intelligence</h3>
            <p className="text-gray-600">
              Advanced AI understands genealogical context and automatically extracts and organizes family data.
            </p>
          </div>
        </div>

        <div className="mt-12 bg-indigo-600 rounded-lg shadow-md p-8 text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Get Started</h2>
          <p className="text-indigo-100 mb-6">
            Use our Telegram bot to quickly add family information, or visit the Family section to manage your data.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <a href="https://t.me/your-bot" target="_blank" rel="noopener noreferrer"
              className="bg-white text-indigo-600 px-6 py-2 rounded font-bold hover:bg-gray-100">
              Open Telegram Bot
            </a>
            <a href="/individuals"
              className="bg-indigo-700 text-white px-6 py-2 rounded font-bold hover:bg-indigo-800">
              View Family
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
