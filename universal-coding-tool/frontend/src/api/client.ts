import axios from 'axios';
import type { Artifact, Job, JobCreateRequest, PolicyMap } from './types';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true
});

export async function login(email: string, password: string) {
  await api.post('/auth/login', { email, password });
}

export async function logout() {
  await api.post('/auth/logout');
}

export async function listJobs(): Promise<Job[]> {
  const { data } = await api.get<Job[]>('/jobs');
  return data;
}

export async function getJob(id: string): Promise<Job> {
  const { data } = await api.get<Job>(`/jobs/${id}`);
  return data;
}

export async function createJob(payload: JobCreateRequest): Promise<Job> {
  const { data } = await api.post<Job>('/jobs', payload);
  return data;
}

export async function listPolicies(): Promise<PolicyMap> {
  const { data } = await api.get<PolicyMap>('/policies');
  return data;
}

export async function listArtifacts(jobId: string): Promise<Artifact[]> {
  const { data } = await api.get<Artifact[]>(`/jobs/${jobId}/artifacts`);
  return data.map((item) => ({
    ...item,
    download_url: `${API_BASE}/jobs/${jobId}/artifacts/${item.name}`
  }));
}

export function streamLogs(jobId: string, onMessage: (log: string) => void) {
  const source = new EventSource(`${API_BASE}/jobs/${jobId}/logs/stream`, {
    withCredentials: true
  });
  source.onmessage = (event) => {
    onMessage(event.data as string);
  };
  return source;
}
