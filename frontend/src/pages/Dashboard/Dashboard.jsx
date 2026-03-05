import { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import * as tf from '@tensorflow/tfjs';
import * as cocossd from '@tensorflow-models/coco-ssd';

const CAMS = [
    { id: 'CAM-01', name: 'LIVE CAMERA', status: 'live', lat: 19.0440, lng: 73.0290 },
    { id: 'CAM-02', name: 'MARKET - PANVEL', status: 'alert', lat: 18.991296, lng: 73.115834 },
    { id: 'CAM-03', name: 'BUS STOP South Mumbai', status: 'live', lat: 19.062412, lng: 72.860005 },
    { id: 'CAM-04', name: 'EASTERN EXPRESSWAY EXIT', status: 'live', lat: 19.087513, lng: 72.923585 },
    { id: 'CAM-05', name: 'PANVEL HIGHWAY', status: 'live', lat: 19.036500, lng: 73.079851 },
    { id: 'CAM-06', name: 'WORLI BRIDGE', status: 'live', lat: 19.0490, lng: 72.827274 },
];


19.062412, 72.860005

function LiveWebcam() {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);

    useEffect(() => {
        let stream = null;
        let animationId = null;
        let model = null;

        const loadModelAndDetect = async () => {
            try {
                // Ensure TF backend is ready, then load model
                await tf.ready();
                model = await cocossd.load();
                console.log("CocoSSD model loaded");
                detectFrame();
            } catch (err) {
                console.error("Failed to load CocoSSD model", err);
            }
        };

        const detectFrame = async () => {
            if (videoRef.current && videoRef.current.readyState === 4 && model && canvasRef.current) {
                const video = videoRef.current;
                const canvas = canvasRef.current;
                const ctx = canvas.getContext('2d');

                // Set canvas dimensions to match video proper dimensions
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                const predictions = await model.detect(video);

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Draw tactical boxes for "person" class only
                predictions.forEach(prediction => {
                    if (prediction.class === 'person') {
                        const [x, y, width, height] = prediction.bbox;

                        // Main box
                        ctx.strokeStyle = '#00ffff';
                        ctx.lineWidth = 2;
                        ctx.strokeRect(x, y, width, height);

                        // Label background
                        ctx.fillStyle = '#00ffff';
                        const textWidth = ctx.measureText(`PERSON ${(prediction.score * 100).toFixed(0)}%`).width;
                        ctx.fillRect(x, y - 20, textWidth + 10, 20);

                        // Label text
                        ctx.fillStyle = '#000000';
                        ctx.font = '14px Arial';
                        ctx.fillText(`PERSON ${(prediction.score * 100).toFixed(0)}%`, x + 5, y - 5);
                    }
                });
            }
            // Loop
            animationId = requestAnimationFrame(detectFrame);
        };

        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(s => {
                    stream = s;
                    if (videoRef.current) {
                        videoRef.current.srcObject = stream;
                        // Start detection once video is playing
                        videoRef.current.onloadeddata = () => {
                            loadModelAndDetect();
                        };
                    }
                })
                .catch(err => console.error("Error accessing webcam: ", err));
        }

        return () => {
            if (animationId) cancelAnimationFrame(animationId);
            if (stream) stream.getTracks().forEach(track => track.stop());
        };
    }, []);

    return (
        <div style={{ position: 'relative', width: '100%', height: '100%' }}>
            <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
            <canvas
                ref={canvasRef}
                style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    pointerEvents: 'none'
                }}
            />
        </div>
    );
}

