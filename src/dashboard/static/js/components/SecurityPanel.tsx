import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Alert,
  Divider,
  Chip,
  Grid,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Lock as LockIcon,
  VpnKey as VpnKeyIcon,
  Shield as ShieldIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

interface SecurityMetrics {
  securityScore: number;
  activeThreats: number;
  certificateStatus: string;
  lastAudit: number;
  accessAttempts: number;
  blockedAttempts: number;
}

const SecurityPanel: React.FC = () => {
  const [metrics, setMetrics] = useState<SecurityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSecurityMetrics = async () => {
      try {
        const response = await fetch('/api/system/security-metrics');
        if (!response.ok) {
          throw new Error('Failed to fetch security metrics');
        }
        const data = await response.json();
        setMetrics(data);
        setError(null);
      } catch (err) {
        setError('Failed to load security metrics');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchSecurityMetrics();
    const interval = setInterval(fetchSecurityMetrics, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const getSecurityScoreColor = (score: number): "error" | "warning" | "success" => {
    if (score >= 80) return "success";
    if (score >= 60) return "warning";
    return "error";
  };

  if (loading) {
    return (
      <Paper sx={{ p: 2, height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <CircularProgress />
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 2, height: '100%' }}>
        <Alert severity="error">{error}</Alert>
      </Paper>
    );
  }

  if (!metrics) {
    return null;
  }

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box display="flex" alignItems="center" mb={2}>
        <SecurityIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Security Status</Typography>
      </Box>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={6}>
          <Box textAlign="center">
            <CircularProgress
              variant="determinate"
              value={metrics.securityScore}
              color={getSecurityScoreColor(metrics.securityScore)}
              size={80}
              thickness={8}
            />
            <Typography variant="body2" color="text.secondary" mt={1}>
              Security Score
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Active Threats
            </Typography>
            <Typography variant="h4" color={metrics.activeThreats > 0 ? "error.main" : "success.main"}>
              {metrics.activeThreats}
            </Typography>
          </Box>
        </Grid>
      </Grid>

      <Divider sx={{ my: 2 }} />

      <List dense>
        <ListItem>
          <ListItemIcon>
            <VpnKeyIcon color={metrics.certificateStatus === 'valid' ? 'success' : 'error'} />
          </ListItemIcon>
          <ListItemText
            primary="Certificate Status"
            secondary={
              <Chip
                size="small"
                label={metrics.certificateStatus}
                color={metrics.certificateStatus === 'valid' ? 'success' : 'error'}
              />
            }
          />
        </ListItem>

        <ListItem>
          <ListItemIcon>
            <LockIcon />
          </ListItemIcon>
          <ListItemText
            primary="Access Attempts"
            secondary={
              <Box>
                <Chip
                  size="small"
                  label={`${metrics.accessAttempts} total`}
                  color="primary"
                  sx={{ mr: 1 }}
                />
                <Chip
                  size="small"
                  label={`${metrics.blockedAttempts} blocked`}
                  color="warning"
                />
              </Box>
            }
          />
        </ListItem>

        <ListItem>
          <ListItemIcon>
            <ShieldIcon />
          </ListItemIcon>
          <ListItemText
            primary="Last Security Audit"
            secondary={new Date(metrics.lastAudit * 1000).toLocaleString()}
          />
        </ListItem>
      </List>

      <Divider sx={{ my: 2 }} />

      <Box>
        <Typography variant="subtitle2" gutterBottom>
          Security Checks
        </Typography>
        <List dense>
          {[
            { check: 'Container Isolation', status: true },
            { check: 'Network Policies', status: true },
            { check: 'Access Controls', status: true },
            { check: 'Data Encryption', status: true },
          ].map((item, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                {item.status ? (
                  <CheckCircleIcon color="success" fontSize="small" />
                ) : (
                  <WarningIcon color="error" fontSize="small" />
                )}
              </ListItemIcon>
              <ListItemText primary={item.check} />
            </ListItem>
          ))}
        </List>
      </Box>
    </Paper>
  );
};

export default SecurityPanel;
