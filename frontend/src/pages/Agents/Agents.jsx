import { useState, useEffect } from 'react';

const DEFAULT_AGENTS = [
    { name: 'Video Monitoring Agent', status: 'active', detail: 'Scanning feeds', icon: 'videocam', desc: 'Real-time YOLO inference on all active camera feeds. Detects persons, vehicles, weapons, and objects.' },
    { name: 'Behavior Analysis Agent', status: 'active', detail: 'Analyzing Movement', icon: 'psychology', desc: 'Crowd density analysis, weapon proximity detection, and assault heuristics using spatial clustering.' },
    { name: 'Threat Assessment Agent', status: 'active', detail: 'All Clear', icon: 'gpp_maybe', desc: 'Grok AI-powered threat evaluation. Generates severity scores and emergency recommendations.' },
    { name: 'Evidence Agent', status: 'active', detail: 'Archiving incidents', icon: 'photo_camera', desc: 'Captures and archives evidence screenshots. Links incident records with stored frames.' },
    { name: 'Accident Detection Agent', status: 'active', detail: 'Monitoring uploads', icon: 'car_crash', desc: 'Vehicle overlap IoU, person-vehicle proximity, and clustering heuristics for accident detection.' },
    { name: 'Alert & Dispatch Agent', status: 'active', detail: 'Standby', icon: 'campaign', desc: 'Priority-based alert generation. Saves alerts to Supabase and can trigger emergency dispatch.' },
];

export default function Agents({ status }) {
    const [agents, setAgents] = useState(DEFAULT_AGENTS);

    useEffect(() => {
        if (status?.ai_nodes) {
            setAgents(status.ai_nodes.map((node, i) => ({
                ...DEFAULT_AGENTS[i] || DEFAULT_AGENTS[0],
                name: node.name,
                status: node.status,
                detail: node.detail,
            })));
        }
    }, [status]);

    const statusColor = (s) => s === 'active' ? 'var(--accent-green)' : s === 'warning' ? 'var(--accent-red)' : 'var(--text-muted)';
    const statusLabel = (s) => s === 'active' ? 'ONLINE' : s === 'warning' ? 'WARNING' : 'IDLE';

    return (
        <div className="agents-page">
            <div className="agents-header">
                <h2>Agentic AI Network</h2>
                <div className="agents-meta">
                    <span className="agents-count">{agents.filter(a => a.status === 'active').length}/{agents.length} ACTIVE</span>
                </div>
            </div>
            <div className="agents-grid">
                {agents.map((agent, i) => (
                    <div key={i} className={`agent-card ${agent.status === 'warning' ? 'warn' : ''}`}>
                        <div className="agent-card-top">
                            <div className="agent-icon-wrap" style={{ background: statusColor(agent.status) + '20', borderColor: statusColor(agent.status) }}>
                                <span className="icon" style={{ color: statusColor(agent.status), fontSize: 22 }}>{agent.icon || 'smart_toy'}</span>
                            </div>
                            <div className="agent-status-badge" style={{ background: statusColor(agent.status) + '20', color: statusColor(agent.status) }}>
                                <span className="agent-status-dot" style={{ background: statusColor(agent.status) }}></span>
                                {statusLabel(agent.status)}
                            </div>
                        </div>
                        <h3>{agent.name}</h3>
                        <p className="agent-detail">{agent.detail}</p>
                        <p className="agent-desc">{agent.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
