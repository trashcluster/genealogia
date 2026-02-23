import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useDropzone } from 'react-dropzone';
import { 
  DocumentArrowUpIcon, 
  EyeIcon, 
  TrashIcon, 
  MagnifyingGlassIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { knowledgeAPI } from '../services/api';
import toast from 'react-hot-toast';

export const KnowledgeBasePage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [semanticQuery, setSemanticQuery] = useState('');
  const queryClient = useQueryClient();

  const { data: documents, isLoading } = useQuery(
    'documents',
    () => knowledgeAPI.getAll().then(res => res.data),
  );

  const { data: searchResults } = useQuery(
    ['document-search', searchQuery],
    () => searchQuery ? knowledgeAPI.search(searchQuery).then(res => res.data) : [],
    { enabled: !!searchQuery }
  );

  const uploadMutation = useMutation(
    (formData: FormData) => knowledgeAPI.upload(formData),
    {
      onSuccess: () => {
        toast.success('Document uploaded successfully');
        queryClient.invalidateQueries('documents');
      },
      onError: () => {
        toast.error('Failed to upload document');
      },
    }
  );

  const semanticSearchMutation = useMutation(
    (query: string) => knowledgeAPI.semanticSearch(query),
    {
      onSuccess: (data) => {
        toast.success(`Found ${data.length} relevant documents`);
      },
      onError: () => {
        toast.error('Search failed');
      },
    }
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      const formData = new FormData();
      acceptedFiles.forEach(file => {
        formData.append('files', file);
      });
      uploadMutation.mutate(formData);
    },
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'text/plain': ['.txt'],
      'text/html': ['.html'],
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload Documents</h2>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <DocumentArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          {isDragActive ? (
            <p className="text-gray-600">Drop the files here...</p>
          ) : (
            <div>
              <p className="text-gray-600 mb-2">Drag & drop documents here, or click to select</p>
              <p className="text-sm text-gray-500">Supports PDF, images, text, and HTML files</p>
            </div>
          )}
        </div>
      </div>

      {/* Search */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Keyword Search</h3>
          <div className="flex space-x-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search documents..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2"
            />
            <button className="p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
              <MagnifyingGlassIcon className="h-5 w-5" />
            </button>
          </div>
          {searchResults?.length > 0 && (
            <div className="mt-4 space-y-2">
              {searchResults.map((doc: any) => (
                <div key={doc.id} className="p-3 border border-gray-200 rounded-lg">
                  <h4 className="font-medium text-gray-900">{doc.title}</h4>
                  <p className="text-sm text-gray-500">{doc.filename}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Semantic Search</h3>
          <div className="flex space-x-2">
            <input
              type="text"
              value={semanticQuery}
              onChange={(e) => setSemanticQuery(e.target.value)}
              placeholder="Search by meaning..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2"
            />
            <button
              onClick={() => semanticQuery && semanticSearchMutation.mutate(semanticQuery)}
              className="p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              <MagnifyingGlassIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Documents List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Documents</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {documents?.length > 0 ? (
            documents.map((doc: any) => (
              <div key={doc.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                  <div>
                    <h3 className="font-medium text-gray-900">{doc.title}</h3>
                    <p className="text-sm text-gray-500">{doc.filename}</p>
                    <p className="text-xs text-gray-400">
                      {doc.file_size ? `${(doc.file_size / 1024).toFixed(1)} KB` : 'Unknown size'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="p-2 text-blue-600 hover:text-blue-800">
                    <EyeIcon className="h-5 w-5" />
                  </button>
                  <button className="p-2 text-red-600 hover:text-red-800">
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="px-6 py-12 text-center">
              <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No documents found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
