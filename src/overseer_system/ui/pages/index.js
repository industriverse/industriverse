import React from 'react';
import { Box, CssBaseline } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import LoginPage from './login';
import Layout from '../components/layout/Layout';
import Dashboard from '../components/dashboard/Dashboard';

/**
 * Home page component that serves as the entry point for the application.
 * Handles authentication routing and renders the appropriate view based on
 * the user's authentication status.
 * 
 * This implements the Role-First, Context-Aware design principle by
 * adapting the UI based on authentication status and user role.
 */
export default function Home() {
  const { isAuthenticated, loading } = useAuth();

  // Show loading state while authentication is being checked
  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <img src="/assets/images/loading.svg" alt="Loading" width={80} height={80} />
      </Box>
    );
  }

  // If not authenticated, show login page
  if (!isAuthenticated) {
    return <LoginPage />;
  }

  // If authenticated, show main application layout with dashboard
  return (
    <>
      <CssBaseline />
      <Layout>
        <Dashboard />
      </Layout>
    </>
  );
}
