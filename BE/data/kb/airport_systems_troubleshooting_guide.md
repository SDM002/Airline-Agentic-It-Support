# Saffron Air — Airport & Business Systems Troubleshooting Guide

Document ID: IT-KB-001 · Version 3.2 · Owner: IT Service Desk · Classification: Internal
Saffron Air is a fictional airline used for this proof of concept. All procedures are synthetic.

This guide is used by the SkyDesk AI helpdesk agent and by L1/L2 IT engineers. Each section is a Standard Operating Procedure (SOP).
Steps marked **[Employee]** are safe for any employee to perform. Steps marked **[IT only]** must be performed by an IT engineer.
If self-service steps do not fix the problem, raise a ticket to the team named in the SOP.

---

## 1. Check-in Application (Departure Control)

The check-in application runs on every check-in counter, gate and kiosk PC. It connects to the central departure control host over the airport MPLS network.
Owner: **Application Support**.

### SOP-APP-001 — Check-in application shows "connection timeout"

Symptoms: PNR lookups or check-in hang and end with "connection timeout"; passengers queue at the counter.

1. **[Employee]** Finish or save any passenger you are working on. Do not leave a passenger half checked in.
2. **[Employee]** Close the check-in application completely (File → Exit) and open it again. Log in with your staff ID.
3. **[Employee]** Check whether the counter next to you has the same problem. If several counters are affected, tell your duty officer and report it as a possible network incident (see SOP-NET-001).
4. **[Employee]** If only your counter is affected, restart the counter PC once.
5. **[IT only]** Purge the local session cache folder of the check-in client and re-launch it. This fixes most single-counter timeouts.
6. **[IT only]** Check host link latency from the station. If latency is above **800 ms**, escalate to the vendor bridge and raise the ticket to **L2 Application Support**.

Priority: **P2** if one counter cannot check in passengers; **P1** if several counters or the whole station are affected.

### SOP-APP-002 — Check-in screen frozen or not responding

Symptoms: screen does not respond to mouse or keyboard, often during flight close-out.

1. **[Employee]** Wait 60 seconds — the application may be finishing a close-out transaction.
2. **[Employee]** Do **not** reboot the PC during flight close-out. Rebooting can corrupt the flight's closing data.
3. **[Employee]** If still frozen, press Ctrl+Alt+Del → Task Manager → end the check-in application, then reopen it.
4. **[IT only]** Purge the local session cache and re-launch. Confirm the flight's close-out status with the duty officer.

### SOP-APP-003 — "Session expired" immediately after login

Symptoms: user logs in successfully and is logged out at once with "session expired".

1. **[Employee]** Check the time shown on the PC clock. If it differs from your phone by more than 2 minutes, report it.
2. **[Employee]** Log out, close the application and log in again.
3. **[IT only]** Re-sync the workstation clock with the station time server. Session tokens are rejected when the clock is more than 5 minutes off.

### SOP-APP-004 — Seat map blank or not loading

1. **[Employee]** Refresh the flight (F5) and reopen the seat map.
2. **[Employee]** Check another flight. If seat maps are blank for all flights, it is a service problem, not your PC.
3. **[IT only]** Restart the seat map service (L2 Application Support only). Raise as **P2**.

### SOP-APP-005 — "Device not mapped" when printing boarding passes or bag tags

1. **[Employee]** Check that the printer is switched on and shows a green ready light.
2. **[Employee]** In the check-in application open Settings → Devices and check that the counter's printer is selected.
3. **[IT only]** Re-map the boarding pass or bag tag printer in the check-in application device settings.

### SOP-APP-006 — Check-in application slow at gates

1. **[Employee]** Note how long one passenger takes to load (e.g. 30 seconds).
2. **[IT only]** Check whether the gate PC has failed over to the backup LTE link. LTE is for emergencies only and is slow. Switch back to MPLS once the main line is repaired (see SOP-NET-003).

---

## 2. Airport Network and Wi-Fi

Airport systems use the wired MPLS network; staff devices and handheld scanners use the staff Wi-Fi.
Owner: **Network Support**.

### SOP-NET-001 — Network down at gates, counters or offices

Symptoms: PCs show "no network", applications cannot connect, Wi-Fi not available.

