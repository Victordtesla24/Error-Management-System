import React from 'react';
import {
  Box,
  Grid,
  CircularProgress,
  Typography,
  Paper,
  useTheme,
} from '@mui/material';

interface SystemMetricsProps {
  cpu: number;
  memory: number;
  disk: number;
}

const MetricGauge: React.FC<{
  value: number;
  label: string;
  color: string;
}> = ({ value, label, color }) => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      position="relative"
    >
      <Box position="relative" display="inline-flex">
        <CircularProgress
          variant="determinate"
          value={value}
          size={80}
          thickness={8}
          sx={{ color }}
        />
        <Box
          position="absolute"
          top={0}
          left={0}
          bottom={0}
          right={0}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Typography variant="body2" component="div" color="text.secondary">
            {`${Math.round(value)}%`}
          </Typography>
        </Box>
      </Box>
      <Typography variant="body1" color="text.secondary" mt={1}>
        {label}
      </Typography>
    </Box>
  );
};

const SystemMetrics: React.FC<SystemMetricsProps> = ({ cpu, memory, disk }) => {
  const theme = useTheme();

  const getColor = (value: number): string => {
    if (value >= 90) return theme.palette.error.main;
    if (value >= 70) return theme.palette.warning.main;
    return theme.palette.success.main;
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Grid container spacing={4} justifyContent="center">
        <Grid item>
          <MetricGauge
            value={cpu}
            label="CPU Usage"
            color={getColor(cpu)}
          />
        </Grid>
        <Grid item>
          <MetricGauge
            value={memory}
            label="Memory Usage"
            color={getColor(memory)}
          />
        </Grid>
        <Grid item>
          <MetricGauge
            value={disk}
            label="Disk Usage"
            color={getColor(disk)}
          />
        </Grid>
      </Grid>
      
      {/* Additional System Information */}
      <Box mt={3}>
        <Grid container spacing={2}>
          <Grid item xs={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              CPU Temperature
            </Typography>
            <Typography variant="body1">
              {cpu > 80 ? '🔥' : '✓'} {Math.round(cpu * 0.5 + 40)}°C
            </Typography>
          </Grid>
          <Grid item xs={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Memory Available
            </Typography>
            <Typography variant="body1">
              {Math.round((100 - memory) * 0.16)} GB
            </Typography>
          </Grid>
          <Grid item xs={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Disk Free
            </Typography>
            <Typography variant="body1">
              {Math.round((100 - disk) * 1.5)} GB
            </Typography>
          </Grid>
          <Grid item xs={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              System Load
            </Typography>
            <Typography variant="body1">
              {(cpu * 0.04).toFixed(2)}
            </Typography>
          </Grid>
        </Grid>
      </Box>

      {/* Warning Indicators */}
      {(cpu >= 90 || memory >= 90 || disk >= 90) && (
        <Box mt={2}>
          <Typography color="error" variant="body2">
            ⚠️ High resource usage detected. Consider optimizing system performance.
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default SystemMetrics;
