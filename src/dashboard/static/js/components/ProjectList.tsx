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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Folder as FolderIcon,
} from '@mui/icons-material';

interface Project {
  id: string;
  path: string;
  active: boolean;
  error_count: number;
  last_scan: number;
  agents: string[];
}

interface ProjectListProps {
  projects: Project[];
  onRefresh: () => void;
}

const ProjectList: React.FC<ProjectListProps> = ({ projects, onRefresh }) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [newProjectPath, setNewProjectPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddProject = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path: newProjectPath }),
      });

      if (!response.ok) {
        throw new Error('Failed to add project');
      }

      setOpenDialog(false);
      setNewProjectPath('');
      onRefresh();
    } catch (err) {
      setError('Failed to add project. Please check the path and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveProject = async (projectId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/projects/${projectId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to remove project');
      }

      onRefresh();
    } catch (err) {
      setError('Failed to remove project');
    } finally {
      setLoading(false);
    }
  };

  const formatLastScan = (timestamp: number) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Projects</Typography>
        <Box>
          <IconButton onClick={onRefresh} size="small" sx={{ mr: 1 }}>
            <RefreshIcon />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
          >
            Add Project
          </Button>
        </Box>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <List>
        {projects.map((project) => (
          <ListItem
            key={project.id}
            divider
            sx={{
              backgroundColor: project.active ? 'action.hover' : 'background.paper',
            }}
          >
            <ListItemText
              primary={
                <Box display="flex" alignItems="center">
                  <FolderIcon sx={{ mr: 1 }} />
                  <Typography>{project.path}</Typography>
                </Box>
              }
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Last Scan: {formatLastScan(project.last_scan)}
                  </Typography>
                  <Box mt={1}>
                    {project.active ? (
                      <Chip
                        size="small"
                        label="Active"
                        color="success"
                        icon={<CheckCircleIcon />}
                      />
                    ) : (
                      <Chip
                        size="small"
                        label="Inactive"
                        color="default"
                      />
                    )}
                    {project.error_count > 0 && (
                      <Tooltip title={`${project.error_count} errors detected`}>
                        <Chip
                          size="small"
                          label={project.error_count}
                          color="error"
                          icon={<ErrorIcon />}
                          sx={{ ml: 1 }}
                        />
                      </Tooltip>
                    )}
                    {project.agents.length > 0 && (
                      <Chip
                        size="small"
                        label={`${project.agents.length} agents`}
                        color="primary"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </Box>
                </Box>
              }
            />
            <ListItemSecondaryAction>
              <IconButton
                edge="end"
                onClick={() => handleRemoveProject(project.id)}
                disabled={loading}
              >
                <DeleteIcon />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
        {projects.length === 0 && (
          <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
            No projects added yet
          </Typography>
        )}
      </List>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Add New Project</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Project Path"
            fullWidth
            value={newProjectPath}
            onChange={(e) => setNewProjectPath(e.target.value)}
            disabled={loading}
            placeholder="/path/to/project"
            helperText="Enter the absolute path to your project directory"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleAddProject}
            variant="contained"
            disabled={!newProjectPath || loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default ProjectList;