function Cam01Map() {
    const cam = CAMS[0]; // CAM-01
    const mapRef = useRef(null);
    const mapInst = useRef(null);

    useEffect(() => {
        if (mapInst.current) return;
        if (!mapRef.current) return;

        const map = L.map(mapRef.current, {
            center: [cam.lat, cam.lng],
            zoom: 17,
            zoomControl: false,
            attributionControl: false,
        });

        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            subdomains: 'abcd',
        }).addTo(map);

        const color = '#00f2ff';
        const icon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="
              width: 22px; height: 22px; border-radius: 50%;
              background: ${color}33; border: 2px solid ${color};
              display: flex; align-items: center; justify-content: center;
              box-shadow: 0 0 16px ${color}80;
            "><div style="width: 8px; height: 8px; border-radius: 50%; background: ${color};"></div></div>`,
            iconSize: [22, 22],
            iconAnchor: [11, 11],
        });

        L.marker([cam.lat, cam.lng], { icon }).addTo(map)
            .bindPopup(`
                <div style="background:#0f172a; color:#f1f5f9; padding:0; border-radius:10px; border:1px solid rgba(255,255,255,0.1); font-family:'Space Grotesk',sans-serif; min-width:220px; overflow:hidden;">
                    <div style="position:relative; width:100%; height:120px; overflow:hidden; background:#000;">
                        <img src="/api/feed/${cam.id}" alt="${cam.name}" style="width:100%; height:100%; object-fit:cover; opacity:0.85;" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
                        <div style="display:none; width:100%; height:100%; align-items:center; justify-content:center; background:#0c1120; color:#475569; font-size:11px;">No Feed Available</div>
                        <div style="position:absolute; top:6px; left:6px; background:rgba(52,211,153,0.8); color:#fff; font-size:8px; font-weight:800; padding:2px 8px; border-radius:4px; text-transform:uppercase; letter-spacing:0.05em;">● LIVE</div>
                    </div>
                    <div style="padding:8px 12px;">
                        <div style="font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:0.1em; color:#00f2ff; margin-bottom:4px;">${cam.id}</div>
                        <div style="font-size:12px; font-weight:600;">${cam.name}</div>
                        <div style="font-size:9px; color:#94a3b8; margin-top:2px;">OPERATIONAL</div>
                        <div style="font-size:9px; color:#64748b; margin-top:2px;">${cam.lat.toFixed(4)}°N, ${cam.lng.toFixed(4)}°E</div>
                        <div style="margin-top:8px;"><a href="#" onclick="window.__mapNavToLive && window.__mapNavToLive(); return false;" style="display:block; text-align:center; background:rgba(13,127,242,0.15); color:#0d7ff2; font-size:9px; font-weight:700; padding:5px 0; border-radius:5px; border:1px solid rgba(13,127,242,0.3); text-decoration:none; text-transform:uppercase; letter-spacing:0.05em;">View Feed</a></div>
                    </div>
                </div>
            `, { className: 'dark-popup', closeButton: false, maxWidth: 240 })
            .openPopup();

        L.circle([cam.lat, cam.lng], {
            radius: 60, color, fillColor: color,
            fillOpacity: 0.06, weight: 1, opacity: 0.3,
        }).addTo(map);

        L.control.zoom({ position: 'bottomright' }).addTo(map);
        mapInst.current = map;

        // Force recalculation of map size after container is laid out
        setTimeout(() => { map.invalidateSize(); }, 200);

        return () => { map.remove(); mapInst.current = null; };
    }, []);

    return <div ref={mapRef} style={{ width: '100%', height: '500px', borderRadius: 10, overflow: 'hidden', background: '#06090e' }}></div>;
}

