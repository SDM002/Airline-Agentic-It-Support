# FE: SkyDesk AI frontend

A simple Next.js UI for the SkyDesk AI backend. **There is no business logic and no data in the frontend.** Every screen calls the FastAPI backend in `BE/` and shows what comes back.
For the overall picture, see the [root README](../README.md); for the API, see [BE/README.md](../BE/README.md).

## 1. Setup and run

Node 20+. The backend must be running at the address in `NEXT_PUBLIC_API_URL`.

```bash
cd FE
npm install
cp .env.example .env.local      # set NEXT_PUBLIC_API_URL to the backend address
npm run dev                     # prints the local address; it must be in the backend's CORS_ORIGINS
```

| Command | Purpose |
|---|---|
| `npm run dev` | Development server (Turbopack) |
| `npm run build` / `npm start` | Production build / serve it |
| `npm run lint` | ESLint |

> Do not run `npm audit fix --force`: it downgrades `shadcn` to 1.x and breaks the build (`Can't resolve 'shadcn/tailwind.css'`). If that happens, run `npm install shadcn@^4.23.0`.

**Stack:**
- Next.js 16 (App Router, JavaScript), React 19
- Tailwind CSS 4, shadcn/ui components, lucide-react icons
- sonner for toasts, react-markdown for the agent's replies

## 2. Folder layout

```
lib/api.js                 the ONLY connection to the backend: login, session, every API call, SSE stream reader
lib/utils.js               cn() class helper
components/
  shell.jsx                header, navigation per role, client-side route guard, HOME page per role
  agent-steps.jsx          live step list while the agent works + "Issue analysis" / "Agent steps" panels
  agent-trace.jsx          the agent's tool calls for a ticket (ticket detail page)
  approval-card.jsx        approve / reject with a comment
  ticket-actions.jsx       engineer controls: assign L1/L2, change status, resolve / close
  ticket-badges.jsx        priority, status, SLA countdown
  ui/                      shadcn/ui building blocks
app/
  page.jsx                 redirects to /login
  login/page.jsx           employee ID + password
  employee/chat            chat with the agent (streaming) + chat history
  employee/my-tickets      the employee's own tickets
  support/dashboard        IT overview: counters, closest to SLA breach, awaiting approval, load per team
  support/tickets          all tickets with filters
  support/tickets/[id]     ticket detail: Details · Knowledge · Comments · Audit tabs + agent trace
  support/approvals        pending access requests (managers and IT)
```

## 3. Pages per role

The user's role comes from the backend at login.

| Role | Home | Pages |
|---|---|---|
| `employee` | `/employee/chat` | Chat, My tickets |
| `manager` | `/support/approvals` | Approvals (their team only) |
| `it_support` | `/support/dashboard` | Dashboard, Tickets, Ticket detail, Approvals |

`components/shell.jsx` is a **client-side guard**. With no session it redirects to `/login`; on a page outside the role's navigation, it redirects to that role's home page.
This is only for the user experience. **Real security is in the backend**, which checks the JWT and role on every call. Calling the API directly with the wrong role returns 403.

The team and status lists in the filters and dropdowns come from `GET /meta`, so they are never copied into the frontend.

## 4. Login and the JWT in the browser

```
Login form ──POST /auth/login (form: username, password)──► backend checks Argon2 hash
           ◄── { access_token (JWT), user {id, name, role, ...} }
localStorage["skydesk.session"] = { token, user }
every later call:  Authorization: Bearer <token>
401 from the backend (expired or invalid token) → session removed → back to /login
Sign out → session removed
```

- `lib/api.js` → `send()` adds the `Authorization` header to every request and turns backend errors (`detail`) into readable messages.
- The token expires after `JWT_EXPIRE_MINUTES` (set in BE/.env). The frontend never decodes it: it only stores it and sends it back.
- The user object is kept beside the token, so the header can show the name and role without another call.

## 5. How the chat streams from the backend

The chat page (`app/employee/chat/page.jsx`) uses `streamMessage()` in `lib/api.js`:

1. `POST /agent/chat/stream` with `{ message, thread_id }` and the Bearer token. `thread_id` is empty for a new chat; the backend creates one and sends it back in the first `start` event.
2. The response is **server-sent events**. They are read with `fetch` plus `res.body.pipeThrough(new TextDecoderStream()).getReader()`, because the browser's `EventSource` cannot send a POST body or an `Authorization` header.
3. The text is split on blank lines (`\n\n`). Each event's `data:` line is parsed as JSON and passed to `onEvent`.
4. `applyEvent()` builds the agent's reply step by step:

| Event | What the screen does |
|---|---|
| `start` | Stores the chat's `thread_id`, so the next message continues the same chat (memory) |
| `guardrail` | Adds a "Guardrail" step (for example "email redacted") |
| `classified` | Adds "Classifying issue" with category · priority · team · airport, and fills the **Issue analysis** panel |
| `knowledge` | Adds "Searching knowledge base · Pinecone" with each SOP and its rerank score: the RAG step, always before any MongoDB step |
| `tool_call` | Adds a step with a spinner, for example "Checking similar tickets · MongoDB" |
| `tool_result` | Ticks that step and shows a one-line result ("<n> found: <n> open", "<ticket ID> · SLA <hours> h") |
| `approval` | Shows the **Waiting for approval** banner with the ticket ID |
| `answer` | Shows the agent's reply (Markdown) |
| `error` | Shows the message, for example "LLM busy" |

While the agent works, `LiveSteps` shows each step with its live state. Afterwards, `StepPanels` shows two collapsible panels:
- **Issue analysis:** the classification and its reason;
- **Agent steps:** every step with its arguments and full result, including the retrieved SOP text.

Chat history (left column) comes from `GET /agent/conversations`. Opening an old chat calls `GET /agent/conversations/{id}`, which returns the messages saved in the LangGraph checkpoint.

## 6. Approvals: how a human resumes the agent

1. The employee's access request pauses the agent. The chat shows **Waiting for approval**, and the ticket shows `awaiting-approval` in My tickets.
2. The manager (or an IAM engineer) opens **Approvals** (`GET /approvals`). Each card shows the requester, the requested access, the agent's reason and the ticket.
3. **Approve** or **Reject** (with an optional comment) calls `POST /approvals/{id}/decision`. The backend checks who may decide, updates the ticket, and resumes the paused agent.
4. The employee sees the ticket as `resolved` or `closed` in My tickets, and the agent's follow-up message in the chat.

If the user may not decide (for example a non-IAM engineer), the backend returns 403 and the card shows its message.

## 7. Ticket detail (IT support)

`GET /tickets/{id}` returns everything for one ticket:

- **Details:** priority, status, SLA countdown, requester, team, assignee; engineer controls (`PATCH /tickets/{id}`).
- **Knowledge:** the SOPs from Pinecone for this ticket (with rerank scores), and similar tickets from MongoDB.
- **Comments:** comments by the agent, engineers and approvers.
- **Audit:** every change, with who made it (the agent or the engineer's name) and when.
- **Agent trace:** for tickets the agent created, what it did in the chat. `search_knowledge (RAG)` first, then each tool call with its arguments.

## 8. Configuration

| File | Key | Value |
|---|---|---|
| `.env.local` (gitignored; copy from `.env.example`) | `NEXT_PUBLIC_API_URL` | the backend address |
| `next.config.mjs` | `experimental.instantInsights.validationLevel` | `"manual-warning"` (quiets Next.js 16 dev instant-navigation warnings) |

The backend must allow the frontend's origin in `CORS_ORIGINS` (BE/.env).
