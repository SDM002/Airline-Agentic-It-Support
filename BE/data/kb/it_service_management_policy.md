# Saffron Air — IT Service Management, Access & Escalation Policy

Document ID: IT-POL-002 · Version 2.4 · Owner: Head of IT Operations · Classification: Internal
Saffron Air is a fictional airline used for this proof of concept. All policies are synthetic.

This policy defines how IT issues are prioritised, how fast they must be handled, when they are escalated, and how access to systems is approved.
It applies to every employee, to IT engineers, and to the SkyDesk AI helpdesk agent.

---

## 1. Purpose and scope

Airline operations depend on IT: check-in, boarding, baggage, crew scheduling, load control and finance all stop when systems fail.
The goals of this policy are:

- Every IT issue is recorded as a ticket, with a clear owner and priority.
- Issues that affect passengers or flights are handled first.
- Access to systems is only granted after approval by an authorised person.
- Every action on a ticket is traceable in the audit log.

Scope: all Saffron Air employees at all stations (BLR, DEL, BOM, HYD, MAA, CCU) and corporate offices.

---

## 2. Support teams and ownership

| Team | Owns |
|---|---|
| Application Support | Check-in application, crew scheduling application, ERP and other business applications |
| Network Support | Airport wired network (MPLS), staff Wi-Fi, handheld Wi-Fi, VPN |
| Hardware Support | Boarding pass and bag tag printers, barcode scanners, PCs, office printers |
| IT Support | Email, Microsoft 365, Teams, general service desk questions |
| Identity & Access Management (IAM) | Access requests, role changes, password resets, account unlocks for privileged systems |

Each team has two levels:

- **L1** — first-line engineers. Handle known issues using the troubleshooting guide (IT-KB-001).
- **L2** — specialists. Handle P1 incidents, unknown problems, vendor escalations and repeated failures.

---

## 3. Priority levels and SLA

Priority is decided by **business impact**, not by how loudly the issue is reported.

| Priority | Definition | Examples | Response SLA | Assigned to |
|---|---|---|---|---|
| **P1 — Critical** | Many users or a whole airport affected, or flight operations stopped | Network down at gates; check-in down at a whole station; load control offline | **4 hours** | L2 |
| **P2 — High** | One employee or counter cannot serve passengers or crew | Check-in timeout at one counter; boarding pass printer not printing; gate scanner not reading | **8 hours** | L1 (L2 if repeated) |
| **P3 — Medium** | One employee's work is degraded, a workaround exists | Slow Wi-Fi; Outlook MFA problem; ERP slow | **24 hours** | L1 |
| **P4 — Low** | Requests, questions, minor issues | Access requests; password resets; office printer toner | **72 hours** | L1 or IAM |

Rules:

- The response SLA is the time within which an engineer must start working on the ticket.
- Priority can be raised by the engineer or the duty officer if impact grows (for example one counter becomes five).
- During flight departure peaks, P2 issues at check-in and boarding are treated as urgent within the 8-hour SLA.

---

## 4. Major incident procedure

A **major incident** is an outage that affects several employees, counters or gates at the same time.

### 4.1 How a major incident is detected

The service desk (including the SkyDesk AI agent) must check for similar open tickets when a network or check-in application issue is reported.
A likely major incident exists when **2 or more open tickets from the same airport describe the same problem within the last few hours**.

### 4.2 What happens

1. Create **one** major incident ticket at **P1**, owned by the responsible team (usually Network Support).
2. List the related ticket IDs in the incident ticket so engineers see the full impact.
3. Assign the incident to **L2** immediately.
4. Do not ask affected employees to perform self-service troubleshooting for a confirmed airport-wide outage.
5. New reports of the same problem are **added to the existing incident** as a comment. Do not create duplicate incident tickets.
6. The L2 engineer confirms the outage, informs the station duty officer and the Network Operations Centre, and posts updates to the incident ticket.
7. When the incident is fixed, the related tickets are resolved with a reference to the incident.

