import React from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from '../styles/theme';
import { AuthProvider } from '../contexts/AuthContext';
import { UIStateProvider } from '../contexts/UIStateContext';
import { EventBusProvider } from '../contexts/EventBusContext';
import { DataProvider } from '../contexts/DataContext';

/**
 * Main application wrapper that provides theme, authentication, UI state,
 * event bus, and data context to all components.
 * 
 * This follows the Role-First, Context-Aware design principle by ensuring
 * all components have access to authentication and role information.
 */
const AppProvider = ({ children }) => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <UIStateProvider>
          <EventBusProvider>
            <DataProvider>
              {children}
            </DataProvider>
          </EventBusProvider>
        </UIStateProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default AppProvider;
