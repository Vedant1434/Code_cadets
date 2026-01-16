from fastapi.responses import HTMLResponse
from jinja2 import Environment, DictLoader

# --- CSS & Layout Constants ---
HEAD_CONTENT = """
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClinicVault | Enterprise Health System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #0d6efd; --secure: #198754; --admin: #6610f2; --bg: #f8f9fa; }
        body { background-color: var(--bg); font-family: 'Segoe UI', system-ui, sans-serif; }
        .navbar { background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .secure-badge { background: #e8f5e9; color: #1b5e20; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; border: 1px solid #c8e6c9; }
        
        /* Video Container */
        .video-wrapper { position: relative; background: #000; border-radius: 12px; overflow: hidden; height: 500px; }
        video { width: 100%; height: 100%; object-fit: cover; }
        #localVideo { position: absolute; bottom: 20px; right: 20px; width: 160px; height: 120px; border: 2px solid white; border-radius: 8px; z-index: 10; background: #333; }
        
        /* Controls Overlay */
        .video-controls {
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
            background: rgba(0,0,0,0.6); padding: 10px 20px; border-radius: 30px;
            display: flex; gap: 15px; z-index: 20;
        }
        .control-btn { 
            width: 45px; height: 45px; border-radius: 50%; border: none; 
            display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
            transition: all 0.2s; color: white; background: #444;
        }
        .control-btn:hover { background: #666; }
        .control-btn.active { background: #dc3545; color: white; }
        .control-btn.recording { background: #dc3545; animation: pulse 1.5s infinite; }

        /* Transcript Overlay */
        #transcriptContainer {
            position: absolute; top: 20px; left: 20px; right: 20px;
            pointer-events: none; z-index: 15;
            display: flex; flex-direction: column; align-items: center;
        }
        .transcript-bubble {
            background: rgba(0,0,0,0.7); color: white; padding: 10px 20px;
            border-radius: 20px; margin-bottom: 10px; max-width: 80%;
            animation: fadeIn 0.3s ease; text-align: center;
            backdrop-filter: blur(4px);
        }

        /* Separate Chat/Transcript Tabs */
        .chat-container { height: 400px; display: flex; flex-direction: column; }
        .chat-messages { flex-grow: 1; overflow-y: auto; padding: 10px; background: #f8f9fa; }
        .msg { padding: 8px 12px; margin-bottom: 8px; border-radius: 8px; max-width: 85%; font-size: 0.95rem; }
        .msg.user { background: #e3f2fd; align-self: flex-end; margin-left: auto; }
        .msg.peer { background: white; border: 1px solid #dee2e6; align-self: flex-start; }
        .msg.system { background: #fff3cd; color: #856404; text-align: center; width: 100%; font-size: 0.8rem; }
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }
    </style>
</head>
"""

NAVBAR_CONTENT = """
<nav class="navbar navbar-expand-lg navbar-light mb-4">
    <div class="container">
        <a class="navbar-brand fw-bold" href="/">
            <i class="fas fa-hospital-user text-primary"></i> ClinicVault <small class="text-muted fw-light">v2.0</small>
        </a>
        <div class="d-flex align-items-center">
            {% if user %}
                <span class="me-3 text-muted">
                    {{ user.full_name }} 
                    <span class="badge bg-secondary ms-1">{{ user.role | upper }}</span>
                </span>
                <a href="/logout" class="btn btn-outline-secondary btn-sm">Logout</a>
            {% endif %}
        </div>
    </div>
</nav>
"""

# --- Page Templates ---
BASE_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
{HEAD_CONTENT}
<body>
    {NAVBAR_CONTENT}
    <div class="container">
        {{% block content %}}{{% endblock %}}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Global Toast Container -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
        <div id="liveToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body" id="toastMessage"></div>
        </div>
    </div>
    <script>
        function showToast(msg) {{
            document.getElementById('toastMessage').innerText = msg;
            const toast = new bootstrap.Toast(document.getElementById('liveToast'));
            toast.show();
        }}
    </script>
