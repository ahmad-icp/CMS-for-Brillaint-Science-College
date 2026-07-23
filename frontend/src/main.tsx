import React from 'react';
import ReactDOM from 'react-dom/client';

import { App } from './app/App';
import { AuthProvider } from './auth/AuthContext';
import { installAuthenticatedFetch } from './services/auth';
import './styles.css';

installAuthenticatedFetch();

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <AuthProvider><App /></AuthProvider>
  </React.StrictMode>,
);
