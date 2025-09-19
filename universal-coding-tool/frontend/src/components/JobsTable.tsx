import type { Job, JobStatus } from '../api/types';

interface Props {
  jobs: Job[];
  selectedId?: string | null;
  onSelect: (job: Job) => void;
  onRefresh: () => void;
  onFilterStatus: (status: JobStatus | 'all') => void;
}

const statusColors: Record<JobStatus, string> = {
  queued: '#a16207',
  running: '#2563eb',
  succeeded: '#16a34a',
  failed: '#dc2626',
  infra_error: '#7c3aed',
  cancelled: '#6b7280'
};

export default function JobsTable({ jobs, selectedId, onSelect, onRefresh, onFilterStatus }: Props) {
  return (
    <div className="jobs-table">
      <div className="table-header">
        <h2>Jobs</h2>
        <div className="table-actions">
          <select onChange={(event) => onFilterStatus(event.target.value as JobStatus | 'all')}>
            <option value="all">All statuses</option>
            <option value="queued">Queued</option>
            <option value="running">Running</option>
            <option value="succeeded">Succeeded</option>
            <option value="failed">Failed</option>
            <option value="infra_error">Infra error</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <button type="button" onClick={onRefresh}>
            Refresh
          </button>
        </div>
      </div>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Status</th>
              <th>Policy</th>
              <th>Mode</th>
              <th>Started</th>
              <th>Finished</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr
                key={job.id}
                onClick={() => onSelect(job)}
                className={selectedId === job.id ? 'selected' : ''}
              >
                <td>{job.id.slice(0, 8)}</td>
                <td>{job.name}</td>
                <td>
                  <span className="status-pill" style={{ backgroundColor: statusColors[job.status] }}>
                    {job.status.replace('_', ' ')}
                  </span>
                </td>
                <td>{job.policy}</td>
                <td>{job.execution_mode}</td>
                <td>{job.started_at ? new Date(job.started_at).toLocaleString() : '—'}</td>
                <td>{job.finished_at ? new Date(job.finished_at).toLocaleString() : '—'}</td>
              </tr>
            ))}
            {jobs.length === 0 && (
              <tr>
                <td colSpan={7} className="empty">
                  No jobs yet. Submit one below.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
