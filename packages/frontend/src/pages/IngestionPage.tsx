import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useDropzone } from 'react-dropzone';
import { 
  DocumentArrowUpIcon, 
  MicrophoneIcon,
  ChatBubbleLeftRightIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { ingestionAPI } from '../services/api';
import toast from 'react-hot-toast';

export const IngestionPage: React.FC = () => {
  const [textInput, setTextInput] = useState('');
  const [selectedAI, setSelectedAI] = useState('openai');
  const queryClient = useQueryClient();

  const { data: history } = useQuery(
    'ingestion-history',
    () => ingestionAPI.getHistory().then(res => res.data),
  );

  const textMutation = useMutation(
    (data: { text: string; ai_provider?: string }) => ingestionAPI.processText(data),
    {
      onSuccess: () => {
        toast.success('Text processed successfully');
        setTextInput('');
        queryClient.invalidateQueries('ingestion-history');
      },
      onError: () => {
        toast.error('Text processing failed');
      },
    }
  );

  const voiceMutation = useMutation(
    (formData: FormData) => ingestionAPI.processVoice(formData),
    {
      onSuccess: () => {
        toast.success('Voice processed successfully');
        queryClient.invalidateQueries('ingestion-history');
      },
      onError: () => {
        toast.error('Voice processing failed');
      },
    }
  );

  const documentMutation = useMutation(
    (formData: FormData) => ingestionAPI.processDocument(formData),
    {
      onSuccess: () => {
        toast.success('Document processed successfully');
        queryClient.invalidateQueries('ingestion-history');
      },
      onError: () => {
        toast.error('Document processing failed');
      },
    }
  );

  const { getRootProps: getVoiceProps, getInputProps: getVoiceInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      const formData = new FormData();
      acceptedFiles.forEach(file => {
        formData.append('voice', file);
      });
      voiceMutation.mutate(formData);
    },
    accept: {
      'audio/*': ['.mp3', '.wav', '.m4a', '.ogg'],
    },
  });

  const { getRootProps: getDocumentProps, getInputProps: getDocumentInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      const formData = new FormData();
      acceptedFiles.forEach(file => {
        formData.append('document', file);
      });
      formData.append('ai_provider', selectedAI);
      documentMutation.mutate(formData);
    },
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'text/plain': ['.txt'],
    },
  });

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      textMutation.mutate({ text: textInput, ai_provider: selectedAI });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Data Ingestion</h1>
      </div>

      {/* AI Provider Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Provider</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { id: 'openai', name: 'OpenAI GPT-4', description: 'Most capable model' },
            { id: 'claude', name: 'Claude', description: 'Balanced performance' },
            { id: 'ollama', name: 'Ollama', description: 'Local models' },
          ].map((provider) => (
            <button
              key={provider.id}
              onClick={() => setSelectedAI(provider.id)}
              className={`p-4 rounded-lg border-2 text-left transition-colors ${
                selectedAI === provider.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <h3 className="font-medium text-gray-900">{provider.name}</h3>
              <p className="text-sm text-gray-500">{provider.description}</p>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Text Input */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Text Input</h2>
          <textarea
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Enter genealogical information, family stories, or historical data..."
            className="w-full h-32 border border-gray-300 rounded-lg px-3 py-2 mb-4"
          />
          <button
            onClick={handleTextSubmit}
            disabled={textMutation.isLoading || !textInput.trim()}
            className="w-full bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {textMutation.isLoading ? 'Processing...' : 'Process Text'}
          </button>
        </div>

        {/* Voice Input */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Voice Input</h2>
          <div
            {...getVoiceProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              voiceMutation.isLoading ? 'border-gray-300 bg-gray-50' : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getVoiceInputProps()} />
            <MicrophoneIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            {voiceMutation.isLoading ? (
              <p className="text-gray-600">Processing voice...</p>
            ) : (
              <div>
                <p className="text-gray-600 mb-2">Drag & drop audio file</p>
                <p className="text-sm text-gray-500">Supports MP3, WAV, M4A, OGG</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Document Upload */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Document Upload</h2>
        <div
          {...getDocumentProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            documentMutation.isLoading ? 'border-gray-300 bg-gray-50' : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getDocumentInputProps()} />
          <DocumentArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          {documentMutation.isLoading ? (
            <p className="text-gray-600">Processing document...</p>
          ) : (
            <div>
              <p className="text-gray-600 mb-2">Drag & drop documents</p>
              <p className="text-sm text-gray-500">Supports PDF, images, text files</p>
            </div>
          )}
        </div>
      </div>

      {/* Ingestion History */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Ingestions</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {history?.length > 0 ? (
            history.slice(0, 10).map((item: any) => (
              <div key={item.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${
                      item.content_type === 'TEXT' ? 'bg-blue-100' :
                      item.content_type === 'VOICE' ? 'bg-green-100' :
                      item.content_type === 'DOCUMENT' ? 'bg-purple-100' :
                      'bg-gray-100'
                    }`}>
                      {item.content_type === 'TEXT' && <ChatBubbleLeftRightIcon className="h-4 w-4 text-blue-600" />}
                      {item.content_type === 'VOICE' && <MicrophoneIcon className="h-4 w-4 text-green-600" />}
                      {item.content_type === 'DOCUMENT' && <DocumentArrowUpIcon className="h-4 w-4 text-purple-600" />}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        {item.source_type} - {item.content_type}
                      </p>
                      <p className="text-sm text-gray-500">
                        {item.ai_provider_used} • {new Date(item.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      item.status === 'SUCCESS' 
                        ? 'bg-green-100 text-green-800'
                        : item.status === 'ERROR'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {item.status}
                    </span>
                    {item.processing_time_ms && (
                      <span className="text-xs text-gray-500">
                        {item.processing_time_ms}ms
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="px-6 py-12 text-center">
              <DocumentArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No ingestion history found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
