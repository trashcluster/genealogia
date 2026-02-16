import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { useGenealogyStore } from '../store/genealogyStore';
import { FiPlus, FiEdit2, FiTrash2 } from 'react-icons/fi';

export const IndividualsPage: React.FC = () => {
  const { token } = useAuthStore();
  const {
    individuals,
    isLoading,
    error,
    fetchIndividuals,
    deleteIndividual,
    selectIndividual,
  } = useGenealogyStore();

  const [showForm, setShowForm] = useState(false);
  const [surname, setSurname] = useState('');
  const [givenNames, setGivenNames] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (token) {
      fetchIndividuals(token);
    }
  }, [token, fetchIndividuals]);

  const filteredIndividuals = individuals.filter(
    (ind) =>
      (ind.surname?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false) ||
      (ind.given_names?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false)
  );

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this individual?')) {
      if (token) {
        await deleteIndividual(token, id);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Family Members</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
          >
            <FiPlus /> Add Member
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <div className="mb-6">
          <input
            type="text"
            placeholder="Search by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
          />
        </div>

        {showForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Add New Member</h2>
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Given names"
                value={givenNames}
                onChange={(e) => setGivenNames(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
              <input
                type="text"
                placeholder="Surname"
                value={surname}
                onChange={(e) => setSurname(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
              <div className="flex gap-2">
                <button
                  onClick={() => setShowForm(false)}
                  className="flex-1 px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  onClick={() => setShowForm(false)}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Add Member
                </button>
              </div>
            </div>
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-8">
            <p className="text-gray-600">Loading...</p>
          </div>
        ) : filteredIndividuals.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-600">No family members found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredIndividuals.map((individual) => (
              <div key={individual.id} className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-900">
                  {individual.given_names} {individual.surname}
                </h3>
                {individual.birth_date && (
                  <p className="text-gray-600">b. {individual.birth_date}</p>
                )}
                {individual.birth_place && (
                  <p className="text-gray-600">{individual.birth_place}</p>
                )}
                {individual.death_date && (
                  <p className="text-gray-600">
                    d. {individual.death_date}
                    {individual.death_place && ` - ${individual.death_place}`}
                  </p>
                )}
                {individual.note && (
                  <p className="text-gray-600 mt-2 text-sm italic">{individual.note}</p>
                )}
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => selectIndividual(individual)}
                    className="flex-1 flex items-center justify-center gap-2 bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700"
                  >
                    <FiEdit2 size={16} /> Edit
                  </button>
                  <button
                    onClick={() => handleDelete(individual.id)}
                    className="flex-1 flex items-center justify-center gap-2 bg-red-600 text-white px-3 py-2 rounded hover:bg-red-700"
                  >
                    <FiTrash2 size={16} /> Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
