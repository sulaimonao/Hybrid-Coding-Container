# UI Guide

## Sign-in screen

- Enter the admin email/password configured in `.env`.
- Sessions persist in an HTTP-only cookie until the browser is closed or the
  backend secret is rotated.

## Dashboard layout

- **Header** – Displays the product name and how many policies were loaded.
- **Jobs table** – Lists jobs with ID, name, status, policy, mode and timestamps.
  - Use the status filter dropdown to focus on a specific lifecycle stage.
  - Click **Refresh** to trigger an immediate API call.
- **Submit job panel** – Located on the right. Fields:
  - Name: arbitrary label for the job.
  - Language: Python/Node/Rust (controls which Docker image is used).
  - Policy: selects container vs. VM profile.
  - Command: shell command executed inside the container/VM.
  - Source code: inline editor; creates `main.py`, `index.js` or `main.rs`.

## Job detail view

Click a job row to open the detail panel:

- **Metadata** – Shows policy, execution mode, image, timestamps and exit code.
- **Status pill** – Color-coded (blue running, green success, red failure).
- **Logs** – Live streamed via Server Sent Events. Autoscrolls as new data
  arrives. If no logs, displays a placeholder message.
- **Artifacts** – List of produced files with download links (opens new tab or
  saves locally).
- **Error banner** – Appears when the job enters `infra_error` state (e.g.
  Docker daemon unavailable).

## Log stream tips

- Logs arrive in near real time for container jobs. VM jobs may lag because the
  host waits for the guest to produce output.
- Close the detail view or navigate away to cancel the EventSource connection.

## Accessibility notes

- All form fields have labels.
- Keyboard navigation: use `Tab` to switch between fields and the job table.
- Color palette passes WCAG AA contrast requirements for body text and status
  pills.

## Common warnings

- **CORS errors** – Ensure the backend is running on `localhost:8000` and that
  you accessed the UI via `localhost:5173`.
- **Session expired** – Refresh the page and sign in again. Happens after secret
  rotation or backend restart.

## Dark mode

Dark mode is not provided out-of-the-box. To add it, extend `styles.css` with a
`[data-theme="dark"]` section and toggle via a simple button in `App.tsx`.
