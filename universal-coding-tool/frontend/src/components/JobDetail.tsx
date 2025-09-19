import { useEffect, useState } from 'react';
import { getJob, listArtifacts } from '../api/client';
import type { Artifact, Job } from '../api/types';
import ArtifactList from './ArtifactList';
import LogStream from './LogStream';

interface Props {
  job: Job;
}

export default function JobDetail({ job }: Props) {
  const [detail, setDetail] = useState<Job>(job);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      const fresh = await getJob(job.id);
      if (mounted) {
        setDetail(fresh);
      }
      const artifactList = await listArtifacts(job.id);
      if (mounted) {
        setArtifacts(artifactList);
      }
    };
    load();
    const timer = setInterval(load, 5000);
    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, [job.id]);

  return (
    <div className="job-detail">
      <header>
        <h2>{detail.name}</h2>
        <span className={`status-pill status-${detail.status}`}>{detail.status.replace('_', ' ')}</span>
      </header>
      <section className="meta">
        <div>
          <strong>Policy:</strong> {detail.policy}
        </div>
        <div>
          <strong>Execution mode:</strong> {detail.execution_mode}
        </div>
        <div>
          <strong>Image:</strong> {detail.image}
        </div>
        <div>
          <strong>Started:</strong>{' '}
          {detail.started_at ? new Date(detail.started_at).toLocaleString() : '—'}
        </div>
        <div>
          <strong>Finished:</strong>{' '}
          {detail.finished_at ? new Date(detail.finished_at).toLocaleString() : '—'}
        </div>
        <div>
          <strong>Exit code:</strong> {detail.exit_code ?? '—'}
        </div>
        {detail.error && (
          <div className="error-banner">Infrastructure error: {detail.error}</div>
        )}
      </section>
      <LogStream jobId={detail.id} />
      <ArtifactList artifacts={artifacts} />
    </div>
  );
}
