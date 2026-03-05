import { useState, useEffect } from 'react';

export default function LiveFeed({ incidents = [], status }) {
    const [feedRunning, setFeedRunning] = useState(false);
    const [loading, setLoading] = useState(false);

    const startFeed = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/feed/start', { method: 'POST' });
            const data = await res.json();
            if (data.status === 'started' || data.status === 'already_running') {
                setFeedRunning(true);
            }
        } catch (e) { console.error(e); }
        setLoading(false);
    };

    const stopFeed = async () => {
        try {
            await fetch('/api/feed/stop', { method: 'POST' });
            setFeedRunning(false);
        } catch (e) { console.error(e); }
    };

    // Check if feed is already running
    useEffect(() => {
        fetch('/api/status').then(r => r.json()).then(d => {
            if (d.feed_running) setFeedRunning(true);
        }).catch(() => { });
    }, []);

    return (
        <div className="live-page">
            <div className="live-main">
                {/* Main Video Feed */}
                <div className="live-feed-container">
                    {feedRunning ? (
                        <>
                            <img src="/api/feed" alt="Live YOLO Detection Feed" />
                            <div className="scanline-overlay scanline"></div>
                            <div className="live-hud-tl">
                                <div className="hud-badge">
                                    <span className="rec-dot"></span>
                                    REC — 4K 30FPS
                                </div>
                                <div className="hud-badge hud-coords">LAT: 41.8781 | LONG: -87.6298</div>
                            </div>
                            <div className="live-hud-br">
                                <button title="Screenshot"><span className="icon" style={{ fontSize: 18 }}>screenshot</span></button>
                                <button onClick={stopFeed} title="Stop Feed"><span className="icon" style={{ fontSize: 18 }}>videocam_off</span></button>
                                <button title="Fullscreen"><span className="icon" style={{ fontSize: 18 }}>fullscreen</span></button>
                            </div>
                        </>
                    ) : (
                        <div className="live-placeholder">
                            <span className="icon">videocam</span>
                            <div style={{ fontSize: 14, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                                {loading ? 'Connecting to webcam...' : 'Camera Feed Offline'}
                            </div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)', maxWidth: 320, textAlign: 'center', lineHeight: 1.5 }}>
                                Click Start to open your webcam and begin YOLOv8 object detection with behavior analysis in real-time.
                            </div>
                            <button className="start-btn" onClick={startFeed} disabled={loading}>
                                {loading ? 'Starting...' : 'Start Live Detection'}
                            </button>
                        </div>
                    )}
                </div>

                {/* Camera Health Table */}
                <div className="cam-health">
                    <div className="cam-health-header">
                        <h3>City-Wide Camera Health</h3>
                        <span>248 ACTIVE NODES</span>
                    </div>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Location</th><th>Signal</th><th>AI Sync</th><th>Status</th></tr>
                        </thead>
                        <tbody>
                            {[
                                { id: 'CAM-01', loc: 'Metro Central Station', signal: 3, sync: 'LOCKED', status: 'OPERATIONAL', color: 'var(--accent-green)' },
                                { id: 'CAM-02', loc: 'Market Square', signal: 4, sync: 'LOCKED', status: feedRunning ? 'LIVE FEED' : 'ALERT STATE', color: feedRunning ? 'var(--primary)' : 'var(--accent-red)' },
                                { id: 'CAM-03', loc: 'Bus Terminal', signal: 2, sync: 'RECONNECTING', status: 'UNSTABLE', color: '#eab308' },
                                { id: 'CAM-04', loc: 'Station', signal: 4, sync: 'LOCKED', status: 'OPERATIONAL', color: 'var(--accent-green)' },
                                { id: 'CAM-05', loc: 'Plaza', signal: 3, sync: 'LOCKED', status: 'OPERATIONAL', color: 'var(--accent-green)' },
                                { id: 'CAM-06', loc: 'Highway', signal: 1, sync: 'OFFLINE', status: 'OFFLINE', color: 'var(--text-muted)' },
                            ].map(c => (
                                <tr key={c.id}>
                                    <td className="cam-id">{c.id}</td>
                                    <td style={{ color: 'var(--text-secondary)' }}>{c.loc}</td>
                                    <td>
                                        <div className="signal-bars">
                                            {[1, 2, 3, 4].map(i => (
                                                <div key={i} className="signal-bar" style={{ background: i <= c.signal ? 'var(--accent-green)' : '#1e293b' }}></div>
                                            ))}
                                        </div>
                                    </td>
                                    <td style={{ color: c.sync === 'LOCKED' ? 'var(--accent-green)' : 'var(--text-muted)' }}>{c.sync}</td>
                                    <td><span className="status-pill" style={{ background: c.color + '18', color: c.color }}>{c.status}</span></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Right Panel */}
            <div className="live-right">
                {/* PTZ Control */}
                <div className="ptz-panel">
                    <h3>PTZ Control — CAM-02</h3>
                    <div className="ptz-dial">
                        <div className="center-icon"><span className="icon">videocam</span></div>
                    </div>
                    <div className="slider-row">
                        <div className="slider-label"><span>Zoom Sensitivity</span><span className="slider-val">85%</span></div>
                        <input type="range" defaultValue={85} />
                    </div>
                    <div className="slider-row">
                        <div className="slider-label"><span>Pan Speed</span><span className="slider-val">42%</span></div>
                        <input type="range" defaultValue={42} />
                    </div>
                </div>

                {/* AI Lens Layers */}
                <div className="lens-panel">
                    <h3>AI Lens Layers</h3>
                    {['Thermal Vision', 'Night Vision', 'Object ID', 'Face Recognition', 'Motion Heatmap'].map((layer, i) => (
                        <div key={layer} className="lens-row">
                            <span>{layer}{layer === 'Face Recognition' ? <span style={{ fontSize: 8, opacity: 0.5, marginLeft: 4 }}>(REDACTED)</span> : ''}</span>
                            <div className={`toggle ${i === 2 || i === 3 ? 'on' : ''}`}>
                                <div className={`knob ${i === 2 || i === 3 ? 'on' : 'off'}`}></div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Quick Switcher */}
                <div className="quick-switch">
                    <div className="quick-switch-header">Quick Switcher</div>
                    <div className="quick-switch-list">
                        {[
                            { id: 'CAM-01', img: 'https://images.unsplash.com/photo-1506544777-64cfbea6eaaf?w=300&q=60', active: false },
                            { id: 'CAM-02 (LIVE)', img: 'https://images.unsplash.com/photo-1590674899484-d5640e854abe?w=300&q=60', active: true },
                            { id: 'CAM-03', img: 'https://images.unsplash.com/photo-1549318180-2d6ec2cb6d85?w=300&q=60', active: false },
                        ].map(t => (
                            <div key={t.id} className={`qs-thumb ${t.active ? 'active' : ''}`}>
                                <img src={t.img} alt={t.id} style={{ filter: t.active ? 'none' : 'grayscale(1)' }} />
                                <div className="scanline" style={{ position: 'absolute', inset: 0, opacity: 0.2 }}></div>
                                <span className="qs-label">{t.id}</span>
                                {t.active && <span className="blink" style={{ position: 'absolute', top: 4, right: 4, width: 7, height: 7, borderRadius: '50%', background: 'var(--accent-red)' }}></span>}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
