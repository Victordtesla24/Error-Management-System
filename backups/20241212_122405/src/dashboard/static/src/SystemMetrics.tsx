import React from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import { blue } from '@mui/material/colors';

interface SystemMetricsProps {
  cpuUsage: number;
  memoryUsage: number;
  projectCount: number;
  agentCount: number;
}

const SystemMetrics: React.FC<SystemMetricsProps> = ({
  cpuUsage,
  memoryUsage,
  projectCount,
  agentCount,
}) => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
            <Typography variant="h6" gutterBottom>
              Resource Usage
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                  <CircularProgress
                    variant="determinate"
                    value={cpuUsage}
                    size={100}
                    sx={{ color: blue[500] }}
                  />
                  <Box
                    sx={{
                      top: 0,
                      left: 0,
                      bottom: 0,
                      right: 0,
                      position: 'absolute',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography variant="caption" component="div" color="text.secondary">
                      {`${Math.round(cpuUsage)}%`}
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body1" align="center" sx={{ mt: 1 }}>
                  CPU Usage
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                  <CircularProgress
                    variant="determinate"
                    value={memoryUsage}
                    size={100}
                    sx={{ color: blue[300] }}
                  />
                  <Box
                    sx={{
                      top: 0,
                      left: 0,
                      bottom: 0,
                      right: 0,
                      position: 'absolute',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography variant="caption" component="div" color="text.secondary">
                      {`${Math.round(memoryUsage)}%`}
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body1" align="center" sx={{ mt: 1 }}>
                  Memory Usage
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="h6">Projects</Typography>
                <Typography variant="h3" sx={{ mt: 2, color: blue[500] }}>
                  {projectCount}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={6}>
              <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="h6">Agents</Typography>
                <Typography variant="h3" sx={{ mt: 2, color: blue[300] }}>
                  {agentCount}
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SystemMetrics;
