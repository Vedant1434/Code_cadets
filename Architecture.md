# ClinicVault Enterprise – Architecture Documentation

## 1. Architectural Overview

ClinicVault Enterprise is a secure, HIPAA-compliant telemedicine platform built using a **layered, service-oriented architecture**. The system is designed to support real-time video consultations, encrypted medical data handling, automated transcription, and full auditability while maintaining scalability and security.

At a high level, the architecture consists of:

* **Client Layer (Frontend UI)**
* **Application Layer (FastAPI Backend)**
* **Real-Time Communication Layer (WebRTC + WebSockets)**
* **Data Layer (Encrypted Database Storage)**
* **Security & Compliance Layer (Cross-cutting)**

---

## 2. High-Level System Architecture

```
[ Browser / Client ]
        |
        | HTTPS / WSS
        v
[ FastAPI Application ]
        |
        | Async ORM (SQLModel)
        v
[ Encrypted Database ]

[ Client ] <--> [ WebRTC P2P Media Channel ] <--> [ Client ]
            (Signaling via WebSockets)
```

---

## 3. Core Architectural Layers

### 3.1 Client Layer (Presentation)

**Technologies**

* HTML5, Bootstrap
* Jinja2 templates
* JavaScript (WebRTC, WebSocket APIs)

**Responsibilities**

* User authentication and session handling
* Role-based dashboards (Patient / Doctor / Admin)
* WebRTC video rendering
* Live transcript overlays
* Secure file uploads

The frontend remains lightweight, delegating all sensitive logic and PHI handling to the backend.

---

### 3.2 Application Layer (FastAPI Backend)

**Technologies**

* FastAPI
* Python async/await
* JWT authentication

**Responsibilities**

* Request routing and validation
* Business logic enforcement
* Role-Based Access Control (RBAC)
* Consultation lifecycle management
* Payment and state transitions
* Orchestration of real-time services

**Key Modules**

* `auth.py` – Authentication & authorization
* `workflow.py` – Consultation and triage workflow
* `admin.py` – Administrative operations
* `security.py` – Encryption, hashing, token handling

---

### 3.3 Real-Time Communication Layer

#### WebRTC (Media Channel)

* Encrypted peer-to-peer video/audio streaming
* DTLS-SRTP encryption
* Low-latency real-time communication

#### WebSockets (Signaling & Data)

* WebRTC signaling (SDP, ICE candidates)
* Live status updates
* Transcription broadcast
* Chat and system events

This separation ensures scalability while maintaining real-time performance.

---

### 3.4 Transcription & AI Layer

**Technology**

* Faster Whisper (Speech-to-Text)

**Workflow**

1. Audio chunks streamed from client
2. Backend processes audio asynchronously
3. Transcription generated in near real-time
4. Transcripts broadcast to participants via WebSocket
5. Encrypted transcripts persisted after session

The transcription pipeline is fully asynchronous to avoid blocking live consultations.

---

### 3.5 Data Layer

**Technologies**

* SQLModel ORM
* SQLite (development)

**Stored Entities**

* Users (Patients, Doctors, Admins)
* Consultations
* Clinical notes
* Prescriptions
* Transcripts
* Audit logs

**Encryption Strategy**

* PHI fields encrypted using Fernet (AES-256)
* Encryption applied before persistence
* Decryption only at authorized access points

---

## 4. End-to-End Workflow Architecture

### 4.1 User Authentication & Authorization

* JWT-based authentication
* Secure password hashing (bcrypt)
* Role-based permissions enforced at API and DB level
* All authentication events audit-logged

---

### 4.2 Dashboard & Role Segregation

| Role    | Capabilities                                         |
| ------- | ---------------------------------------------------- |
| Patient | Request consultations, view history, upload files    |
| Doctor  | Accept consultations, manage availability, add notes |
| Admin   | User management, audit logs, system monitoring       |

---

### 4.3 Consultation Lifecycle

1. **Triage Initiation**

   * Patient submits symptoms & specialty
   * System auto-assigns available doctor
   * Doctor status → BUSY

2. **Payment Gate**

   * Consultation enters `PENDING_PAYMENT`
   * Successful payment → `ACTIVE`
   * Failure → cancellation and doctor release

3. **Active Session**

   * WebRTC video session established
   * WebSocket channel opened
   * Live transcription enabled
   * Notes & files securely stored

4. **Completion**

   * Doctor ends consultation
   * All session data encrypted & persisted
   * Doctor status → ONLINE

---

## 5. Security & Compliance Architecture

### 5.1 Data Protection

* AES-256 encryption at rest
* HTTPS enforced for all endpoints
* Encrypted backups

### 5.2 Access Control

* Role-based authorization
* Consultation-scoped permissions
* Database-level access enforcement

### 5.3 Audit Logging

* Immutable audit log entries
* Timestamped user actions
* Purpose-of-access tracking

### 5.4 Session Security

* Secure cookies
* CSRF protection
* Token expiration & rotation

---

## 6. Deployment Architecture

### Development

* Local SQLite database
* Single FastAPI instance
* Hot reload enabled

### Production

* Multiple Uvicorn workers
* Reverse proxy with HTTPS
* Load balancer support

```
[ Load Balancer ]
        |
[ FastAPI Instances ]
        |
[ Database (Encrypted) ]
```

---

## 7. Scalability & Extensibility

* Stateless API design
* Horizontal scaling supported
* Modular router structure
* AI components replaceable or extendable
* Future-ready for microservices migration

---

## 8. Architectural Principles

* **Security by Design**
* **Least Privilege Access**
* **Asynchronous First**
* **Clear Separation of Concerns**
* **Compliance-Driven Logging**

---

**ClinicVault Enterprise Architecture** ensures a balance between performance, security, compliance, and extensibility—making it suitable for real-world healthcare environments.
