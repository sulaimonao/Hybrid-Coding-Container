import { useEffect, useMemo, useState } from 'react';
import {
  createJob,
  listJobs,
  listPolicies
} from './api/client';
import type { Job, JobCreateRequest, JobStatus, PolicyMap } from './api/types';
import JobDetail from './components/JobDetail';
import JobsTable from './components/JobsTable';
import Login from './components/Login';

const DEFAULT_CODE = `print("Hello from sandbox")`;

export default function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [statusFilter, setStatusFilter] = useState<JobStatus | 'all'>('all');
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [policies, setPolicies] = useState<PolicyMap>({});
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [code, setCode] = useState(DEFAULT_CODE);
  const [jobName, setJobName] = useState('hello_python');
  const [command, setCommand] = useState('python main.py');
  const [language, setLanguage] = useState<'python' | 'node' | 'rust'>('python');
  const [policy, setPolicy] = useState<'safe-default' | 'research' | 'experimental' | 'dedicated-vm'>('safe-default');

  const filteredJobs = useMemo(() => {
    if (statusFilter === 'all') {
      return jobs;
    }
    return jobs.filter((job) => job.status === statusFilter);
  }, [jobs, statusFilter]);

  const refreshJobs = async () => {
    try {
      const jobList = await listJobs();
      setJobs(jobList);
      setSelectedJob((current) => current ?? (jobList.length ? jobList[0] : null));
    } catch (err) {
      setError('Failed to load jobs.');
    }
  };

  useEffect(() => {
    if (!authenticated) {
      return;
    }
    refreshJobs();
    listPolicies().then(setPolicies).catch(() => setPolicies({}));
    const timer = setInterval(refreshJobs, 5000);
    return () => clearInterval(timer);
  }, [authenticated]);

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const payload: JobCreateRequest = {
        name: jobName,
        lang: language,
        files: [{ path: language === 'python' ? 'main.py' : language === 'node' ? 'index.js' : 'main.rs', content: code }],
        cmd: command,
        policy
      };
      const job = await createJob(payload);
      setJobs((prev) => [job, ...prev]);
      setSelectedJob(job);
    } catch (err) {
      setError('Job submission failed.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!authenticated) {
    return <Login onSuccess={() => setAuthenticated(true)} />;
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Universal Coding Tool</h1>
        <div className="policy-info">{Object.keys(policies).length} policies loaded</div>
      </header>
      <main>
        <section className="content">
          <JobsTable
            jobs={filteredJobs}
            selectedId={selectedJob?.id}
            onSelect={setSelectedJob}
            onRefresh={refreshJobs}
            onFilterStatus={(value) => setStatusFilter(value)}
          />
          {selectedJob ? <JobDetail job={selectedJob} /> : <p>Select a job to view details.</p>}
        </section>
        <aside className="sidebar">
          <div className="card">
            <h2>Submit job</h2>
            <label>
              Name
              <input value={jobName} onChange={(event) => setJobName(event.target.value)} />
            </label>
            <label>
              Language
              <select value={language} onChange={(event) => setLanguage(event.target.value as typeof language)}>
                <option value="python">Python</option>
                <option value="node">Node</option>
                <option value="rust">Rust</option>
              </select>
            </label>
            <label>
              Policy
              <select value={policy} onChange={(event) => setPolicy(event.target.value as typeof policy)}>
                {Object.keys(policies).length === 0 ? (
                  <option value="safe-default">safe-default</option>
                ) : (
                  Object.keys(policies).map((key) => (
                    <option key={key} value={key}>
                      {key}
                    </option>
                  ))
                )}
              </select>
            </label>
            <label>
              Command
              <input value={command} onChange={(event) => setCommand(event.target.value)} />
            </label>
            <label>
              Source code
              <textarea value={code} onChange={(event) => setCode(event.target.value)} rows={10} />
            </label>
            <button type="button" onClick={handleSubmit} disabled={submitting}>
              {submitting ? 'Submitting…' : 'Run job'}
            </button>
            {error && <p className="error">{error}</p>}
          </div>
        </aside>
      </main>
    </div>
  );
}