</body>
</html>
"""

CONSULTATION_TEMPLATE = """
{% extends "base" %}
{% block content %}
<div class="row">
    <!-- Main Video Stage -->
    <div class="col-lg-8 mb-4">
        <div class="video-wrapper shadow-sm">
            <video id="remoteVideo" autoplay playsinline></video>
            <video id="localVideo" autoplay playsinline muted></video>
            
            <!-- Floating Transcripts -->
            <div id="transcriptContainer"></div>
            
            <!-- Controls -->
            <div class="video-controls">
                <button class="control-btn" id="btnToggleAudio" title="Mute/Unmute"><i class="fas fa-microphone"></i></button>
                <button class="control-btn" id="btnToggleVideo" title="Start/Stop Video"><i class="fas fa-video"></i></button>
                <button class="control-btn" id="btnToggleTranscript" title="Show/Hide Captions"><i class="fas fa-closed-captioning"></i></button>
                <div style="width:1px; background:#666; height:30px;"></div>
                <button class="control-btn" id="btnRecord" title="Start Transcription"><i class="fas fa-wave-square"></i></button>
                <a href="/consultation/end/{{ consultation.id }}" class="control-btn" style="background: #dc3545;" title="End Call"><i class="fas fa-phone-slash"></i></a>
            </div>
        </div>
        
        <!-- Doctor Tools -->
        {% if user.role == 'doctor' %}
        <div class="card mt-3">
            <div class="card-body">
                <h6 class="card-title"><i class="fas fa-notes-medical"></i> Clinical Notes (Private)</h6>
                <form action="/consultation/notes" method="post">
                    <input type="hidden" name="consultation_id" value="{{ consultation.id }}">
                    <div class="input-group">
                        <textarea name="notes" class="form-control" rows="2" placeholder="Private observations..."></textarea>
                        <button class="btn btn-primary">Save Encrypted</button>
                    </div>
                </form>
            </div>
        </div>
        {% endif %}
    </div>

    <!-- Sidebar -->
    <div class="col-lg-4">
        <!-- Patient Info -->
        <div class="card mb-3">
            <div class="card-header bg-light"><strong>Patient Data</strong></div>
            <div class="card-body">
                <small class="text-muted">Symptoms:</small>
                <div class="alert alert-light border">{{ symptoms_decrypted }}</div>
            </div>
        </div>

        <!-- Chat Area -->
        <div class="card chat-container mb-3">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
                <span><i class="fas fa-comments"></i> Live Chat</span>
                <span class="badge bg-success" id="connectionStatus">Connected</span>
            </div>
            <div class="chat-messages d-flex flex-column" id="chatBox">
                <div class="msg system">Secure channel established.</div>
            </div>
            <div class="card-footer bg-white">
                <input type="text" id="msgInput" class="form-control" placeholder="Type a message...">
            </div>
        </div>
        
        <!-- History (Only visible to Doctors) -->
        {% if user.role == 'doctor' and history %}
        <div class="card">
            <div class="card-header bg-info text-white"><i class="fas fa-history"></i> Patient History</div>
            <div class="list-group list-group-flush" style="max-height: 200px; overflow-y: auto;">
                {% for h in history %}
                <div class="list-group-item">
                    <div class="d-flex justify-content-between">
                        <small class="fw-bold">{{ h.date }}</small>
                        <small class="text-muted">{{ h.specialty }}</small>
                    </div>
                    <small class="text-muted fst-italic">Dr. {{ h.doctor_name }}</small>
                    <p class="mb-0 small mt-1">{{ h.notes }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
</div>

<script>
    const consultId = "{{ consultation.id }}";
    const userId = "{{ user.id }}";
    const userName = "{{ user.full_name }}";
    const wsUrl = "ws://" + window.location.host + "/ws/" + consultId + "/" + userId;
    let ws = new WebSocket(wsUrl);
    
    // UI Elements
    const localVideo = document.getElementById('localVideo');
    const remoteVideo = document.getElementById('remoteVideo');
    const chatBox = document.getElementById('chatBox');
    const transcriptContainer = document.getElementById('transcriptContainer');
    
    // State
    let localStream;
    let peerConnection;
    let showCaptions = false;
    let isRecording = false;
    let recorderStream;
    
    // WebRTC Config
    const rtcConfig = { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] };

    // --- WebSocket Logic ---
    ws.onmessage = async (event) => {
        try {
            const msg = JSON.parse(event.data);
            
            if (msg.type === "transcript") {
                if (showCaptions) showFloatingTranscript(msg.text);
            }
            else if (msg.type === "chat") {
                addChatMessage(msg.sender, msg.text, 'peer');
            }
            else if (msg.type === "system") {
                addChatMessage("System", msg.text, 'system');
                if (msg.text.includes("left")) {
                    remoteVideo.srcObject = null;
                    showToast("Partner disconnected");
                }
            }
            else if (msg.type === "offer") await handleOffer(msg);
            else if (msg.type === "answer") await handleAnswer(msg);
            else if (msg.type === "candidate") await handleCandidate(msg);
            
        } catch(e) { console.error(e); }
    };

    // --- UI Actions ---
    function addChatMessage(sender, text, type) {
        const div = document.createElement('div');
        div.className = `msg ${type}`;
        div.innerText = type === 'system' ? text : `${text}`;
        if (type === 'peer') div.title = sender;
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function showFloatingTranscript(text) {
        const bubble = document.createElement('div');
        bubble.className = 'transcript-bubble';
        bubble.innerText = text;
        transcriptContainer.appendChild(bubble);
        setTimeout(() => bubble.remove(), 5000);
    }

    document.getElementById('msgInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const text = e.target.value;
            ws.send(JSON.stringify({ type: "chat", text: text, sender: userName }));
            addChatMessage("Me", text, 'user');
            e.target.value = '';
        }
    });

    // --- Media Controls ---
    document.getElementById('btnToggleAudio').onclick = () => {
        const track = localStream.getAudioTracks()[0];
        track.enabled = !track.enabled;
        document.getElementById('btnToggleAudio').classList.toggle('active', !track.enabled);
    };

    document.getElementById('btnToggleVideo').onclick = () => {
        const track = localStream.getVideoTracks()[0];
        track.enabled = !track.enabled;
        document.getElementById('btnToggleVideo').classList.toggle('active', !track.enabled);
    };

    document.getElementById('btnToggleTranscript').onclick = function() {
        showCaptions = !showCaptions;
        this.classList.toggle('active', showCaptions);
        showToast(showCaptions ? "Captions ON" : "Captions OFF");
    };

    // --- WebRTC Logic ---
    async function startMedia() {
        try {
            localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            localVideo.srcObject = localStream;
            
            // Initiate Call
            peerConnection = new RTCPeerConnection(rtcConfig);
            peerConnection.onicecandidate = e => {
                if(e.candidate) ws.send(JSON.stringify({ type: "candidate", candidate: e.candidate }));
            };
            peerConnection.ontrack = e => { remoteVideo.srcObject = e.streams[0]; };
            
            localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));
            
            // Allow time for socket to connect then offer
            setTimeout(async () => {
                if (userId > consultId) { // Simple logic to decide who offers (avoids collision)
                    const offer = await peerConnection.createOffer();
                    await peerConnection.setLocalDescription(offer);
                    ws.send(JSON.stringify({ type: "offer", sdp: offer }));
                }
            }, 1000);
            
        } catch(e) { showToast("Camera access denied"); }
    }
    
    // WebRTC Handlers
    async function handleOffer(msg) {
        if (!peerConnection) {
             peerConnection = new RTCPeerConnection(rtcConfig);
             peerConnection.onicecandidate = e => { if(e.candidate) ws.send(JSON.stringify({ type: "candidate", candidate: e.candidate })); };
             peerConnection.ontrack = e => { remoteVideo.srcObject = e.streams[0]; };
             localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));
        }
        await peerConnection.setRemoteDescription(new RTCSessionDescription(msg.sdp));
        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);
        ws.send(JSON.stringify({ type: "answer", sdp: answer }));
    }
    
    async function handleAnswer(msg) { await peerConnection.setRemoteDescription(new RTCSessionDescription(msg.sdp)); }
    async function handleCandidate(msg) { if(peerConnection) await peerConnection.addIceCandidate(new RTCIceCandidate(msg.candidate)); }

    startMedia(); // Auto start camera on load

    // --- Transcription Loop ---
    document.getElementById('btnRecord').onclick = async function() {
        if (!isRecording) {
            isRecording = true;
            this.classList.add('recording');
            if (!recorderStream) recorderStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            startTranscribing();
        } else {
            isRecording = false;
            this.classList.remove('recording');
        }
    };

    function startTranscribing() {
        if (!isRecording) return;
        const mediaRecorder = new MediaRecorder(recorderStream);
        const chunks = [];
        mediaRecorder.ondataavailable = e => chunks.push(e.data);
        mediaRecorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'audio/webm' });
            if (blob.size > 1000 && isRecording) {
                const fd = new FormData();
                fd.append("audio_blob", blob);
                fd.append("consultation_id", consultId);
                fd.append("user_id", userId);
                fetch("/consultation/transcribe", { method: "POST", body: fd });
            }
            if (isRecording) startTranscribing();
        };
        mediaRecorder.start();
        setTimeout(() => mediaRecorder.stop(), 3000);
    }
