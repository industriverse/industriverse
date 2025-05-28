import React from 'react';
import { AppProps } from 'next/app';
import Head from 'next/head';
import AppProvider from '../contexts/AppProvider';

/**
 * Custom App component for Next.js that wraps the entire application
 * with the AppProvider to provide theme, authentication, UI state,
 * event bus, and data context to all components.
 */
function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>Overseer System</title>
        <meta name="viewport" content="minimum-scale=1, initial-scale=1, width=device-width" />
        <meta name="description" content="Overseer System - Industrial Foundry Framework Control Room" />
      </Head>
      <AppProvider>
        <Component {...pageProps} />
      </AppProvider>
    </>
  );
}

export default MyApp;
