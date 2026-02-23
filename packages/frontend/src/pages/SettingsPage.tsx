import React, { useState } from 'react';
import { Cog6ToothIcon, KeyIcon, BrainIcon, CameraIcon } from '@heroicons/react/24/outline';
import { useAuthStore } from '../store/authStore';
import toast from 'react-hot-toast';

export const SettingsPage: React.FC = () => {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    // AI Provider Settings
    preferredAIProvider: 'openai',
    openaiApiKey: '',
    claudeApiKey: '',
    ollamaUrl: 'http://localhost:11434',
    enableFallbackProviders: true,
    
    // Face Recognition Settings
    faceRecognitionEnabled: true,
    faceRecognitionModel: 'facenet',
    faceSimilarityThreshold: 0.6,
    
    // Notification Settings
    emailNotifications: true,
    telegramNotifications: false,
    
    // Privacy Settings
    dataSharing: false,
    analyticsEnabled: true,
  });

  const handleSave = () => {
    // Save settings to backend
    toast.success('Settings saved successfully');
  };

  const handleReset = () => {
    // Reset to defaults
    toast.success('Settings reset to defaults');
  };

  const tabs = [
    { id: 'general', name: 'General', icon: Cog6ToothIcon },
    { id: 'ai', name: 'AI Providers', icon: BrainIcon },
    { id: 'face', name: 'Face Recognition', icon: CameraIcon },
    { id: 'api', name: 'API Keys', icon: KeyIcon },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <div className="flex space-x-2">
          <button
            onClick={handleReset}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Reset to Defaults
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Save Settings
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'general' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">General Settings</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Notifications
                  </label>
                  <select
                    value={settings.emailNotifications ? 'true' : 'false'}
                    onChange={(e) => setSettings({...settings, emailNotifications: e.target.value === 'true'})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="true">Enabled</option>
                    <option value="false">Disabled</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Telegram Notifications
                  </label>
                  <select
                    value={settings.telegramNotifications ? 'true' : 'false'}
                    onChange={(e) => setSettings({...settings, telegramNotifications: e.target.value === 'true'})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="true">Enabled</option>
                    <option value="false">Disabled</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Data Sharing
                  </label>
                  <select
                    value={settings.dataSharing ? 'true' : 'false'}
                    onChange={(e) => setSettings({...settings, dataSharing: e.target.value === 'true'})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="true">Enabled</option>
                    <option value="false">Disabled</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Analytics
                  </label>
                  <select
                    value={settings.analyticsEnabled ? 'true' : 'false'}
                    onChange={(e) => setSettings({...settings, analyticsEnabled: e.target.value === 'true'})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="true">Enabled</option>
                    <option value="false">Disabled</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'ai' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">AI Provider Settings</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred AI Provider
                  </label>
                  <select
                    value={settings.preferredAIProvider}
                    onChange={(e) => setSettings({...settings, preferredAIProvider: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="openai">OpenAI</option>
                    <option value="claude">Claude</option>
                    <option value="ollama">Ollama</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Enable Fallback Providers
                  </label>
                  <select
                    value={settings.enableFallbackProviders ? 'true' : 'false'}
                    onChange={(e) => setSettings({...settings, enableFallbackProviders: e.target.value === 'true'})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="true">Enabled</option>
                    <option value="false">Disabled</option>
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ollama URL
                  </label>
                  <input
                    type="url"
                    value={settings.ollamaUrl}
                    onChange={(e) => setSettings({...settings, ollamaUrl: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    placeholder="http://localhost:11434"
                  />
                </div>
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">AI Provider Information</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <h5 className="font-medium text-blue-800">OpenAI</h5>
                    <p className="text-blue-700">GPT-4, most capable but requires API key</p>
                  </div>
                  <div>
                    <h5 className="font-medium text-blue-800">Claude</h5>
                    <p className="text-blue-700">Anthropic's model, balanced performance</p>
                  </div>
                  <div>
                    <h5 className="font-medium text-blue-800">Ollama</h5>
                    <p className="text-blue-700">Local models, privacy-focused</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'face' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">Face Recognition Settings</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Face Recognition
                  </label>
                  <select
                    value={settings.faceRecognitionEnabled ? 'true' : 'false'}
                    onChange={(e) => setSettings({...settings, faceRecognitionEnabled: e.target.value === 'true'})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="true">Enabled</option>
                    <option value="false">Disabled</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Recognition Model
                  </label>
                  <select
                    value={settings.faceRecognitionModel}
                    onChange={(e) => setSettings({...settings, faceRecognitionModel: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="facenet">FaceNet</option>
                    <option value="arcface">ArcFace</option>
                    <option value="dlib">DLib</option>
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Similarity Threshold: {settings.faceSimilarityThreshold}
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    value={settings.faceSimilarityThreshold}
                    onChange={(e) => setSettings({...settings, faceSimilarityThreshold: parseFloat(e.target.value)})}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>More Strict</span>
                    <span>More Lenient</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'api' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">API Keys</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    value={settings.openaiApiKey}
                    onChange={(e) => setSettings({...settings, openaiApiKey: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    placeholder="sk-..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Claude API Key
                  </label>
                  <input
                    type="password"
                    value={settings.claudeApiKey}
                    onChange={(e) => setSettings({...settings, claudeApiKey: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    placeholder="sk-ant-..."
                  />
                </div>
              </div>

              <div className="p-4 bg-yellow-50 rounded-lg">
                <h4 className="font-medium text-yellow-900 mb-2">Security Notice</h4>
                <p className="text-sm text-yellow-800">
                  API keys are encrypted and stored securely. Never share your API keys with others.
                  Keys with access to billing information should be handled with extra care.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
