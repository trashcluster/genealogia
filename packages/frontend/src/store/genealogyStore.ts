import create from 'zustand';

interface Individual {
  id: string;
  user_id: string;
  gedcom_id: string;
  given_names?: string;
  surname?: string;
  sex?: string;
  birth_date?: string;
  birth_place?: string;
  death_date?: string;
  death_place?: string;
  note?: string;
  created_at: string;
  updated_at: string;
}

interface GenealogyStore {
  individuals: Individual[];
  selectedIndividual: Individual | null;
  isLoading: boolean;
  error: string | null;
  fetchIndividuals: (token: string) => Promise<void>;
  createIndividual: (token: string, data: Partial<Individual>) => Promise<void>;
  updateIndividual: (token: string, id: string, data: Partial<Individual>) => Promise<void>;
  deleteIndividual: (token: string, id: string) => Promise<void>;
  selectIndividual: (individual: Individual | null) => void;
  setError: (error: string | null) => void;
}

export const useGenealogyStore = create<GenealogyStore>((set) => ({
  individuals: [],
  selectedIndividual: null,
  isLoading: false,
  error: null,

  fetchIndividuals: async (token: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch('http://localhost:8000/api/individuals', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch individuals');

      const data = await response.json();
      set({ individuals: data, isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Unknown error',
        isLoading: false,
      });
    }
  },

  createIndividual: async (token: string, data: Partial<Individual>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch('http://localhost:8000/api/individuals', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) throw new Error('Failed to create individual');

      const newIndividual = await response.json();
      set((state) => ({
        individuals: [...state.individuals, newIndividual],
        isLoading: false,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Unknown error',
        isLoading: false,
      });
    }
  },

  updateIndividual: async (token: string, id: string, data: Partial<Individual>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`http://localhost:8000/api/individuals/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) throw new Error('Failed to update individual');

      const updatedIndividual = await response.json();
      set((state) => ({
        individuals: state.individuals.map((ind) => (ind.id === id ? updatedIndividual : ind)),
        selectedIndividual: state.selectedIndividual?.id === id ? updatedIndividual : state.selectedIndividual,
        isLoading: false,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Unknown error',
        isLoading: false,
      });
    }
  },

  deleteIndividual: async (token: string, id: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`http://localhost:8000/api/individuals/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to delete individual');

      set((state) => ({
        individuals: state.individuals.filter((ind) => ind.id !== id),
        selectedIndividual: state.selectedIndividual?.id === id ? null : state.selectedIndividual,
        isLoading: false,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Unknown error',
        isLoading: false,
      });
    }
  },

  selectIndividual: (individual: Individual | null) => {
    set({ selectedIndividual: individual });
  },

  setError: (error: string | null) => {
    set({ error });
  },
}));
