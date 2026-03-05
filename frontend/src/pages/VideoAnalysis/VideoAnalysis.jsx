import { useState, useRef } from 'react';

export default function VideoAnalysis() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState('');
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [dragOver, setDragOver] = useState(false);
    const inputRef = useRef(null);

    const handleFile = (f) => {
        if (!f) return;
        const allowed = ['video/mp4', 'video/avi', 'video/x-msvideo', 'video/quicktime', 'video/x-matroska'];
        if (!allowed.includes(f.type) && !f.name.match(/\.(mp4|avi|mov|mkv)$/i)) {
            setError('Unsupported file type. Use MP4, AVI, MOV, or MKV.');
            return;
        }
        setFile(f);
        setError(null);
        setResult(null);
        setPreview(URL.createObjectURL(f));
    };

    const onDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const f = e.dataTransfer.files[0];
        handleFile(f);
    };

    const upload = async () => {
        if (!file) return;
        setUploading(true);
        setProgress('Uploading video...');
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            setProgress('Analyzing video — running YOLOv8 accident detection...');
            const res = await fetch('/api/upload_accident_video', {
                method: 'POST',
                body: formData,
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: 'Server error' }));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }

            const data = await res.json();
            setResult(data);
            setProgress('');
        } catch (e) {
            setError(e.message || 'Upload failed');
            setProgress('');
        }
        setUploading(false);
    };

    const reset = () => {
        setFile(null);
        setPreview(null);
        setResult(null);
        setError(null);
        setProgress('');
        if (inputRef.current) inputRef.current.value = '';
    };

    const severityColor = (s) => {
        if (!s) return 'var(--text-muted)';
        const sl = s.toLowerCase();
        if (sl === 'critical' || sl === 'high') return 'var(--accent-red)';
        if (sl === 'medium') return 'var(--accent-orange)';
        return 'var(--accent-green)';
    };

    return (
        <div className="va-page">
            <div className="va-header">
                <h2><span className="icon" style={{ fontSize: 20, marginRight: 8, verticalAlign: 'middle' }}>car_crash</span>AI Accident Video Analysis</h2>
                <div className="va-header-sub">
                    Upload a CCTV / dashcam video and the AI pipeline will detect accidents using YOLOv8 + Grok analysis.
                </div>
            </div>

            <div className="va-body">
                {/* Left — Upload + Preview */}
                <div className="va-left">
                    {/* Drop Zone */}
                    {!file && (
                        <div
                            className={`va-dropzone ${dragOver ? 'drag-over' : ''}`}
                            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                            onDragLeave={() => setDragOver(false)}
                            onDrop={onDrop}
                            onClick={() => inputRef.current?.click()}
                        >
                            <input
                                ref={inputRef}
                                type="file"
                                accept="video/mp4,video/avi,video/quicktime,video/x-matroska,.mp4,.avi,.mov,.mkv"
                                style={{ display: 'none' }}
                                onChange={(e) => handleFile(e.target.files[0])}
                            />
                            <span className="icon" style={{ fontSize: 56, color: 'var(--primary)', opacity: 0.5 }}>cloud_upload</span>
                            <div className="va-drop-text">Drop video here or click to browse</div>
                            <div className="va-drop-hint">Supports MP4, AVI, MOV, MKV • Max recommended: 100MB</div>
                        </div>
                    )}

                    {/* Video Preview */}
                    {file && (
                        <div className="va-preview-section">
                            <div className="va-preview-card">
                                {preview && (
                                    <video src={preview} controls className="va-video-preview" />
                                )}
                                <div className="va-file-info">
                                    <span className="icon" style={{ fontSize: 18, color: 'var(--primary)' }}>movie</span>
                                    <div>
                                        <div className="va-filename">{file.name}</div>
                                        <div className="va-filesize">{(file.size / (1024 * 1024)).toFixed(1)} MB</div>
                                    </div>
                                    <button className="va-remove-btn" onClick={reset} title="Remove">
                                        <span className="icon" style={{ fontSize: 16 }}>close</span>
                                    </button>
                                </div>
                            </div>

                            <div className="va-actions">
                                <button className="va-analyze-btn" onClick={upload} disabled={uploading}>
                                    {uploading ? (
                                        <><span className="icon va-spin" style={{ fontSize: 16 }}>autorenew</span> Analyzing...</>
                                    ) : (
                                        <><span className="icon" style={{ fontSize: 16 }}>play_arrow</span> Run Accident Analysis</>
                                    )}
                                </button>
                                <button className="va-reset-btn" onClick={reset} disabled={uploading}>
                                    <span className="icon" style={{ fontSize: 16 }}>restart_alt</span> Reset
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Progress */}
                    {progress && (
                        <div className="va-progress">
                            <div className="va-progress-bar"><div className="va-progress-fill"></div></div>
                            <span>{progress}</span>
                        </div>
                    )}

                    {/* Error */}
                    {error && (
                        <div className="va-error">
                            <span className="icon" style={{ fontSize: 16, color: 'var(--accent-red)' }}>error</span>
                            {error}
                        </div>
                    )}
                </div>

                {/* Right — Results */}
                <div className="va-right">
                    {!result && !uploading && (
                        <div className="va-empty-result">
                            <span className="icon" style={{ fontSize: 48, color: 'var(--text-muted)', opacity: 0.3 }}>analytics</span>
                            <div>Upload a video to see analysis results</div>
                        </div>
                    )}

                    {uploading && (
                        <div className="va-empty-result">
                            <span className="icon va-spin" style={{ fontSize: 48, color: 'var(--primary)' }}>autorenew</span>
                            <div>Running AI pipeline...</div>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                                YOLOv8 Detection → Grok Analysis → Report Generation
                            </div>
                        </div>
                    )}

                    {result && (
                        <div className="va-results">
                            {/* Detection Status */}
                            <div className={`va-result-banner ${result.accident_detected ? 'detected' : 'clear'}`}>
                                <span className="icon" style={{ fontSize: 28 }}>
                                    {result.accident_detected ? 'warning' : 'check_circle'}
                                </span>
                                <div>
                                    <div className="va-banner-title">
                                        {result.accident_detected ? 'ACCIDENT DETECTED' : 'NO ACCIDENT DETECTED'}
                                    </div>
                                    <div className="va-banner-sub">
                                        {result.accident_detected
                                            ? `${result.incident_type || 'Vehicle collision'} • Severity: ${result.severity || 'Unknown'}`
                                            : (result.message || 'The video shows no signs of accidents.')}
                                    </div>
                                </div>
                            </div>

                            {result.accident_detected && (
                                <>
                                    {/* Quick Stats */}
                                    <div className="va-stats-row">
                                        <div className="va-stat">
                                            <div className="va-stat-val" style={{ color: severityColor(result.severity) }}>
                                                {result.severity || '—'}
                                            </div>
                                            <div className="va-stat-label">Severity</div>
                                        </div>
                                        <div className="va-stat">
                                            <div className="va-stat-val">{result.report?.confidence ? `${(result.report.confidence * 100).toFixed(0)}%` : '—'}</div>
                                            <div className="va-stat-label">Confidence</div>
                                        </div>
                                        <div className="va-stat">
                                            <div className="va-stat-val">{result.report?.vehicle_count ?? result.vehicles?.length ?? '—'}</div>
                                            <div className="va-stat-label">Vehicles</div>
                                        </div>
                                        <div className="va-stat">
                                            <div className="va-stat-val">{result.report?.person_count ?? '—'}</div>
                                            <div className="va-stat-label">Persons</div>
                                        </div>
                                    </div>

                                    {/* Timestamp */}
                                    {result.timestamp && (
                                        <div className="va-detail-row">
                                            <span className="icon" style={{ fontSize: 14, color: 'var(--primary)' }}>schedule</span>
                                            <span>Incident at <strong>{result.timestamp}</strong></span>
                                        </div>
                                    )}

                                    {/* Emergency */}
                                    {result.report?.emergency_required && (
                                        <div className="va-emergency">
                                            <span className="icon" style={{ fontSize: 16 }}>local_hospital</span>
                                            EMERGENCY RESPONSE REQUIRED
                                        </div>
                                    )}

                                    {/* Detection Reason */}
                                    {result.report?.detection_reason && (
                                        <div className="va-section">
                                            <h4><span className="icon" style={{ fontSize: 14 }}>search</span> Detection Reason</h4>
                                            <p>{result.report.detection_reason}</p>
                                        </div>
                                    )}

                                    {/* AI Analysis */}
                                    {result.report?.report_text && (
                                        <div className="va-section">
                                            <h4><span className="icon" style={{ fontSize: 14 }}>smart_toy</span> Grok AI Analysis</h4>
                                            <p className="va-report-text">{result.report.report_text}</p>
                                        </div>
                                    )}

                                    {/* Vehicles */}
                                    {result.vehicles && result.vehicles.length > 0 && (
                                        <div className="va-section">
                                            <h4><span className="icon" style={{ fontSize: 14 }}>directions_car</span> Detected Vehicles</h4>
                                            <div className="va-vehicles">
                                                {result.vehicles.map((v, i) => (
                                                    <div key={i} className="va-vehicle-chip">
                                                        {v.label || v.type || v} {v.confidence ? `(${(v.confidence * 100).toFixed(0)}%)` : ''}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
