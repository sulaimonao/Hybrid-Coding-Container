export type JobStatus =
  | 'queued'
  | 'running'
  | 'succeeded'
  | 'failed'
  | 'infra_error'
  | 'cancelled';

export interface Job {
  id: string;
  name: string;
  status: JobStatus;
  started_at?: string | null;
  finished_at?: string | null;
  policy: string;
  execution_mode: 'container' | 'dedicated-vm';
  image: string;
  limits: Record<string, unknown>;
  exit_code?: number | null;
  error?: string | null;
}

export interface Artifact {
  name: string;
  size: number;
  download_url?: string;
}

export interface JobCreateRequest {
  name: string;
  lang: 'python' | 'node' | 'rust';
  files: { path: string; content: string }[];
  cmd: string;
  policy: 'safe-default' | 'research' | 'experimental' | 'dedicated-vm';
}

export type PolicyMap = Record<string, Record<string, unknown>>;