</script>
{% endblock %}
"""

# Store templates
HTML_TEMPLATES = {
    "base": BASE_TEMPLATE,
    "consultation": CONSULTATION_TEMPLATE,
    # Login/Register/Dashboard templates are simplified for brevity but follow the same modular pattern
    "login": """{% extends "base" %}
    {% block content %}
    <div class="row justify-content-center mt-5"><div class="col-md-5"><div class="card p-4 shadow-sm">
        <h3 class="text-center mb-4">Portal Login</h3>
        <form action="/auth/login" method="post">
            <div class="mb-3"><label>Email</label><input type="email" name="username" class="form-control" required></div>
            <div class="mb-3"><label>Password</label><input type="password" name="password" class="form-control" required></div>
            <button class="btn btn-primary w-100">Login</button>
        </form>
        <div class="mt-3 text-center"><a href="/register">Create Patient Account</a> | <form action="/auth/seed" method="post" class="d-inline"><button class="btn btn-link p-0">Seed Data</button></form></div>
    </div></div></div>
    {% endblock %}""",
    
    "register": """{% extends "base" %}
    {% block content %}
    <div class="row justify-content-center mt-5"><div class="col-md-5"><div class="card p-4">
        <h3>New Patient</h3>
        <form action="/auth/register" method="post">
            <div class="mb-3"><label>Name</label><input type="text" name="full_name" class="form-control" required></div>
            <div class="mb-3"><label>Email</label><input type="email" name="email" class="form-control" required></div>
            <div class="mb-3"><label>Password</label><input type="password" name="password" class="form-control" required></div>
            <button class="btn btn-success w-100">Register</button>
        </form>
    </div></div></div>
    {% endblock %}""",

    "dashboard_patient": """{% extends "base" %}
    {% block content %}
    <div class="row"><div class="col-md-8"><div class="card p-4">
        <h4>My Triage</h4>
        {% if active_consultation %}
            <div class="alert alert-success">
                <strong>Active Case:</strong> {{ active_consultation.specialty }} <br>
                Status: {{ active_consultation.status }}
                {% if active_consultation.status == 'active' %}<a href="/consultation/{{ active_consultation.id }}" class="btn btn-success ms-3">Join Room</a>{% endif %}
                {% if active_consultation.status == 'pending_payment' %}<a href="/billing/{{ active_consultation.id }}" class="btn btn-warning ms-3">Pay Now</a>{% endif %}
            </div>
        {% else %}
            <form action="/triage/start" method="post">
                <select name="specialty" class="form-select mb-3"><option>Cardiology</option><option>Dermatology</option><option>General</option></select>
                <textarea name="symptoms" class="form-control mb-3" placeholder="Describe symptoms..."></textarea>
                <button class="btn btn-primary">Request Doctor</button>
            </form>
        {% endif %}
    </div></div></div>
    {% endblock %}""",
    
    "dashboard_doctor": """{% extends "base" %}
    {% block content %}
    <h4>Doctor Dashboard</h4>
    <div class="d-flex justify-content-between mb-3">
        <span>Status: <strong>{{ user.status }}</strong></span>
        <a href="/doctor/toggle_status" class="btn btn-sm btn-outline-primary">Toggle Status</a>
    </div>
    <div class="row">
        {% for c in consultations %}
        <div class="col-md-4"><div class="card p-3 mb-3">
            <h5>Patient #{{ c.patient_id }}</h5>
            <p>Status: {{ c.status }}</p>
            {% if c.status == 'active' %}<a href="/consultation/{{ c.id }}" class="btn btn-success">Enter Room</a>{% endif %}
        </div></div>
        {% endfor %}
    </div>
    {% endblock %}""",
    
    "dashboard_admin": """{% extends "base" %}
    {% block content %}
    <h4>Admin Panel</h4>
    <div class="row">
        <div class="col-md-4">
            <form action="/admin/add_doctor" method="post" class="card p-3">
                <h6>Add Doctor</h6>
                <input name="full_name" placeholder="Name" class="form-control mb-2">
                <input name="email" placeholder="Email" class="form-control mb-2">
                <input name="password" placeholder="Pass" class="form-control mb-2">
                <select name="specialty" class="form-select mb-2"><option>Cardiology</option><option>General</option></select>
                <button class="btn btn-primary btn-sm">Add</button>
            </form>
        </div>
    </div>
    {% endblock %}""",

    "billing": """{% extends "base" %}
    {% block content %}
    <div class="card p-5 text-center" style="max-width:500px; margin:auto;">
        <h3>Invoice: $20.00</h3>
        <p>Consultation #{{ consultation.id }}</p>
        <form action="/billing/process" method="post">
            <input type="hidden" name="consultation_id" value="{{ consultation.id }}">
            <button name="outcome" value="success" class="btn btn-success">Pay Success</button>
            <button name="outcome" value="fail" class="btn btn-danger">Pay Fail</button>
        </form>
    </div>
    {% endblock %}"""
}

def render_template(name: str, context: dict):
    env = Environment(loader=DictLoader(HTML_TEMPLATES))
    tmpl = env.get_template(name)
    return HTMLResponse(tmpl.render(**context))