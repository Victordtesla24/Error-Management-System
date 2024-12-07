import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Divider,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Delete as DeleteIcon,
  Backup as BackupIcon,
  RestartAlt as RestartIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

interface SystemStatus {
  projects: number;
  agents: number;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  uptime: number;
}

interface ControlPanelProps {
  systemStatus: SystemStatus | null;
  onStart: () => Promise<void>;
  onStop: () => Promise<void>;
}

const ControlPanel: React.FC<ControlPanelProps> = ({
  systemStatus,
  onStart,
  onStop,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmDialog, setConfirmDialog] = useState(false);
  const [settingsDialog, setSettingsDialog] = useState(false);
  const [settings, setSettings] = useState({
    autoRestart: true,
    debugMode: false,
    maxAgents: 5,
    autoFix: true,
  });

  const handleAction = async (action: () => Promise<void>) => {
    setLoading(true);
    setError(null);
    try {
      await action();
    } catch (err) {
      setError('Failed to perform action');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSystemRestart = async () => {
    setConfirmDialog(false);
    await handleAction(async () => {
      await onStop();
      await new Promise(resolve => setTimeout(resolve, 1000));
      await onStart();
    });
  };

  const handleBackup = async () => {
    await handleAction(async () => {
      const response = await fetch('/api/system/backup', { method: 'POST' });
      if (!response.ok) throw new Error('Backup failed');
    });
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">System Controls</Typography>
        <Box>
          <IconButton onClick={() => setSettingsDialog(true)}>
            <SettingsIcon />
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={2}>
        {/* System Status */}
        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              System Status
            </Typography>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Active Projects: {systemStatus?.projects || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Running Agents: {systemStatus?.agents || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Uptime: {systemStatus ? formatUptime(systemStatus.uptime) : '-'}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={1}>
            <Grid item>
              <Button
                variant="contained"
                color="success"
                startIcon={<StartIcon />}
                onClick={() => handleAction(onStart)}
                disabled={loading}
              >
                Start
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="contained"
                color="error"
                startIcon={<StopIcon />}
                onClick={() => handleAction(onStop)}
                disabled={loading}
              >
                Stop
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="contained"
                color="warning"
                startIcon={<RestartIcon />}
                onClick={() => setConfirmDialog(true)}
                disabled={loading}
              >
                Restart
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="contained"
                startIcon={<BackupIcon />}
                onClick={handleBackup}
                disabled={loading}
              >
                Backup
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Grid>

      {/* Confirmation Dialog */}
      <Dialog open={confirmDialog} onClose={() => setConfirmDialog(false)}>
        <DialogTitle>
          <WarningIcon color="warning" sx={{ mr: 1 }} />
          Confirm Restart
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to restart the system? All agents will be stopped and restarted.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSystemRestart}
            variant="contained"
            color="warning"
            disabled={loading}
          >
            Restart
          </Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog open={settingsDialog} onClose={() => setSettingsDialog(false)}>
        <DialogTitle>System Settings</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoRestart}
                    onChange={(e) => setSettings({ ...settings, autoRestart: e.target.checked })}
                  />
                }
                label="Auto-restart on failure"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.debugMode}
                    onChange={(e) => setSettings({ ...settings, debugMode: e.target.checked })}
                  />
                }
                label="Debug mode"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoFix}
                    onChange={(e) => setSettings({ ...settings, autoFix: e.target.checked })}
                  />
                }
                label="Automatic error fixing"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsDialog(false)}>Cancel</Button>
          <Button
            onClick={() => setSettingsDialog(false)}
            variant="contained"
            color="primary"
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default ControlPanel;
