import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';

import SystemMetrics from './SystemMetrics';
import ProjectList from './ProjectList';
import AgentManager from './AgentManager';
import SecurityPanel from './SecurityPanel';
import ControlPanel from './ControlPanel';
import { Agent, Project, SystemStatus } from '../types';

const API_BASE = 'http://localhost:8080/api';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    cpu_usage: 0,
    memory_usage: 0,
    projects: 0,
    agents: 0,
  });
  const [systemRunning, setSystemRunning] = useState<'running' | 'stopped'>('stopped');
  const [projects, setProjects] = useState<Project[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);

  useEffect(() => {
    fetchSystemStatus();
    fetchProjects();
    fetchAgents();
    const interval = setInterval(() => {
      fetchSystemStatus();
      fetchProjects();
      fetchAgents();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/system/status`);
      if (!response.ok) {
        throw new Error('Failed to fetch system status');
      }
      const data = await response.json();
      setSystemStatus(data);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await fetch(`${API_BASE}/projects`);
      if (!response.ok) {
        throw new Error('Failed to fetch projects');
      }
      const data = await response.json();
      setProjects(data);
    } catch (err) {
      console.error('Error fetching projects:', err);
    }
  };

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_BASE}/agents`);
      if (!response.ok) {
        throw new Error('Failed to fetch agents');
      }
      const data = await response.json();
      setAgents(data);
    } catch (err) {
      console.error('Error fetching agents:', err);
    }
  };

  const handleStartSystem = async () => {
    try {
      const response = await fetch(`${API_BASE}/system/start`, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to start system');
      }
      setSystemRunning('running');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start system');
    }
  };

  const handleStopSystem = async () => {
    try {
      const response = await fetch(`${API_BASE}/system/stop`, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to stop system');
      }
      setSystemRunning('stopped');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop system');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ m: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, mt: 4 }}>
      <Container maxWidth="lg">
        <Grid container spacing={3}>
          {/* System Metrics */}
          <Grid item xs={12}>
            <SystemMetrics
              cpuUsage={systemStatus.cpu_usage}
              memoryUsage={systemStatus.memory_usage}
              projectCount={systemStatus.projects}
              agentCount={systemStatus.agents}
            />
          </Grid>

          {/* Control Panel */}
          <Grid item xs={12} md={6}>
            <ControlPanel
              systemStatus={systemRunning}
              onStart={handleStartSystem}
              onStop={handleStopSystem}
            />
          </Grid>

          {/* Security Panel */}
          <Grid item xs={12} md={6}>
            <SecurityPanel />
          </Grid>

          {/* Project List */}
          <Grid item xs={12} md={6}>
            <ProjectList
              projects={projects}
              onRefresh={fetchProjects}
            />
          </Grid>

          {/* Agent Manager */}
          <Grid item xs={12} md={6}>
            <AgentManager
              agents={agents}
              onRefresh={fetchAgents}
            />
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Dashboard;
