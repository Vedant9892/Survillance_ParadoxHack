import { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './pages/Dashboard/Dashboard.jsx';
import LiveFeed from './pages/LiveFeed/LiveFeed.jsx';
import Incidents from './pages/Incidents/Incidents.jsx';
import MapView from './pages/MapView/MapView.jsx';
import Agents from './pages/Agents/Agents.jsx';
import Alerts from './pages/Alerts/Alerts.jsx';
import VideoAnalysis from './pages/VideoAnalysis/VideoAnalysis.jsx';

const PAGES = ['dashboard', 'live', 'incidents', 'map', 'agents', 'alerts', 'video'];
const NAV_ITEMS = [
    { id: 'dashboard', icon: 'dashboard', label: 'Dashboard' },
    { id: 'live', icon: 'videocam', label: 'Live Feed' },
    { id: 'video', icon: 'car_crash', label: 'Video Analysis' },
    { id: 'incidents', icon: 'article', label: 'Incidents' },
    { id: 'map', icon: 'map', label: 'Map' },
    { id: 'agents', icon: 'memory', label: 'Agents' },
    { id: 'alerts', icon: 'warning', label: 'Alerts' },
];

function App() {
    const [page, setPage] = useState('dashboard');
    const [time, setTime] = useState('');
    const [incidents, setIncidents] = useState([]);
    const [status, setStatus] = useState(null);

    // Live clock
    useEffect(() => {
        const tick = () => {
            const d = new Date();
            setTime(d.toLocaleTimeString('en-GB') + ' | ' + d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).toUpperCase());
        };
        tick();
        const id = setInterval(tick, 1000);
        return () => clearInterval(id);
    }, []);

    // Poll incidents
    useEffect(() => {
        const poll = () => {
            fetch('/api/incidents').then(r => r.json()).then(setIncidents).catch(() => { });
            fetch('/api/status').then(r => r.json()).then(setStatus).catch(() => { });
        };
        poll();
        const id = setInterval(poll, 3000);
        return () => clearInterval(id);
    }, []);

    return (
        <div className="shell">
            {/* ── Top Bar ─────────────────────────── */}
            <header className="topbar">
                <div className="topbar-brand">
                    <div className="logo">
                        <span className="icon">shield_person</span>
                        <h1>SASV</h1>
                    </div>
                    <div className="topbar-status">
                        <span className="dot"></span>
                        SYSTEM ONLINE
                    </div>
                    <div className="topbar-time">{time}</div>
                </div>
                <div className="topbar-right">
                    <div className="net-status">
                        <span><span className="net-dot" style={{ background: 'var(--accent-green)' }}></span>NETWORK: STABLE</span>
                        <span><span className="net-dot" style={{ background: 'var(--primary)' }}></span>AI: SYNCHRONIZED</span>
                    </div>
                    <button className="bell-btn">
                        <span className="icon" style={{ fontSize: 20 }}>notifications</span>
                        {incidents.length > 0 && <span className="badge"></span>}
                    </button>
                    <div className="topbar-user">
                        <div>
                            <div className="uname">Vedant</div>
                            <div className="urole">Director of Ops</div>
                        </div>
                        <div className="uavatar"></div>
                    </div>
                </div>
            </header>

            {/* ── Body ────────────────────────────── */}
            <div className="body-layout">
                {/* Sidebar */}
                <aside className="sidebar">
                    <nav>
                        {NAV_ITEMS.map(n => (
                            <a key={n.id} className={page === n.id ? 'active' : ''} onClick={() => PAGES.includes(n.id) && setPage(n.id)}>
                                <span className="icon">{n.icon}</span>
                            </a>
                        ))}
                    </nav>
                    <div className="spacer"></div>
                    <button><span className="icon">settings</span></button>
                </aside>

                {/* Main */}
                <div className="main-area">
                    {page === 'dashboard' && <Dashboard incidents={incidents} status={status} onNavigate={setPage} />}
                    {page === 'live' && <LiveFeed incidents={incidents} status={status} />}
                    {page === 'video' && <VideoAnalysis />}
                    {page === 'incidents' && <Incidents incidents={incidents} />}
                    {page === 'map' && <MapView onNavigate={setPage} />}
                    {page === 'agents' && <Agents status={status} />}
                    {page === 'alerts' && <Alerts incidents={incidents} />}
                </div>
            </div>
        </div>
    );
}

export default App;
