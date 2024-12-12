import React from 'react';
import { createRoot } from 'react-dom/client';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import App from './App';

const container = document.getElementById('root');
if (!container) {
  throw new Error('Failed to find the root element');
}

const root = createRoot(container);

root.render(
  <React.StrictMode>
    <CssBaseline />
    <Box
      component="main"
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        width: '100%',
        bgcolor: '#f5f5f5'
      }}
    >
      <App />
    </Box>
  </React.StrictMode>
);