1. **[Employee]** Check one other device nearby (a colleague's PC or phone on staff Wi-Fi).
2. **[Employee]** Check the network cable is plugged in at both ends.
3. **[Employee]** If more than one device or area is affected, **do not** troubleshoot further. Inform the duty officer and report it immediately.
4. **[IT only]** Check the switch and access points for the affected area in the network monitoring tool.
5. **[IT only]** If the MPLS link is down, fail over the station router to the LTE backup (SOP-NET-003) and notify the Network Operations Centre.

Priority: **P1** for gate, counter or load-control areas affecting operations; **P2** for a single office.
Multiple reports from the same airport within a short time must be handled as one major incident (see IT-POL-002, Section 4).

### SOP-NET-002 — Staff Wi-Fi slow or dropping

1. **[Employee]** Forget the staff Wi-Fi network on your device and reconnect.
2. **[Employee]** Move closer to an access point and try again.
3. **[IT only]** Reboot or update the firmware of the access point serving the area.
4. **[IT only]** Check for bandwidth-heavy traffic (for example video streaming) and block it by policy.

Priority: **P3** unless operations are blocked.

### SOP-NET-003 — Station LAN failover to LTE backup

**[IT only]** When the MPLS link is down: switch the station router to the LTE backup link, inform the Network Operations Centre, and tell the station that systems will be slower. Switch back to MPLS as soon as the line is repaired.

### SOP-NET-004 — VPN not connecting from home or travel

1. **[Employee]** Check your internet connection works (open any public website).
2. **[Employee]** Restart the VPN client and sign in again.
3. **[Employee]** If the error says "authentication failed" or "certificate", report it — do not reinstall the client yourself.
4. **[IT only]** Renew the VPN client certificate through endpoint manager. Certificates are valid for 365 days.

---

## 3. Boarding Pass and Bag Tag Printers

Counters and gates use thermal printers for boarding passes (ATB stock) and bag tags.
Owner: **Hardware Support**.

Before raising a ticket, the employee must give: **printer ID** (label on the printer, e.g. BPP-DEL-12), **counter or gate number**, and **the error or light shown**.

### SOP-HW-001 — Boarding pass printer not printing or printing blank

1. **[Employee]** Open the printer lid. Remove any jammed or crumpled boarding pass stock.
2. **[Employee]** Check you are using approved Saffron Air boarding pass stock. Wrong stock causes jams and blank prints.
3. **[Employee]** Close the lid firmly and press the feed button once. One blank pass should feed out.
4. **[Employee]** Print a test pass from the check-in application.
5. **[IT only]** Re-map the printer in the check-in application (SOP-APP-005).

Priority: **P2** — a counter cannot serve passengers without boarding passes.

### SOP-HW-002 — Printer shows "offline" in the check-in application

1. **[Employee]** Check the printer power light. Switch the printer off, wait 10 seconds, switch it on.
2. **[Employee]** Check the cable between the printer and the PC is firmly connected.
3. **[Employee]** In the check-in application, select the printer again in Settings → Devices.
4. **[IT only]** Replace the USB-serial adapter if the printer stays offline — this is the most common hardware cause.

### SOP-HW-003 — Bag tags printing faded or unreadable

1. **[Employee]** Check the bag tag stock is loaded label-side up.
2. **[IT only]** Clean the print head and adjust the print darkness setting. Replace the print head if cleaning does not help.

### SOP-HW-004 — Office printer problems (toner, driver, garbled output)

1. **[Employee]** Check the printer display for "toner low" or "paper jam" messages.
2. **[IT only]** Replace toner, or reinstall the printer driver if output contains garbage characters.

Priority: **P4** for office printers unless finance or payroll deadlines are affected (P3).

---

## 4. Barcode Scanners (Gate and Baggage)

Handheld scanners read boarding passes at gates and bag tags on the ramp. They connect over the handheld Wi-Fi network.
Owner: **Hardware Support**.

Before raising a ticket, give the **scanner ID**, the **gate or belt number** and what happens when you scan.

### SOP-HW-010 — Scanner does not read boarding passes or bag tags

1. **[Employee]** Clean the scanner window with a soft cloth.
2. **[Employee]** For mobile boarding passes, ask the passenger to increase phone screen brightness.
3. **[Employee]** Restart the scanner (hold the power button for 5 seconds).
4. **[IT only]** Reset the scanner firmware and re-pair it with the gate terminal.

### SOP-HW-011 — Scanner beeps but the system receives nothing

1. **[Employee]** Restart the scanner and the gate application.
2. **[IT only]** Re-enable keyboard-wedge mode in the scanner settings.

### SOP-HW-012 — Scanner shows "no host connection"

1. **[Employee]** Check the Wi-Fi icon on the scanner. Move closer to the gate or belt.
2. **[IT only]** Re-join the scanner to the handheld Wi-Fi network.

### SOP-HW-013 — Battery drains quickly or scanner is physically damaged

1. **[Employee]** Swap to a charged spare battery from the charging cradle.
2. **[Employee]** For a cracked screen or broken unit, stop using it and collect a spare from the station IT cupboard.
3. **[IT only]** Replace the battery or the unit.

Priority: **P2** at an active gate or belt; **P3** if a spare is available.

---

## 5. Crew Scheduling Application

Used by cabin crew to view rosters and by crew schedulers to build pairings. Rosters are published from the planning system through an integration queue.
Owner: **Application Support**.

### SOP-CRW-001 — Crew scheduling application stuck on loading

1. **[Employee]** Close the application and open it again. On mobile, update the app from the company portal.
2. **[Employee]** Check whether colleagues have the same problem.
3. **[IT only]** Check the integration queue for stuck roster publish messages and clear them. Raise as **P2** if crew cannot see duties for the next 24 hours.

### SOP-CRW-002 — Roster not updated or duties missing

1. **[Employee]** Pull down to refresh, then log out and log in again.
2. **[IT only]** Trigger a manual roster publish from the planning system.
3. **[IT only]** For missing standby duties, check the standby duty type mapping.

### SOP-CRW-003 — "User not found" on login

1. **[Employee]** Check you are using your staff ID, not your email address.
2. **[IT only]** Link the crew profile to the login account. If the employee has no access at all, this is an **access request** — follow IT-POL-002, Section 5.

### SOP-CRW-004 — Wrong duty hours or slow pairing creation

1. **[IT only]** Wrong duty hours: check the time zone setting for imported flights.
2. **[IT only]** Slow pairing creation: rebuild the database index (L2 only, outside peak planning hours).

---

## 6. ERP (Finance, Payroll, Procurement)

Owner: **Application Support**.

### SOP-ERP-001 — ERP login failure ("invalid credentials")

1. **[Employee]** Check Caps Lock and that you are using your current password.
2. **[Employee]** If you changed your password recently, clear the saved password in your browser and type it again.
3. **[Employee]** Do not keep retrying — the account locks after **5 failed attempts**.
4. **[IT only]** Unlock the ERP account. If a password reset is needed, follow the password policy (IT-POL-002, Section 6).

### SOP-ERP-002 — ERP slow, reports timing out or workflow stuck

1. **[Employee]** Note the module, the report name and the time it happened.
2. **[IT only]** Restart stuck workflow jobs (for example invoice approval).
3. **[IT only]** For report timeouts, optimise the report query and rerun it overnight. Payroll reports near the payroll deadline are **P2**.

---

## 7. Email and Microsoft 365

Owner: **IT Support**.

### SOP-M365-001 — Cannot sign in to Outlook / MFA keeps failing

1. **[Employee]** Check the time on your phone is set automatically — MFA codes fail if the phone clock is wrong.
2. **[Employee]** Approve the sign-in in the authenticator app, or use the 6-digit code.
3. **[Employee]** If you have a new phone, the authenticator must be set up again — report it.
4. **[IT only]** Re-register the MFA method in Microsoft 365 after verifying the employee's identity.

### SOP-M365-002 — Account blocked on mobile

1. **[IT only]** Enrol the phone in device management. Company email is only allowed on enrolled devices.

### SOP-M365-003 — Mailbox full, Teams problems, not receiving email

1. **[Employee]** Mailbox full: delete large old emails and empty Deleted Items.
2. **[Employee]** Teams stuck on a white screen: quit Teams fully and reopen.
3. **[IT only]** Enable the online archive; clear the Teams cache; check quarantine rules if external email is missing (**P2** if business email is blocked for a department).

---

## 8. When to stop self-service and raise a ticket

Raise a ticket immediately, without self-service, when:

- More than one employee, counter or gate is affected (possible major incident).
- The fix requires an **[IT only]** step.
- The employee asks for access to a system, or a password reset (always needs approval or identity checks).
- Equipment is physically damaged.
- Self-service steps were tried and the problem continues.

Include in every ticket: what happened, where (airport, counter/gate), device ID if hardware, error message, and steps already tried.
