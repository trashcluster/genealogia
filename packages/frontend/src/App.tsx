import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './store/authStore';
import { Navbar } from './components/Navbar';
import { LoginPage } from './pages/LoginPage';
import { HomePage } from './pages/HomePage';
import { IndividualsPage } from './pages/IndividualsPage';
import { FamilyTreePage } from './pages/FamilyTreePage';
import { TimelinePage } from './pages/TimelinePage';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { FaceRecognitionPage } from './pages/FaceRecognitionPage';
import { IngestionPage } from './pages/IngestionPage';
import { SettingsPage } from './pages/SettingsPage';
import './styles/index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route
                path="/"
                element={
                  <PrivateRoute>
                    <HomePage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/individuals"
                element={
                  <PrivateRoute>
                    <IndividualsPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/family-tree"
                element={
                  <PrivateRoute>
                    <FamilyTreePage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/timeline"
                element={
                  <PrivateRoute>
                    <TimelinePage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/knowledge-base"
                element={
                  <PrivateRoute>
                    <KnowledgeBasePage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/face-recognition"
                element={
                  <PrivateRoute>
                    <FaceRecognitionPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/ingestion"
                element={
                  <PrivateRoute>
                    <IngestionPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/settings"
                element={
                  <PrivateRoute>
                    <SettingsPage />
                  </PrivateRoute>
                }
              />
            </Routes>
          </main>
        </div>
        <Toaster position="top-right" />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
