import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { PlusIcon, EyeIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { individualsAPI } from '../services/api';

export const FamilyTreePage: React.FC = () => {
  const { data: individuals, isLoading } = useQuery(
    'individuals',
    () => individualsAPI.getAll().then(res => res.data),
  );

  const { data: families } = useQuery(
    'families',
    () => individualsAPI.getAll().then(res => res.data),
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Family Tree</h1>
        <div className="flex space-x-4">
          <Link
            to="/individuals?action=add"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Individual
          </Link>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Interactive Family Tree</h2>
        <div className="h-96 bg-gray-100 rounded-lg flex items-center justify-center">
          <p className="text-gray-500">Family tree visualization will be implemented here</p>
          <p className="text-gray-400 text-sm">Using D3.js or React Flow for interactive visualization</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Individuals</h2>
          {individuals?.length > 0 ? (
            <div className="space-y-3">
              {individuals.slice(0, 5).map((individual: any) => (
                <div key={individual.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">
                      {individual.given_names} {individual.surname}
                    </p>
                    <p className="text-sm text-gray-500">
                      {individual.birth_date ? `Born: ${individual.birth_date}` : 'Birth date unknown'}
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <Link
                      to={`/individuals/${individual.id}`}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      <EyeIcon className="h-5 w-5" />
                    </Link>
                    <Link
                      to={`/individuals/${individual.id}/edit`}
                      className="text-green-600 hover:text-green-800"
                    >
                      <PencilIcon className="h-5 w-5" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No individuals found</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Family Groups</h2>
          {families?.length > 0 ? (
            <div className="space-y-3">
              {families.slice(0, 5).map((family: any) => (
                <div key={family.id} className="p-3 border border-gray-200 rounded-lg">
                  <p className="font-medium text-gray-900">
                    {family.husband_name || 'Unknown'} & {family.wife_name || 'Unknown'}
                  </p>
                  <p className="text-sm text-gray-500">
                    {family.marriage_date ? `Married: ${family.marriage_date}` : 'Marriage date unknown'}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No family groups found</p>
          )}
        </div>
      </div>
    </div>
  );
};
