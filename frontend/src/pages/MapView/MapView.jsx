import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// map used from https://leafletjs.com/examples/custom-icons/ with custom styling for live/alert status and popups showing feed preview and details. The CAMS array is hardcoded for demo purposes but can be fetched from an API in a real application.

const CAMS = [
    { id: 'CAM-01', name: 'LIVE CAMERA', status: 'live', lat: 19.0440, lng: 73.0290 },
    { id: 'CAM-02', name: 'MARKET - PANVEL', status: 'alert', lat: 18.991296, lng: 73.115834 },
    { id: 'CAM-03', name: 'BUS STOP South Mumbai', status: 'live', lat: 19.062412, lng: 72.860005 },
    { id: 'CAM-04', name: 'EASTERN EXPRESSWAY EXIT', status: 'live', lat: 19.087513, lng: 72.923585 },
    { id: 'CAM-05', name: 'PANVEL HIGHWAY', status: 'live', lat: 19.036500, lng: 73.079851 },
    { id: 'CAM-06', name: 'WORLI BRIDGE', status: 'live', lat: 19.0490, lng: 72.827274 },
];
export default function MapView({ onNavigate }) {
    const mapRef = useRef(null);
    const mapInst = useRef(null);

    useEffect(() => {
        window.__mapNavToLive = () => onNavigate && onNavigate('live');
        return () => { delete window.__mapNavToLive; };
    }, [onNavigate]);

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
                    width: 22px; height: 22px; border-radius: 50%;
                    background: ${color}33; border: 2px solid ${color};
                    display: flex; align-items: center; justify-content: center;
                    box-shadow: 0 0 16px ${color}80;
                "><div style="width: 8px; height: 8px; border-radius: 50%; background: ${color};"></div></div>`,
                iconSize: [22, 22],
                iconAnchor: [11, 11],
            });

            const marker = L.marker([cam.lat, cam.lng], { icon }).addTo(map);
            marker.bindPopup(`
                <div style="background:#0f172a; color:#f1f5f9; padding:0; border-radius:10px; border:1px solid rgba(255,255,255,0.1); font-family:'Space Grotesk',sans-serif; min-width:240px; overflow:hidden;">
                    <div style="position:relative; width:100%; height:135px; overflow:hidden; background:#000;">
                        <img src="/api/feed/${cam.id}" alt="${cam.name}" style="width:100%; height:100%; object-fit:cover; opacity:0.85;" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
                        <div style="display:none; width:100%; height:100%; align-items:center; justify-content:center; background:#0c1120; color:#475569; font-size:11px;">No Feed Available</div>
                        <div style="position:absolute; top:8px; left:8px; background:${isAlert ? 'rgba(255,59,48,0.8)' : 'rgba(52,211,153,0.8)'}; color:#fff; font-size:8px; font-weight:800; padding:2px 8px; border-radius:4px; text-transform:uppercase; letter-spacing:0.05em;">${isAlert ? '⚠ ALERT' : '● LIVE'}</div>
                    </div>
                    <div style="padding:10px 14px;">
                        <div style="font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.1em; color:${color}; margin-bottom:4px;">${cam.id}</div>
                        <div style="font-size:13px; font-weight:600;">${cam.name}</div>
                        <div style="font-size:10px; color:#94a3b8; margin-top:4px;">${isAlert ? '⚠ ACTIVE INCIDENT' : '● OPERATIONAL'}</div>
                        <div style="font-size:9px; color:#64748b; margin-top:2px;">LAT: ${cam.lat.toFixed(4)} | LNG: ${cam.lng.toFixed(4)}</div>
                        <div style="margin-top:10px; display:flex; gap:8px;">
                            <a href="#" onclick="window.__mapNavToLive && window.__mapNavToLive(); return false;" style="flex:1; display:block; text-align:center; background:rgba(13,127,242,0.15); color:#0d7ff2; font-size:10px; font-weight:700; padding:6px 0; border-radius:6px; border:1px solid rgba(13,127,242,0.3); text-decoration:none; text-transform:uppercase; letter-spacing:0.05em;">View Feed</a>
                        </div>
                    </div>
                </div>
            `, { className: 'dark-popup', closeButton: false, maxWidth: 260 });

            if (isAlert) {
                L.circle([cam.lat, cam.lng], {
                    radius: 100,
                    color: '#ff3b30',
                    fillColor: '#ff3b30',
                    fillOpacity: 0.08,
                    weight: 1,
                    opacity: 0.4,
                }).addTo(map);
            }
        });

        L.control.zoom({ position: 'bottomright' }).addTo(map);
        mapInst.current = map;

        return () => { map.remove(); mapInst.current = null; };
    }, []);

    return (
        <div className="map-fullpage">
            <div className="map-fullpage-header">
                <h2>Incident Map — Operational Area</h2>
                <div className="map-stats">
                    <span className="map-stat"><span className="dot-live"></span> {CAMS.filter(c => c.status === 'live').length} Operational</span>
                    <span className="map-stat"><span className="dot-alert"></span> {CAMS.filter(c => c.status === 'alert').length} Alert</span>
                    <span className="map-stat-total">{CAMS.length} Total Nodes</span>
                </div>
            </div>
            <div ref={mapRef} style={{ flex: 1, borderRadius: 12, overflow: 'hidden' }}></div>
        </div>
    );
}
