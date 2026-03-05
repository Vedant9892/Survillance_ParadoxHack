import { useState, useEffect } from 'react';

export default function Alerts({ incidents = [] }) {
    const [alerts, setAlerts] = useState([]);

    useEffect(() => {
        // Build alerts from incidents
        const mapped = incidents.map((inc, i) => ({
            id: inc.incident_id || `ALERT-${i + 1}`,
            type: inc.incident_type || 'Unknown',
            location: inc.location || 'Unknown',
            timestamp: inc.timestamp || '—',
            confidence: inc.confidence_score || 0,
            priority: inc.confidence_score > 0.85 ? 'critical' : inc.confidence_score > 0.7 ? 'high' : 'medium',
            acknowledged: false,
        }));
        setAlerts(mapped.length > 0 ? mapped : DEFAULT_ALERTS);
    }, [incidents]);

    const priorityColor = (p) => {
        if (p === 'critical') return 'var(--accent-red)';
        if (p === 'high') return 'var(--accent-orange)';
        return 'var(--primary)';
    };

    const acknowledge = (id) => {
        setAlerts(prev => prev.map(a => a.id === id ? { ...a, acknowledged: true } : a));
    };

    const active = alerts.filter(a => !a.acknowledged);
    const acked = alerts.filter(a => a.acknowledged);

    return (
        <div className="alerts-page">
            <div className="alerts-page-header">
                <h2><span className="icon" style={{ fontSize: 20, marginRight: 8, verticalAlign: 'middle' }}>warning</span>Alert Center</h2>
                <div className="alerts-page-count">
                    <span className="apb-active">{active.length} ACTIVE</span>
                    <span className="apb-acked">{acked.length} ACKNOWLEDGED</span>
                </div>
            </div>

            {/* Active Alerts */}
            <div className="alerts-list">
                {active.length === 0 && (
                    <div className="alert-empty">
                        <span className="icon" style={{ fontSize: 40, color: 'var(--accent-green)', opacity: 0.5 }}>verified</span>
                        <div>All clear — no active alerts</div>
                    </div>
                )}
                {active.map(alert => (
                    <div key={alert.id} className={`alert-page-card priority-${alert.priority}`}>
                        <div className="apc-left">
                            <div className="apc-priority" style={{ background: priorityColor(alert.priority) + '20', color: priorityColor(alert.priority) }}>
                                <span className="apc-priority-dot" style={{ background: priorityColor(alert.priority) }}></span>
                                {alert.priority.toUpperCase()}
                            </div>
                            <div className="apc-type">{alert.type}</div>
                            <div className="apc-meta">
                                <span><span className="icon" style={{ fontSize: 12 }}>location_on</span> {alert.location}</span>
                                <span><span className="icon" style={{ fontSize: 12 }}>schedule</span> {alert.timestamp}</span>
                                <span>{(alert.confidence * 100).toFixed(0)}% confidence</span>
                            </div>
                        </div>
                        <div className="apc-right">
                            <button className="apc-ack-btn" onClick={() => acknowledge(alert.id)}>
                                <span className="icon" style={{ fontSize: 14 }}>check</span> Acknowledge
                            </button>
                            <button className="apc-dispatch-btn">
                                <span className="icon" style={{ fontSize: 14 }}>send</span> Dispatch
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Acknowledged */}
            {acked.length > 0 && (
                <>
                    <h3 className="acked-header">Acknowledged</h3>
                    <div className="alerts-list acked">
                        {acked.map(alert => (
                            <div key={alert.id} className="alert-page-card acked">
                                <div className="apc-left">
                                    <div className="apc-type" style={{ opacity: 0.5 }}>{alert.type}</div>
                                    <div className="apc-meta">
                                        <span>{alert.location}</span>
                                        <span>{alert.timestamp}</span>
                                    </div>
                                </div>
                                <span className="icon" style={{ fontSize: 20, color: 'var(--accent-green)' }}>check_circle</span>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}

const DEFAULT_ALERTS = [
    { id: 'ALERT-001', type: 'Weapon detected near individual', location: 'CAM-02 – Market Square', timestamp: '14:02:18', confidence: 0.92, priority: 'critical', acknowledged: false },
    { id: 'ALERT-002', type: 'Dense crowd gathering detected', location: 'CAM-05 – Downtown Plaza', timestamp: '13:45:02', confidence: 0.78, priority: 'high', acknowledged: false },
    { id: 'ALERT-003', type: 'Potential physical assault', location: 'CAM-01 – Metro Station', timestamp: '12:30:15', confidence: 0.71, priority: 'medium', acknowledged: false },
];
