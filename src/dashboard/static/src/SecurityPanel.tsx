import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Grid from '@mui/material/Grid';
import Chip from '@mui/material/Chip';
import {
  Security,
  Lock,
  Shield,
  Warning,
  CheckCircle,
} from '@mui/icons-material';

interface SecurityMetrics {
  securityScore: number;
  activeThreats: number;
  certificateStatus: 'valid' | 'expired' | 'warning';
  lastScan: string;
}

const SecurityPanel: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState<SecurityMetrics>({
    securityScore: 0,
    activeThreats: 0,
    certificateStatus: 'valid',
    lastScan: new Date().toISOString(),
  });

  useEffect(() => {
    fetchSecurityMetrics();
    const interval = setInterval(fetchSecurityMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSecurityMetrics = async () => {
    try {
      const response = await fetch('/api/system/security-metrics');
      if (!response.ok) {
        throw new Error('Failed to fetch security metrics');
      }
      const data = await response.json();
      setMetrics(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching security metrics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 2, height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <CircularProgress />
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Security Status
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Security sx={{ mr: 1 }} />
            <Typography variant="subtitle1">
              Security Score: {metrics.securityScore}%
            </Typography>
          </Box>
        </Grid>

        {metrics.activeThreats > 0 && (
          <Grid item xs={12}>
            <Alert severity="warning" icon={<Warning />}>
              {metrics.activeThreats} active threat{metrics.activeThreats !== 1 ? 's' : ''} detected
            </Alert>
          </Grid>
        )}

        <Grid item xs={12}>
          <List>
            <ListItem>
              <ListItemIcon>
                <Lock />
              </ListItemIcon>
              <ListItemText primary="Access Control" secondary="Enabled" />
              <Chip label="Active" color="success" size="small" />
            </ListItem>

            <ListItem>
              <ListItemIcon>
                <Shield />
              </ListItemIcon>
              <ListItemText primary="Certificate Status" secondary={metrics.certificateStatus} />
              <Chip
                label={metrics.certificateStatus}
                color={metrics.certificateStatus === 'valid' ? 'success' : 'warning'}
                size="small"
              />
            </ListItem>

            <ListItem>
              <ListItemIcon>
                <CheckCircle />
              </ListItemIcon>
              <ListItemText
                primary="Last Security Scan"
                secondary={new Date(metrics.lastScan).toLocaleString()}
              />
            </ListItem>
          </List>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default SecurityPanel;