function IncidentMap() {
    const mapRef = useRef(null);
    const mapInst = useRef(null);

    useEffect(() => {
        if (mapInst.current) return;

        const map = L.map(mapRef.current, {
            center: [19.046, 73.031],
            zoom: 15,
            zoomControl: false,
            attributionControl: false,
        });

        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
        }).addTo(map);

        CAMS.forEach(cam => {
            const isAlert = cam.status === 'alert';
            const color = isAlert ? '#ff3b30' : '#00f2ff';

            const icon = L.divIcon({
                className: 'custom-marker',
                html: `<div style="
          width: 18px; height: 18px; border-radius: 50%;
          background: ${color}33; border: 2px solid ${color};
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 0 12px ${color}80;
        "><div style="width: 6px; height: 6px; border-radius: 50%; background: ${color};"></div></div>`,
                iconSize: [18, 18],
                iconAnchor: [9, 9],
            });

            const marker = L.marker([cam.lat, cam.lng], { icon }).addTo(map);
            marker.bindPopup(`
        <div style="background:#0f172a; color:#f1f5f9; padding:0; border-radius:10px; border:1px solid rgba(255,255,255,0.1); font-family:'Space Grotesk',sans-serif; min-width:220px; overflow:hidden;">
            <div style="position:relative; width:100%; height:120px; overflow:hidden; background:#000;">
                <img src="/api/feed/${cam.id}" alt="${cam.name}" style="width:100%; height:100%; object-fit:cover; opacity:0.85;" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
                <div style="display:none; width:100%; height:100%; align-items:center; justify-content:center; background:#0c1120; color:#475569; font-size:11px;">No Feed Available</div>
                <div style="position:absolute; top:6px; left:6px; background:${isAlert ? 'rgba(255,59,48,0.8)' : 'rgba(52,211,153,0.8)'}; color:#fff; font-size:8px; font-weight:800; padding:2px 8px; border-radius:4px; text-transform:uppercase; letter-spacing:0.05em;">${isAlert ? '⚠ ALERT' : '● LIVE'}</div>
            </div>
            <div style="padding:8px 12px;">
                <div style="font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:0.1em; color:${color}; margin-bottom:4px;">${cam.id}</div>
                <div style="font-size:12px; font-weight:600;">${cam.name}</div>
                <div style="font-size:9px; color:#94a3b8; margin-top:2px;">${isAlert ? '⚠ ACTIVE INCIDENT' : 'OPERATIONAL'}</div>
                <div style="margin-top:8px;"><a href="#" onclick="window.__mapNavToLive && window.__mapNavToLive(); return false;" style="display:block; text-align:center; background:rgba(13,127,242,0.15); color:#0d7ff2; font-size:9px; font-weight:700; padding:5px 0; border-radius:5px; border:1px solid rgba(13,127,242,0.3); text-decoration:none; text-transform:uppercase; letter-spacing:0.05em;">View Feed</a></div>
            </div>
        </div>
      `, { className: 'dark-popup', closeButton: false, maxWidth: 240 });

            if (isAlert) {
                L.circle([cam.lat, cam.lng], { radius: 80, color: '#ff3b30', fillColor: '#ff3b30', fillOpacity: 0.08, weight: 1, opacity: 0.4 }).addTo(map);
            }
        });

        L.control.zoom({ position: 'bottomright' }).addTo(map);
        mapInst.current = map;

        setTimeout(() => { map.invalidateSize(); }, 200);

        return () => { map.remove(); mapInst.current = null; };
    }, []);

    return <div ref={mapRef} style={{ width: '100%', height: '500px', borderRadius: 10, overflow: 'hidden', background: '#06090e' }}></div>;
}