### 4.3 Communication

The station duty officer is informed of every P1 at their airport. For outages longer than 30 minutes, the duty officer decides on manual procedures (manual boarding lists, handwritten bag tags).

---

## 5. Access request and approval policy

### 5.1 Principle of least privilege

Employees receive only the access they need for their job. Access is linked to the employee's **department and role** in the employee directory.

### 5.2 Who must approve

| Request | Approver |
|---|---|
| Access to an application used by the employee's own department (e.g. cabin crew → crew scheduling) | The employee's **line manager** |
| Access to another department's system (e.g. gate agent → load control) | The **system owner's manager**, after the line manager |
| Privileged or admin access, payroll or finance edit access | Line manager **and** IAM |
| Password resets | **IAM**, after identity verification (no manager approval needed) |

Only employees with the role **manager** or **IT support (IAM)** may approve. An employee can never approve their own request.

### 5.3 Rules for the SkyDesk AI agent

- The agent must **never grant access itself**.
- For every access request the agent must: check the employee's profile (department, role, manager), create an access request ticket (category Access Request, team IAM, priority P4), and request approval.
- The conversation pauses until an authorised person approves or rejects.
- After approval, IAM provisions the access. After rejection, the ticket is closed with the reason given to the employee.

### 5.4 Typical decisions

- Cabin crew requesting read-only roster access in the crew scheduling application → normally **approved** by the In-flight Services Manager.
- Finance staff requesting ERP modules for their own process → normally **approved** by the Corporate Services Manager.
- Gate agents requesting load control access → normally **rejected**; load control is restricted to load controllers.

---

## 6. Password and account policy

- Passwords must be at least 12 characters and are changed every 90 days.
- Accounts lock after **5 failed login attempts**. Locked accounts are unlocked by Application Support (business apps) or IAM (privileged systems).
- Password resets require identity verification: employee ID plus a code sent to the registered phone.
- IT staff and the SkyDesk AI agent must never ask for, or accept, an employee's password in chat or email.
- MFA is mandatory for email, VPN and remote access. Re-registering MFA on a new phone requires identity verification by IT Support.

---

## 7. Escalation rules (L1 → L2)

A ticket must be escalated to L2 when any of the following is true:

1. It is a **P1** or part of a major incident.
2. The fix needs vendor involvement (for example check-in host latency above 800 ms).
3. The same problem happened **3 or more times in 30 days** for the same device, counter or employee (check similar tickets).
4. L1 has worked on it for more than half of the SLA without a fix.
5. The fix requires changes to a production service, database or integration queue.

Escalation is done by reassigning the ticket to L2 with a comment explaining what was already tried.

---

## 8. Ticket lifecycle

| Status | Meaning |
|---|---|
| open | Created, not yet picked up by an engineer |
| in-progress | An engineer is working on it |
| awaiting-approval | Waiting for a manager or IAM decision (access requests, sensitive actions) |
| resolved | Fixed; the employee is informed |
| closed | Finished without a fix being needed, or rejected, or confirmed by the employee |

Rules:

- Every status change, assignment and approval is written to the **audit log** with who did it and when.
- A ticket is only marked resolved when the fix is confirmed or the employee confirms the problem is gone.
- Resolution comments must describe the actual fix, so that future similar tickets can reuse it.

---

## 9. What the SkyDesk AI agent may and may not do

The agent may:

- Classify issues, set priority and choose the team using this policy.
- Search the knowledge base (IT-KB-001) and give **[Employee]** self-service steps.
- Look up the employee's profile and similar tickets.
- Create, update and assign tickets, and add comments.
- Request approval for sensitive actions.

The agent must not:

- Grant access, reset passwords or change accounts itself.
- Perform **[IT only]** steps or claim that it has repaired an airline system.
- Invent ticket IDs, SOP numbers or ticket statuses.
- Ask for passwords or MFA codes.

Real fixes to airline systems are always carried out by IT engineers.
