// React and DOM types
declare namespace React {
  interface FunctionComponent<P = {}> {
    (props: P, context?: any): ReactElement<any, any> | null;
    displayName?: string;
  }
  type FC<P = {}> = FunctionComponent<P>;
}

// Basic DOM types
interface Window {
  process: {
    env: {
      NODE_ENV: string;
      PUBLIC_URL: string;
    }
  }
}

// Project-specific types
interface SystemStatus {
  projects: number;
  agents: number;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  uptime: number;
}

interface Project {
  id: string;
  path: string;
  active: boolean;
  error_count: number;
  last_scan: number;
  agents: string[];
}

interface Agent {
  id: string;
  project_id: string | null;
  cpu_usage: number;
  memory_usage: number;
  status: string;
  last_active: number;
}

interface SecurityMetrics {
  securityScore: number;
  activeThreats: number;
  certificateStatus: string;
  lastAudit: number;
  accessAttempts: number;
  blockedAttempts: number;
}

// MUI types
declare module '@mui/material/styles' {
  interface Theme {
    status: {
      danger: string;
    };
    palette: {
      primary: {
        main: string;
        light: string;
        dark: string;
      };
      secondary: {
        main: string;
        light: string;
        dark: string;
      };
      error: {
        main: string;
        light: string;
        dark: string;
      };
      warning: {
        main: string;
        light: string;
        dark: string;
      };
      success: {
        main: string;
        light: string;
        dark: string;
      };
      text: {
        primary: string;
        secondary: string;
        disabled: string;
      };
      background: {
        default: string;
        paper: string;
      };
    };
  }
  interface ThemeOptions {
    status?: {
      danger?: string;
    };
    palette?: {
      primary?: {
        main?: string;
        light?: string;
        dark?: string;
      };
      secondary?: {
        main?: string;
        light?: string;
        dark?: string;
      };
      error?: {
        main?: string;
        light?: string;
        dark?: string;
      };
      warning?: {
        main?: string;
        light?: string;
        dark?: string;
      };
      success?: {
        main?: string;
        light?: string;
        dark?: string;
      };
      text?: {
        primary?: string;
        secondary?: string;
        disabled?: string;
      };
      background?: {
        default?: string;
        paper?: string;
      };
    };
  }
}

declare module '@mui/material/styles/createPalette' {
  interface Palette {
    neutral: {
      main: string;
      contrastText: string;
    };
  }
  interface PaletteOptions {
    neutral?: {
      main?: string;
      contrastText?: string;
    };
  }
}

// MUI component props
declare module '@mui/material' {
  interface ChipProps {
    size?: 'small' | 'medium';
    label?: React.ReactNode;
    color?: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
    sx?: any;
  }

  interface CircularProgressProps {
    variant?: 'determinate' | 'indeterminate';
    value?: number;
    color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' | 'inherit';
    size?: number;
    thickness?: number;
    sx?: any;
  }

  interface SvgIconProps {
    color?: 'inherit' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
    fontSize?: 'inherit' | 'large' | 'medium' | 'small';
    sx?: any;
  }
}

// Recharts types
declare module 'recharts' {
  export interface LineProps {
    type?: 'basis' | 'basisClosed' | 'basisOpen' | 'linear' | 'linearClosed' | 'natural' | 'monotoneX' | 'monotoneY' | 'monotone' | 'step' | 'stepBefore' | 'stepAfter';
    dataKey: string;
    stroke?: string;
    name?: string;
  }
  
  export const LineChart: React.FC<{
    data: any[];
    children?: React.ReactNode;
  }>;
  
  export const Line: React.FC<LineProps>;
  
  export const XAxis: React.FC<{
    dataKey: string;
  }>;
  
  export const YAxis: React.FC;
  
  export const CartesianGrid: React.FC<{
    strokeDasharray: string;
  }>;
  
  export const Tooltip: React.FC;
  
  export const ResponsiveContainer: React.FC<{
    width: string | number;
    height: number | string;
  }>;
}
