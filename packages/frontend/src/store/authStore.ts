import create from 'zustand';

interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

interface AuthStore {
  user: User | null;
  token: string | null;
  apiKey: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  setToken: (token: string) => void;
  setApiKey: (apiKey: string) => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  apiKey: localStorage.getItem('apiKey'),
  isAuthenticated: !!localStorage.getItem('token'),

  login: async (username: string, password: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) throw new Error('Login failed');

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      set({
        token: data.access_token,
        isAuthenticated: true,
      });
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  register: async (username: string, email: string, password: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });

      if (!response.ok) throw new Error('Registration failed');

      const data = await response.json();
      localStorage.setItem('apiKey', data.api_key);
      set({
        apiKey: data.api_key,
        user: data,
      });
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('apiKey');
    set({
      user: null,
      token: null,
      apiKey: null,
      isAuthenticated: false,
    });
  },

  setToken: (token: string) => {
    localStorage.setItem('token', token);
    set({ token, isAuthenticated: true });
  },

  setApiKey: (apiKey: string) => {
    localStorage.setItem('apiKey', apiKey);
    set({ apiKey });
  },
}));
