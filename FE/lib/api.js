// The frontend's only connection to the backend (FastAPI in BE/). No data lives here:
// every function is one HTTP call. The login token is kept in localStorage and sent on each request.

const API = process.env.NEXT_PUBLIC_API_URL
const SESSION_KEY = "skydesk.session"

// ---------------------------------------------------------------- session
let cached = { raw: null, value: null }

function readSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    if (raw !== cached.raw) cached = { raw, value: raw ? JSON.parse(raw) : null }
    return cached.value
  } catch {
    return null
  }
}

/** The logged-in user { id, name, title, role, ... }, or null. Same object until the session changes. */
export function getSession() {
  return readSession()?.user ?? null
}

export function logout() {
  localStorage.removeItem(SESSION_KEY)
}

async function send(path, { method = "GET", body, form } = {}) {
  const headers = {}
  const token = readSession()?.token
  if (token) headers.Authorization = `Bearer ${token}`

  let payload
  if (form) payload = new URLSearchParams(form)
  if (body) {
    headers["Content-Type"] = "application/json"
    payload = JSON.stringify(body)
  }

  const res = await fetch(`${API}${path}`, { method, headers, body: payload })

  if (res.status === 401 && token) {
    // Token expired: back to the login page
    logout()
    window.location.href = "/login"
  }
  if (!res.ok) {
    const error = await res.json().catch(() => ({}))
    throw new Error(typeof error.detail === "string" ? error.detail : `Request failed (${res.status})`)
  }
  return res
}

const request = async (path, options) => (await send(path, options)).json()

// ---------------------------------------------------------------- auth
export async function login(employeeId, password) {
  const { access_token, user } = await request("/auth/login", { method: "POST", form: { username: employeeId, password } })
  localStorage.setItem(SESSION_KEY, JSON.stringify({ token: access_token, user }))
  return user
}

// ---------------------------------------------------------------- business values (teams, statuses, ...)
let meta = null
/** Fetched once from the backend (BE/app/core/domain.py) and shared by every page. */
export const getMeta = () => (meta ??= request("/meta").catch((e) => ((meta = null), Promise.reject(e))))

// ---------------------------------------------------------------- agent chat (employee)

/** Streams the agent's steps: calls onEvent({ type, ... }) for each server-sent event as it arrives. */
export async function streamMessage(message, threadId, onEvent) {
  const res = await send("/agent/chat/stream", { method: "POST", body: { message, thread_id: threadId } })
  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader()
  let buffer = ""
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += value
    const events = buffer.split("\n\n")
    buffer = events.pop()
    for (const event of events) {
      const data = event.split("\n").find((line) => line.startsWith("data:"))
      if (data) onEvent(JSON.parse(data.slice(5)))
    }
  }
}
export const listConversations = () => request("/agent/conversations")
export const getConversation = (threadId) => request(`/agent/conversations/${threadId}`)

// ---------------------------------------------------------------- tickets
export const listMyTickets = () => request("/tickets/mine")
export const listTickets = () => request("/tickets")
export const getTicket = (id) => request(`/tickets/${id}`)
export const updateTicket = (id, patch) => request(`/tickets/${id}`, { method: "PATCH", body: patch })

// ---------------------------------------------------------------- approvals (manager / IAM)
export const listApprovals = () => request("/approvals")
export const decideApproval = (id, approve, comment) => request(`/approvals/${id}/decision`, { method: "POST", body: { approve, comment } })
