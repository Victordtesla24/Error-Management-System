import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Button,
  IconButton,
  Alert,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  Stop as StopIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Components
import SystemMetrics from './SystemMetrics';
import ProjectList from './ProjectList';
import AgentManager from './AgentManager';
import SecurityPanel from './SecurityPanel';
import ControlPanel from './ControlPanel';

interface SystemStatus {
  projects: number;
  agents: number;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  uptime: number;
}

interface Project {
  id: string;
  path: string;
  active: boolean;
  error_count: number;
  last_scan: number;
  agents: string[];
}

interface Agent {
  id: string;
  project_id: string | null;
  cpu_usage: number;
  memory_usage: number;
  status: string;
  last_active: number;
}

const Dashboard: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metricsHistory, setMetricsHistory] = useState<any[]>([]);

  // Fetch data periodically
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusRes, projectsRes, agentsRes] = await Promise.all([
          fetch('/api/system/status'),
          fetch('/api/projects'),
          fetch('/api/agents'),
        ]);

        if (!statusRes.ok || !projectsRes.ok || !agentsRes.ok) {
          throw new Error('Failed to fetch data');
        }

        const status = await statusRes.json();
        const projectsData = await projectsRes.json();
        const agentsData = await agentsRes.json();

        setSystemStatus(status);
        setProjects(projectsData);
        setAgents(agentsData);

        // Update metrics history
        setMetricsHistory(prev => [
          ...prev,
          {
            time: new Date().toLocaleTimeString(),
            cpu: status.cpu_usage,
            memory: status.memory_usage,
          },
        ].slice(-20)); // Keep last 20 data points

        setError(null);
      } catch (err) {
        setError('Failed to fetch system data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    // Trigger useEffect
  };

  const handleStartSystem = async () => {
    try {
      const res = await fetch('/api/system/start', { method: 'POST' });
      if (!res.ok) throw new Error('Failed to start system');
      handleRefresh();
    } catch (err) {
      setError('Failed to start system');
      console.error(err);
    }
  };

  const handleStopSystem = async () => {
    try {
      const res = await fetch('/api/system/stop', { method: 'POST' });
      if (!res.ok) throw new Error('Failed to stop system');
      handleRefresh();
    } catch (err) {
      setError('Failed to stop system');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box py={4}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Header */}
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h4">Error Management System Dashboard</Typography>
              <Box>
                <IconButton onClick={handleRefresh}>
                  <RefreshIcon />
                </IconButton>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<PlayArrowIcon />}
                  onClick={handleStartSystem}
                  sx={{ mr: 1 }}
                >
                  Start
                </Button>
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<StopIcon />}
                  onClick={handleStopSystem}
                >
                  Stop
                </Button>
              </Box>
            </Box>
          </Grid>

          {/* System Metrics */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                System Metrics
              </Typography>
              <SystemMetrics
                cpu={systemStatus?.cpu_usage || 0}
                memory={systemStatus?.memory_usage || 0}
                disk={systemStatus?.disk_usage || 0}
              />
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={metricsHistory}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="cpu" stroke="#8884d8" name="CPU" />
                  <Line type="monotone" dataKey="memory" stroke="#82ca9d" name="Memory" />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          {/* Security Panel */}
          <Grid item xs={12} md={4}>
            <SecurityPanel />
          </Grid>

          {/* Project List */}
          <Grid item xs={12} md={6}>
            <ProjectList projects={projects} onRefresh={handleRefresh} />
          </Grid>

          {/* Agent Manager */}
          <Grid item xs={12} md={6}>
            <AgentManager agents={agents} onRefresh={handleRefresh} />
          </Grid>

          {/* Control Panel */}
          <Grid item xs={12}>
            <ControlPanel
              systemStatus={systemStatus}
              onStart={handleStartSystem}
              onStop={handleStopSystem}
            />
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Dashboard;
