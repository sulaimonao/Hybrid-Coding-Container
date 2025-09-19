import { useEffect, useRef, useState } from 'react';
import { streamLogs } from '../api/client';

interface Props {
  jobId: string;
}

export default function LogStream({ jobId }: Props) {
  const [logs, setLogs] = useState<string>('');
  const logRef = useRef<HTMLPreElement | null>(null);

  useEffect(() => {
    setLogs('');
    const source = streamLogs(jobId, (chunk) => {
      setLogs((prev) => `${prev}${chunk}\n`);
    });
    return () => {
      source.close();
    };
  }, [jobId]);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="log-stream">
      <h3>Logs</h3>
      <pre ref={logRef}>{logs || 'Logs will appear here when the job starts.'}</pre>
    </div>
  );
}
