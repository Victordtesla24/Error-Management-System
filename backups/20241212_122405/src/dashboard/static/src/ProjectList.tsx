import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemSecondaryAction from '@mui/material/ListItemSecondaryAction';
import IconButton from '@mui/material/IconButton';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import Chip from '@mui/material/Chip';
import Collapse from '@mui/material/Collapse';
import { Add, Delete, Refresh, ExpandMore, ChevronRight, Close, BugReport } from '@mui/icons-material';
import { Project, Agent, ErrorReport } from '../types';

const API_BASE = 'http://localhost:8080/api';

interface ProjectListProps {
  projects: Project[];
  onRefresh: () => void;
}

interface FileTreeProps {
  node: {
    name: string;
    type: 'file' | 'directory';
    children?: any[];
  };
  level: number;
  expanded: boolean;
  onToggle: () => void;
}

const FileTree: React.FC<FileTreeProps> = ({ node, level, expanded, onToggle }) => {
  const [isExpanded, setIsExpanded] = React.useState(false);

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  return (
    <Box sx={{ ml: level * 2 }}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          cursor: node.type === 'directory' ? 'pointer' : 'default',
          py: 0.5,
          '&:hover': {
            bgcolor: 'rgba(0, 0, 0, 0.04)',
          },
        }}
        onClick={node.type === 'directory' ? handleToggle : undefined}
      >
        {node.type === 'directory' && (
          <IconButton size="small" sx={{ p: 0.5 }}>
            {isExpanded ? <ExpandMore /> : <ChevronRight />}
          </IconButton>
        )}
        <Typography
          variant="body2"
          sx={{
            ml: node.type === 'file' ? 3.5 : 0.5,
            color: node.type === 'directory' ? 'primary.main' : 'text.primary',
          }}
        >
          {node.name}
        </Typography>
      </Box>
      {node.type === 'directory' && node.children && (
        <Collapse in={isExpanded}>
          {node.children.map((child, index) => (
            <FileTree 
              key={`${child.name}-${index}`} 
              node={child} 
              level={level + 1}
              expanded={false}
              onToggle={handleToggle}
            />
          ))}
        </Collapse>
      )}
    </Box>
  );
};

