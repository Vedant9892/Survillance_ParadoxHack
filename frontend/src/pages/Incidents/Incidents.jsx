export default function Incidents({ incidents = [] }) {
    const display = incidents.length > 0 ? incidents : [
        { incident_id: 'CASE-88291-B', timestamp: '2023-10-24 14:02:18', incident_type: 'Market Square Incident', location: 'CAM-02', confidence_score: 0.87 },
        { incident_id: 'CASE-88102-M', timestamp: '2023-10-24 09:15:44', incident_type: 'Metro Perimeter Breach', location: 'CAM-01', confidence_score: 0.92 },
        { incident_id: 'CASE-88055-T', timestamp: '2023-10-23 22:11:02', incident_type: 'Highway Speeding Violation', location: 'CAM-06', confidence_score: 0.74 },
        { incident_id: 'CASE-87994-B', timestamp: '2023-10-23 18:30:12', incident_type: 'Bus Terminal Suspicious Bag', location: 'CAM-03', confidence_score: 0.89 },
        { incident_id: 'CASE-87552-P', timestamp: '2023-10-22 12:00:00', incident_type: 'Plaza Gathering Event', location: 'CAM-05', confidence_score: 0.65 },
        { incident_id: 'CASE-87110-S', timestamp: '2023-10-21 08:44:21', incident_type: 'Station Main Hall Alert', location: 'CAM-04', confidence_score: 0.98 },
    ];

    return (
        <div className="incidents-page">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h2>Evidence Archive Access</h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--accent-orange)', display: 'inline-block' }}></span>
                    <span style={{ fontSize: 10, fontWeight: 700, color: 'var(--accent-orange)', textTransform: 'uppercase', letterSpacing: '0.15em' }}>Evidence Archive Access</span>
                </div>
            </div>

            <div style={{ borderRadius: 12, overflow: 'hidden', border: '1px solid var(--border)', background: 'var(--surface-glass)' }}>
                <table className="incidents-table">
                    <thead>
                        <tr>
                            <th>Case ID</th>
                            <th>Timestamp</th>
                            <th>Incident Type</th>
                            <th>Camera</th>
                            <th>Confidence</th>
                            <th>Evidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        {display.map((inc, i) => (
                            <tr key={i}>
                                <td className="id-col">{inc.incident_id || `CASE-${String(i + 1).padStart(5, '0')}`}</td>
                                <td>{inc.timestamp}</td>
                                <td className="type-col">{inc.incident_type}</td>
                                <td>{inc.location}</td>
                                <td>
                                    <span className="status-pill" style={{
                                        background: inc.confidence_score > 0.8 ? 'rgba(255,59,48,0.15)' : 'rgba(13,127,242,0.15)',
                                        color: inc.confidence_score > 0.8 ? 'var(--accent-red)' : 'var(--primary)'
                                    }}>
                                        {(inc.confidence_score * 100).toFixed(0)}% CONFIDENCE
                                    </span>
                                </td>
                                <td>
                                    {inc.evidence_image ? (
                                        <a href={`/api/screenshots/${inc.evidence_image.split('/').pop()}`} target="_blank" rel="noreferrer"
                                            style={{ color: 'var(--primary)', fontSize: 11, fontWeight: 700, textDecoration: 'none' }}>
                                            View
                                        </a>
                                    ) : (
                                        <span style={{ color: 'var(--text-muted)', fontSize: 11 }}>—</span>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
