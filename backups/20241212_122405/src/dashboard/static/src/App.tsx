import React from 'react';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Dashboard from './components/Dashboard';

const App: React.FC = () => {
  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default', py: 3 }}>
      <Container maxWidth="lg">
        <Dashboard />
      </Container>
    </Box>
  );
};

export default App;