export default function Dashboard({ incidents = [], status, onNavigate }) {
    useEffect(() => {
        window.__mapNavToLive = () => onNavigate && onNavigate('live');
        return () => { delete window.__mapNavToLive; };
    }, [onNavigate]);

    return (
        <div className="dashboard-page">
            <div className="dash-content">
                {/* ── Left: Camera Grid + Map ────────── */}
                <div className="dash-left">
                    <div className="cam-grid">
                        {CAMS.map(cam => (
                            <div key={cam.id} className={`cam-card ${cam.status === 'alert' ? 'alert-state' : ''}`}
                                onClick={() => onNavigate && onNavigate('live')}>
                                {/* Live MJPEG stream from server or Local Webcam */}
                                {cam.id === 'CAM-01' ? (
                                    <LiveWebcam />
                                ) : (
                                    <img src={`/api/feed/${cam.id}`} alt={cam.name}
                                        onError={(e) => { e.target.style.display = 'none'; }}
                                        style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                )}
                                <div className="overlay scanline" style={{ opacity: 0.12 }}></div>
                                <div className="cam-label">
                                    {cam.status === 'alert' && <span className="icon" style={{ fontSize: 14, color: 'var(--accent-red)' }}>warning</span>}
                                    <span className={`dot ${cam.status === 'alert' ? 'alert' : 'live'}`}></span>
                                    {cam.id}: {cam.name}
                                </div>
                                {cam.status === 'alert' && <div className="conf-badge">YOLO Active</div>}
                            </div>
                        ))}
                    </div>

                    {/* Maps Row */}
                    <div className="maps-row">
                        {/* CAM-01 Location Map */}
                        <div className="map-section">
                            <div className="map-header-row">
                                <div>
                                    <h3>CAM-01 Location</h3>
                                    <div className="map-sub">LIVE CAMERA &bull; {CAMS[0].lat.toFixed(4)}&deg;N, {CAMS[0].lng.toFixed(4)}&deg;E</div>
                                </div>
                                <span className="map-status-badge live">LIVE</span>
                            </div>
                            <Cam01Map />
                        </div>

                        {/* Incident Map */}
                        <div className="map-section">
                            <div className="map-header-row">
                                <div>
                                    <h3>Incident Map</h3>
                                    <div className="map-sub">Operational Area &bull; {CAMS.length} active nodes</div>
                                </div>
                                <span className="map-status-badge nodes">{CAMS.length} NODES</span>
                            </div>
                            <IncidentMap />
                        </div>
                    </div>
                </div>

                {/* ── Right Panel ────────────────────── */}
                <div className="dash-right">
                    {/* AI Analysis */}
                    <div className="ai-analysis">
                        <h3>AI Analysis</h3>
                        <div className="threat-circle">
                            <svg viewBox="0 0 36 36">
                                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                    fill="none" stroke="#1e293b" strokeWidth="3" />
                                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                    fill="none" stroke="var(--accent-red)" strokeWidth="3" strokeDasharray="82, 100" strokeLinecap="round" />
                            </svg>
                            <div>
                                <div className="threat-pct">82%</div>
                                <div className="threat-label">Threat</div>
                                <div className="threat-risk">High Risk</div>
                            </div>
                        </div>
                        <ul className="ai-bullets">
                            <li><span className="icon">error</span>Sudden crowd density spike in Sector 7 (+45%)</li>
                            <li><span className="icon">error</span>Non-standard movement patterns detected</li>
                            <li><span className="icon">error</span>Object identification: Unauthorized containers</li>
                        </ul>
                    </div>

                    {/* Active Alerts */}
                    <div className="alerts-section">
                        <div className="alerts-header">
                            <h3>Active Alerts</h3>
                            <span className="priority-badge">{incidents.length > 0 ? incidents.length : 1} PRIORITY</span>
                        </div>
                        {incidents.length > 0 ? (
                            incidents.slice(0, 3).map((inc, i) => (
                                <div key={i} className={`alert-card ${i === 0 ? 'priority' : ''}`}>
                                    <span className="alert-time">{inc.timestamp}</span>
                                    <div className="alert-title">{inc.incident_type}</div>
                                    <div className="alert-desc">{inc.location}. Confidence: {(inc.confidence_score * 100).toFixed(0)}%</div>
                                    <div className="alert-actions">
                                        <button className="btn-dispatch">Dispatch</button>
                                        <button className="btn-view-feed" onClick={() => onNavigate && onNavigate('live')}>View Feed</button>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="alert-card priority">
                                <span className="alert-time">14:02:18</span>
                                <div className="alert-title">Monitoring Active</div>
                                <div className="alert-desc">All cameras running YOLO detection. No incidents detected yet.</div>
                                <div className="alert-actions">
                                    <button className="btn-view-feed" onClick={() => onNavigate && onNavigate('live')}>View Feed</button>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Agentic AI Status */}
                    <div className="ai-status">
                        <h3>Agentic AI Status</h3>
                        {(status?.ai_nodes || [
                            { name: 'Video Monitoring Agent', status: 'active', detail: 'Scanning 6 feeds' },
                            { name: 'Behavior Analysis Agent', status: 'active', detail: 'Analyzing Movement' },
                            { name: 'Threat Assessment Agent', status: 'warning', detail: 'Evaluating Sector 7' },
                            { name: 'Evidence Agent', status: 'active', detail: 'Archiving incidents' },
                            { name: 'LPR Agent', status: 'idle', detail: 'Idle - No Traffic' },
                            { name: 'Dispatch Relay Agent', status: 'active', detail: 'Standby' },
                        ]).map((agent, i) => (
                            <div key={i} className={`agent-row ${agent.status === 'warning' ? 'warn' : ''}`}>
                                <span className="agent-name">
                                    <span className="agent-dot" style={{
                                        background: agent.status === 'active' ? 'var(--accent-green)'
                                            : agent.status === 'warning' ? 'var(--accent-red)'
                                                : 'var(--text-muted)'
                                    }}></span>
                                    {agent.name}
                                </span>
                                <span className={`agent-detail ${agent.status === 'warning' ? '' : agent.status === 'idle' ? 'cyan' : 'green'}`}>
                                    {agent.detail}
                                </span>
                            </div>
                        ))}
                    </div>

                    {/* Incident Log */}
                    <div className="incident-log" style={{ borderRadius: 12, padding: 16, border: '1px solid var(--border)', background: 'var(--surface-glass)' }}>
                        <h3 style={{ fontSize: 11, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>Incident Log</h3>
                        {(incidents.length > 0 ? incidents.slice(0, 5) : [
                            { timestamp: '—', incident_type: 'YOLO detection running on all cameras' },
                            { timestamp: '—', incident_type: 'Behavior analysis active' },
                            { timestamp: '—', incident_type: 'Waiting for incidents...' },
                        ]).map((item, i) => (
                            <div key={i} className="log-entry">
                                <span className="log-time">{item.timestamp}</span>
                                <span className="log-bar"></span>
                                <span className="log-text">{item.incident_type}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
