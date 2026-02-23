import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useDropzone } from 'react-dropzone';
import { 
  CameraIcon, 
  UserGroupIcon, 
  MagnifyingGlassIcon,
  UserIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { faceRecognitionAPI } from '../services/api';
import toast from 'react-hot-toast';

export const FaceRecognitionPage: React.FC = () => {
  const [selectedPerson, setSelectedPerson] = useState('');
  const queryClient = useQueryClient();

  const { data: stats } = useQuery(
    'face-stats',
    () => faceRecognitionAPI.getStats().then(res => res.data),
  );

  const { data: clusters } = useQuery(
    'face-clusters',
    () => faceRecognitionAPI.getClusters().then(res => res.data),
  );

  const detectMutation = useMutation(
    (formData: FormData) => faceRecognitionAPI.detectFaces(formData),
    {
      onSuccess: (data) => {
        toast.success(`Detected ${data.faces.length} faces`);
        queryClient.invalidateQueries('face-stats');
      },
      onError: () => {
        toast.error('Face detection failed');
      },
    }
  );

  const registerMutation = useMutation(
    (formData: FormData) => faceRecognitionAPI.registerFace(formData),
    {
      onSuccess: () => {
        toast.success('Face registered successfully');
        queryClient.invalidateQueries('face-clusters');
      },
      onError: () => {
        toast.error('Face registration failed');
      },
    }
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      const formData = new FormData();
      acceptedFiles.forEach(file => {
        formData.append('image', file);
      });
      detectMutation.mutate(formData);
    },
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
    },
  });

  const { getRootProps: getRegisterProps, getInputProps: getRegisterInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      const formData = new FormData();
      acceptedFiles.forEach(file => {
        formData.append('image', file);
      });
      formData.append('person_name', selectedPerson);
      registerMutation.mutate(formData);
    },
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Face Recognition</h1>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <CameraIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Total Photos</p>
              <p className="text-xl font-semibold text-gray-900">{stats?.total_photos || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <UserIcon className="h-8 w-8 text-green-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Detected Faces</p>
              <p className="text-xl font-semibold text-gray-900">{stats?.total_faces || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <UserGroupIcon className="h-8 w-8 text-purple-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Identified People</p>
              <p className="text-xl font-semibold text-gray-900">{stats?.identified_people || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-yellow-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Clusters</p>
              <p className="text-xl font-semibold text-gray-900">{clusters?.length || 0}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Face Detection */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Detect Faces</h2>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <CameraIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            {isDragActive ? (
              <p className="text-gray-600">Drop the image here...</p>
            ) : (
              <div>
                <p className="text-gray-600 mb-2">Drag & drop an image to detect faces</p>
                <p className="text-sm text-gray-500">Supports PNG, JPG, JPEG</p>
              </div>
            )}
          </div>
          {detectMutation.data && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">Detection Results</h3>
              <p className="text-sm text-gray-600">
                Found {detectMutation.data.faces.length} face(s) in the image
              </p>
            </div>
          )}
        </div>

        {/* Face Registration */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Register Face</h2>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Person Name</label>
            <input
              type="text"
              value={selectedPerson}
              onChange={(e) => setSelectedPerson(e.target.value)}
              placeholder="Enter person's name"
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            />
          </div>
          <div
            {...getRegisterProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getRegisterInputProps()} />
            <UserIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            {isDragActive ? (
              <p className="text-gray-600">Drop the image here...</p>
            ) : (
              <div>
                <p className="text-gray-600 mb-2">Drag & drop an image to register face</p>
                <p className="text-sm text-gray-500">Add a person name above first</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Face Clusters */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Face Clusters</h2>
        </div>
        <div className="p-6">
          {clusters?.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {clusters.map((cluster: any) => (
                <div key={cluster.id} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">
                    {cluster.person_name || `Person ${cluster.id}`}
                  </h3>
                  <p className="text-sm text-gray-500 mb-3">
                    {cluster.face_count} face(s)
                  </p>
                  <div className="grid grid-cols-3 gap-2">
                    {cluster.sample_faces?.map((face: any, index: number) => (
                      <img
                        key={index}
                        src={face.thumbnail_url}
                        alt={`Face ${index + 1}`}
                        className="w-full h-20 object-cover rounded"
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <UserGroupIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No face clusters found</p>
              <p className="text-sm text-gray-400 mt-2">Upload some photos to get started</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
