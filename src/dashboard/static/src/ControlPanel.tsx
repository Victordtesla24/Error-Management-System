import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import { PlayArrow, Stop, Settings } from '@mui/icons-material';

export interface ControlPanelProps {
  systemStatus: 'running' | 'stopped';
  onStart: () => void;
  onStop: () => void;
}

interface SystemSettings {
  autoRestart: boolean;
  debugMode: boolean;
  autoFix: boolean;
}

const ControlPanel: React.FC<ControlPanelProps> = ({
  systemStatus,
  onStart,
  onStop,
}) => {
  const [settings, setSettings] = useState<SystemSettings>({
    autoRestart: true,
    debugMode: false,
    autoFix: true,
  });

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Control Panel
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<PlayArrow />}
              onClick={onStart}
              disabled={systemStatus === 'running'}
            >
              Start System
            </Button>
            <Button
              variant="contained"
              color="error"
              startIcon={<Stop />}
              onClick={onStop}
              disabled={systemStatus === 'stopped'}
            >
              Stop System
            </Button>
          </Box>
        </Grid>
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom>
            System Settings
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.autoRestart}
                  onChange={(e) => setSettings({ ...settings, autoRestart: e.target.checked })}
                  color="primary"
                />
              }
              label="Auto Restart on Failure"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={settings.debugMode}
                  onChange={(e) => setSettings({ ...settings, debugMode: e.target.checked })}
                  color="primary"
                />
              }
              label="Debug Mode"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={settings.autoFix}
                  onChange={(e) => setSettings({ ...settings, autoFix: e.target.checked })}
                  color="primary"
                />
              }
              label="Auto Fix Issues"
            />
          </Box>
        </Grid>
        <Grid item xs={12}>
          <Typography variant="body2" color="text.secondary">
            System Status: {systemStatus.charAt(0).toUpperCase() + systemStatus.slice(1)}
          </Typography>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ControlPanel;
