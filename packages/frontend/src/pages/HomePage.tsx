import React from 'react';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  UserGroupIcon, 
  ShareIcon, 
  ClockIcon, 
  DocumentArrowUpIcon,
  CameraIcon,
  BookOpenIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { api } from '../services/api';

const StatCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ElementType;
  color: string;
  href?: string;
}> = ({ title, value, icon: Icon, color, href }) => {
  const content = (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow p-6 border border-gray-200 hover:shadow-lg transition-shadow cursor-pointer"
    >
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
        </div>
      </div>
    </motion.div>
  );

  if (href) {
    return <Link to={href}>{content}</Link>;
  }
  return content;
};

export const HomePage: React.FC = () => {
  const { data: stats, isLoading } = useQuery(
    'dashboard-stats',
    () => api.get('/api/stats').then(res => res.data),
    { refetchInterval: 30000 }
  );

  const statsData = stats || {
    individuals: 0,
    families: 0,
    events: 0,
    documents: 0,
    photos: 0,
    recentIngestions: []
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome back! Here's an overview of your genealogy data.
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard
          title="Individuals"
          value={statsData.individuals}
          icon={UserGroupIcon}
          color="bg-blue-500"
          href="/individuals"
        />
        <StatCard
          title="Families"
          value={statsData.families}
          icon={ShareIcon}
          color="bg-green-500"
          href="/family-tree"
        />
        <StatCard
          title="Events"
          value={statsData.events}
          icon={ClockIcon}
          color="bg-purple-500"
          href="/timeline"
        />
        <StatCard
          title="Documents"
          value={statsData.documents}
          icon={BookOpenIcon}
          color="bg-yellow-500"
          href="/knowledge-base"
        />
        <StatCard
          title="Photos"
          value={statsData.photos}
          icon={CameraIcon}
          color="bg-pink-500"
          href="/face-recognition"
        />
        <StatCard
          title="Recent Ingestions"
          value={statsData.recentIngestions?.length || 0}
          icon={DocumentArrowUpIcon}
          color="bg-indigo-500"
          href="/ingestion"
        />
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        {statsData.recentIngestions?.length > 0 ? (
          <div className="space-y-3">
            {statsData.recentIngestions.map((ingestion: any, index: number) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100">
                <div className="flex items-center space-x-3">
                  <DocumentArrowUpIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {ingestion.source_type} - {ingestion.content_type}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(ingestion.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  ingestion.status === 'SUCCESS' 
                    ? 'bg-green-100 text-green-800'
                    : ingestion.status === 'ERROR'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {ingestion.status}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No recent activity</p>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/individuals?action=add"
            className="flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Individual
          </Link>
          <Link
            to="/face-recognition?action=upload"
            className="flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <CameraIcon className="h-5 w-5 mr-2" />
            Upload Photo
          </Link>
          <Link
            to="/knowledge-base?action=upload"
            className="flex items-center justify-center px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <BookOpenIcon className="h-5 w-5 mr-2" />
            Import Document
          </Link>
        </div>
      </div>

      {/* Features Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center mb-4">
            <div className="p-3 bg-indigo-100 rounded-lg">
              <DocumentArrowUpIcon className="h-6 w-6 text-indigo-600" />
            </div>
            <h3 className="ml-3 text-lg font-semibold text-gray-900">AI-Powered Ingestion</h3>
          </div>
          <p className="text-gray-600">
            Multiple AI providers (OpenAI, Claude, Ollama) automatically extract genealogical data from text, voice, images, and documents.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <CameraIcon className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="ml-3 text-lg font-semibold text-gray-900">Face Recognition</h3>
          </div>
          <p className="text-gray-600">
            Advanced face recognition automatically identifies and tags family members in photos, creating visual connections across your family tree.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center mb-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <BookOpenIcon className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="ml-3 text-lg font-semibold text-gray-900">Knowledge Base</h3>
          </div>
          <p className="text-gray-600">
            Centralized document storage with semantic search, event extraction, and correlation to enrich your family history.
          </p>
        </div>
      </div>
    </div>
  );
};