const ProjectList: React.FC<ProjectListProps> = ({ projects, onRefresh }) => {
  const [expandedProjects, setExpandedProjects] = useState<{ [key: string]: boolean }>({});
  const [errorDialogOpen, setErrorDialogOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [addProjectDialogOpen, setAddProjectDialogOpen] = useState(false);
  const [projectPath, setProjectPath] = useState('');
  const [error, setError] = useState('');

  const handleAddProject = async () => {
    if (!projectPath) {
      setError('Project path is required');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path: projectPath }),
      });

      if (!response.ok) {
        throw new Error('Failed to add project');
      }

      setAddProjectDialogOpen(false);
      setProjectPath('');
      setError('');
      onRefresh();
    } catch (err) {
      console.error('Failed to add project:', err);
      setError('Failed to add project. Please check the path and try again.');
    }
  };

  const handleUnassignAgent = async (projectId: string, agentId: string) => {
    try {
      const response = await fetch(`${API_BASE}/projects/${projectId}/agents/${agentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to unassign agent');
      }

      onRefresh();
    } catch (err) {
      console.error('Failed to unassign agent:', err);
    }
  };

  const handleDrop = async (projectId: string, item: { type: string, agentId: string }) => {
    if (item.type === 'agent') {
      try {
        const response = await fetch(`${API_BASE}/projects/${projectId}/agents/${item.agentId}`, {
          method: 'POST',
        });

        if (!response.ok) {
          throw new Error('Failed to assign agent');
        }

        onRefresh();
      } catch (err) {
        console.error('Failed to assign agent:', err);
      }
    }
  };

  const toggleProjectExpansion = (projectId: string) => {
    setExpandedProjects(prev => ({
      ...prev,
      [projectId]: !prev[projectId]
    }));
  };

  const handleViewErrors = (project: Project) => {
    setSelectedProject(project);
    setErrorDialogOpen(true);
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Projects
        </Typography>
        <Box>
          <IconButton onClick={onRefresh} size="small" sx={{ mr: 1 }}>
            <Refresh />
          </IconButton>
          <Button
            variant="contained"
            size="small"
            startIcon={<Add />}
            onClick={() => setAddProjectDialogOpen(true)}
          >
            Add Project
          </Button>
        </Box>
      </Box>

      <List>
        {projects.map((project) => (
          <ListItem
            key={project.id}
            sx={{
              flexDirection: 'column',
              alignItems: 'flex-start',
              border: '1px solid #e0e0e0',
              borderRadius: 1,
              mb: 1,
              p: 2,
              '&.drag-over': {
                backgroundColor: 'rgba(25, 118, 210, 0.08)',
                borderColor: 'primary.main',
              },
            }}
            onDragOver={(e) => {
              e.preventDefault();
              e.currentTarget.classList.add('drag-over');
            }}
            onDragLeave={(e) => {
              e.currentTarget.classList.remove('drag-over');
            }}
            onDrop={(e) => {
              e.preventDefault();
              e.currentTarget.classList.remove('drag-over');
              const data = JSON.parse(e.dataTransfer.getData('application/json'));
              handleDrop(project.id, data);
            }}
          >
            <Box sx={{ width: '100%', display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                  {project.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {project.path}
                </Typography>
              </Box>
              <Box>
                <IconButton
                  size="small"
                  onClick={() => handleViewErrors(project)}
                  sx={{ mr: 1 }}
                >
                  <BugReport />
                </IconButton>
                <Chip
                  label={project.status}
                  color={project.status === 'active' ? 'success' : 'default'}
                  size="small"
                  sx={{ mr: 1 }}
                />
                <IconButton
                  size="small"
                  onClick={() => toggleProjectExpansion(project.id)}
                >
                  {expandedProjects[project.id] ? <ExpandMore /> : <ChevronRight />}
                </IconButton>
              </Box>
            </Box>

            {/* Assigned Agents */}
            {project.assigned_agents && project.assigned_agents.length > 0 && (
              <Box sx={{ mt: 1, width: '100%' }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Assigned Agents
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {project.assigned_agents.map((agent) => (
                    <Chip
                      key={agent.id}
                      label={`${agent.type} (${agent.roles.join(', ')})`}
                      color={agent.status === 'active' ? 'primary' : 'default'}
                      size="small"
                      onDelete={() => handleUnassignAgent(project.id, agent.id)}
                      deleteIcon={<Close fontSize="small" />}
                    />
                  ))}
                </Box>
              </Box>
            )}

            {project.structure && (
              <Collapse in={expandedProjects[project.id]} sx={{ width: '100%' }}>
                <Box sx={{ mt: 2, border: '1px solid #e0e0e0', borderRadius: 1, p: 1 }}>
                  {project.structure.map((node, index) => (
                    <FileTree 
                      key={`${node.name}-${index}`} 
                      node={node} 
                      level={0}
                      expanded={expandedProjects[project.id]}
                      onToggle={() => toggleProjectExpansion(project.id)}
                    />
                  ))}
                </Box>
              </Collapse>
            )}
          </ListItem>
        ))}
      </List>

      {/* Add Project Dialog */}
      <Dialog
        open={addProjectDialogOpen}
        onClose={() => {
          setAddProjectDialogOpen(false);
          setProjectPath('');
          setError('');
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add Project</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <TextField
              fullWidth
              label="Project Path"
              value={projectPath}
              onChange={(e) => setProjectPath(e.target.value)}
              error={!!error}
              helperText={error || 'Enter the full path to your project directory'}
              placeholder="/Users/admin/projects/my-project"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setAddProjectDialogOpen(false);
            setProjectPath('');
            setError('');
          }}>
            Cancel
          </Button>
          <Button onClick={handleAddProject} variant="contained">
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Error Dialog */}
      <Dialog
        open={errorDialogOpen}
        onClose={() => {
          setErrorDialogOpen(false);
          setSelectedProject(null);
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Project Errors</DialogTitle>
        <DialogContent>
          {selectedProject?.errors?.map((error, index) => (
            <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2" color="text.secondary">
                  {new Date(error.timestamp).toLocaleString()}
                </Typography>
                <Chip
                  label={error.status}
                  color={error.status === 'fixed' ? 'success' : error.status === 'fixing' ? 'warning' : 'error'}
                  size="small"
                />
              </Box>
              <Typography variant="body1" sx={{ mt: 1 }}>
                {error.type}: {error.message}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                File: {error.file}:{error.line}
              </Typography>
              {error.fixDescription && (
                <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                  Fix: {error.fixDescription}
                </Typography>
              )}
            </Box>
          ))}
          {(!selectedProject?.errors || selectedProject.errors.length === 0) && (
            <Typography>No errors detected</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setErrorDialogOpen(false);
            setSelectedProject(null);
          }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default ProjectList;
