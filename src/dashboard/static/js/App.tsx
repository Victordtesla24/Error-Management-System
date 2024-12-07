import React from 'react';
import { Box, Container } from '@mui/material';
import Dashboard from './components/Dashboard';

const App: React.FC = () => {
  return (
    <Box sx={{ 
      minHeight: '100vh',
      backgroundColor: 'background.default',
      py: 3
    }}>
      <Container maxWidth="xl">
        <Dashboard />
      </Container>
    </Box>
  );
};

export default App;
