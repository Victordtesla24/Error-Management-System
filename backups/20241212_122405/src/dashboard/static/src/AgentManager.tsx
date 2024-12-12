import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import Chip from '@mui/material/Chip';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Timeline from '@mui/lab/Timeline';
import TimelineItem from '@mui/lab/TimelineItem';
import TimelineSeparator from '@mui/lab/TimelineSeparator';
import TimelineConnector from '@mui/lab/TimelineConnector';
import TimelineContent from '@mui/lab/TimelineContent';
import TimelineDot from '@mui/lab/TimelineDot';
import TimelineOppositeContent from '@mui/lab/TimelineOppositeContent';
import { Add, Refresh, Message, Delete } from '@mui/icons-material';
import { Agent } from '../types';

const API_BASE = 'http://localhost:8080/api';

interface AgentManagerProps {
  agents: Agent[];
  onRefresh: () => void;
}

const AgentManager: React.FC<AgentManagerProps> = ({ agents, onRefresh }) => {
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [messageDialogOpen, setMessageDialogOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [agentType, setAgentType] = useState('');
  const [roles, setRoles] = useState<string[]>([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const availableRoles = [
    'Error Handler',
    'Code Reviewer',
    'Test Engineer',
    'Debug Specialist',
    'Performance Optimizer',
    'Security Auditor'
  ];

  const handleCreateAgent = async () => {
    if (!agentType || roles.length === 0) {
      setError('Agent type and at least one role are required');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/agents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: agentType,
          roles: roles,
          apiKey: 'temp-key', // In a real app, this would be properly managed
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create agent');
      }

      setAddDialogOpen(false);
      setAgentType('');
      setRoles([]);
      setError('');
      onRefresh();
    } catch (err) {
      console.error('Failed to create agent:', err);
      setError('Failed to create agent');
    }
  };

  const handleSendMessage = async () => {
    if (!selectedAgent || !message) {
      setError('Message is required');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/agents/${selectedAgent.id}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      setMessageDialogOpen(false);
      setSelectedAgent(null);
      setMessage('');
      setError('');
      onRefresh();
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message');
    }
  };

  const handleDragStart = (e: React.DragEvent, agent: Agent) => {
    e.dataTransfer.setData('application/json', JSON.stringify({
      type: 'agent',
      agentId: agent.id
    }));
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Agents
        </Typography>
        <Box>
          <IconButton onClick={onRefresh} size="small" sx={{ mr: 1 }}>
            <Refresh />
          </IconButton>
          <Button
            variant="contained"
            size="small"
            startIcon={<Add />}
            onClick={() => setAddDialogOpen(true)}
          >
            Add Agent
          </Button>
        </Box>
      </Box>

      <List>
        {agents.map((agent) => (
          <ListItem
            key={agent.id}
            draggable
            onDragStart={(e) => handleDragStart(e, agent)}
            sx={{
              border: '1px solid #e0e0e0',
              borderRadius: 1,
              mb: 1,
              cursor: 'grab',
              '&:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.04)',
              },
            }}
          >
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="subtitle1">{agent.type}</Typography>
                  <Chip
                    label={agent.status}
                    color={agent.status === 'active' ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
              }
              secondary={
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Roles: {agent.roles.join(', ')}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Last Active: {new Date(agent.lastActive).toLocaleString()}
                  </Typography>
                </Box>
              }
            />
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton
                size="small"
                onClick={() => {
                  setSelectedAgent(agent);
                  setMessageDialogOpen(true);
                }}
              >
                <Message />
              </IconButton>
            </Box>
          </ListItem>
        ))}
      </List>

      {/* Add Agent Dialog */}
      <Dialog
        open={addDialogOpen}
        onClose={() => {
          setAddDialogOpen(false);
          setAgentType('');
          setRoles([]);
          setError('');
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add Agent</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth
              label="Agent Type"
              value={agentType}
              onChange={(e) => setAgentType(e.target.value)}
              error={!!error && !agentType}
              helperText={error && !agentType ? 'Agent type is required' : ''}
            />
            <FormControl fullWidth>
              <InputLabel>Roles</InputLabel>
              <Select
                multiple
                value={roles}
                onChange={(e) => setRoles(typeof e.target.value === 'string' ? [e.target.value] : e.target.value)}
                error={!!error && roles.length === 0}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} size="small" />
                    ))}
                  </Box>
                )}
              >
                {availableRoles.map((role) => (
                  <MenuItem key={role} value={role}>
                    {role}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setAddDialogOpen(false);
            setAgentType('');
            setRoles([]);
            setError('');
          }}>
            Cancel
          </Button>
          <Button onClick={handleCreateAgent} variant="contained">
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Send Message Dialog */}
      <Dialog
        open={messageDialogOpen}
        onClose={() => {
          setMessageDialogOpen(false);
          setSelectedAgent(null);
          setMessage('');
          setError('');
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Send Message to Agent</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Typography variant="subtitle1">
              Agent: {selectedAgent?.type}
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              error={!!error && !message}
              helperText={error && !message ? 'Message is required' : ''}
              placeholder="Enter instructions or queries for the agent..."
            />
            {selectedAgent?.history && selectedAgent.history.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Agent History
                </Typography>
                <Timeline>
                  {selectedAgent.history.map((entry, index) => (
                    <TimelineItem key={index}>
                      <TimelineOppositeContent color="text.secondary">
                        {new Date(entry.timestamp).toLocaleString()}
                      </TimelineOppositeContent>
                      <TimelineSeparator>
                        <TimelineDot color={entry.result === 'Success' ? 'success' : 'primary'} />
                        {index < selectedAgent.history.length - 1 && <TimelineConnector />}
                      </TimelineSeparator>
                      <TimelineContent>
                        <Typography>{entry.action}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {entry.result}
                        </Typography>
                      </TimelineContent>
                    </TimelineItem>
                  ))}
                </Timeline>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setMessageDialogOpen(false);
            setSelectedAgent(null);
            setMessage('');
            setError('');
          }}>
            Cancel
          </Button>
          <Button onClick={handleSendMessage} variant="contained">
            Send
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default AgentManager;
