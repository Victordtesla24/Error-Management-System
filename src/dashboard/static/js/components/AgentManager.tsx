import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Chip,
  Tooltip,
  CircularProgress,
  LinearProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
} from '@mui/icons-material';

interface Agent {
  id: string;
  project_id: string | null;
  cpu_usage: number;
  memory_usage: number;
  status: string;
  last_active: number;
}

interface AgentManagerProps {
  agents: Agent[];
  onRefresh: () => void;
}

const AgentManager: React.FC<AgentManagerProps> = ({ agents, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateAgent = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/agents', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to create agent');
      }

      onRefresh();
    } catch (err) {
      setError('Failed to create agent');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveAgent = async (agentId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/agents/${agentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to remove agent');
      }

      onRefresh();
    } catch (err) {
      setError('Failed to remove agent');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string): "default" | "primary" | "error" | "warning" | "success" => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'success';
      case 'idle':
        return 'primary';
      case 'error':
        return 'error';
      case 'busy':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatLastActive = (timestamp: number) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Agents</Typography>
        <Box>
          <IconButton onClick={onRefresh} size="small" sx={{ mr: 1 }}>
            <RefreshIcon />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateAgent}
            disabled={loading}
          >
            Create Agent
          </Button>
        </Box>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <List>
        {agents.map((agent) => (
          <ListItem
            key={agent.id}
            divider
            sx={{
              backgroundColor: agent.status.toLowerCase() === 'active' ? 'action.hover' : 'background.paper',
            }}
          >
            <ListItemText
              primary={
                <Box display="flex" alignItems="center">
                  <MemoryIcon sx={{ mr: 1 }} />
                  <Typography>Agent {agent.id}</Typography>
                  <Chip
                    size="small"
                    label={agent.status}
                    color={getStatusColor(agent.status)}
                    sx={{ ml: 1 }}
                  />
                </Box>
              }
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Last Active: {formatLastActive(agent.last_active)}
                  </Typography>
                  <Box mt={1}>
                    <Tooltip title="CPU Usage">
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={agent.cpu_usage}
                          color={agent.cpu_usage > 80 ? 'error' : 'primary'}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          CPU: {agent.cpu_usage}%
                        </Typography>
                      </Box>
                    </Tooltip>
                    <Tooltip title="Memory Usage">
                      <Box sx={{ width: '100%', mt: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={agent.memory_usage}
                          color={agent.memory_usage > 80 ? 'error' : 'primary'}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          Memory: {agent.memory_usage}%
                        </Typography>
                      </Box>
                    </Tooltip>
                  </Box>
                  {agent.project_id && (
                    <Chip
                      size="small"
                      label={`Project: ${agent.project_id}`}
                      color="info"
                      sx={{ mt: 1 }}
                    />
                  )}
                </Box>
              }
            />
            <ListItemSecondaryAction>
              <IconButton
                edge="end"
                onClick={() => handleRemoveAgent(agent.id)}
                disabled={loading}
                sx={{ ml: 1 }}
              >
                <DeleteIcon />
              </IconButton>
              {agent.status.toLowerCase() === 'active' ? (
                <IconButton
                  edge="end"
                  color="error"
                  disabled={loading}
                >
                  <StopIcon />
                </IconButton>
              ) : (
                <IconButton
                  edge="end"
                  color="success"
                  disabled={loading}
                >
                  <PlayArrowIcon />
                </IconButton>
              )}
            </ListItemSecondaryAction>
          </ListItem>
        ))}
        {agents.length === 0 && (
          <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
            No agents created yet
          </Typography>
        )}
      </List>
    </Paper>
  );
};

export default AgentManager;
