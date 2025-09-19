import type { Artifact } from '../api/types';

interface Props {
  artifacts: Artifact[];
}

export default function ArtifactList({ artifacts }: Props) {
  return (
    <div className="artifact-list">
      <h3>Artifacts</h3>
      {artifacts.length === 0 ? (
        <p>No artifacts yet.</p>
      ) : (
        <ul>
          {artifacts.map((artifact) => (
            <li key={artifact.name}>
              <a href={artifact.download_url} download>
                {artifact.name}
              </a>{' '}
              <span>({Math.round(artifact.size / 1024)} KB)</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
