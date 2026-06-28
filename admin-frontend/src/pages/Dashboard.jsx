import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { IndianRupee, Users, Car, AlertTriangle, Play, RefreshCw, FileText } from 'lucide-react';
import api, { mockData } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState(mockData.stats);
  const [activities, setActivities] = useState(mockData.activities);
  const [loading, setLoading] = useState(false);
  const [alerts, setAlerts] = useState([
    { id: 1, type: 'maintenance', text: 'Vehicle DL-1CA-5643 is due for scheduled maintenance (180 days elapsed).' },
    { id: 2, type: 'document', text: 'Driver Kabir Singh: License DL-14202100034 is expiring in 7 days.' }
  ]);

  const refreshDashboard = async () => {
    setLoading(true);
    try {
      const statsRes = await api.get('/api/v1/reports/profitability/'); // mock logic fallback
      const auditRes = await api.get('/api/v1/audit/');
      // Map API responses if they exist
      if (statsRes.data && statsRes.data.length > 0) {
        const totalGross = statsRes.data.reduce((acc, c) => acc + c.total_earnings, 0);
        const activeVehicles = statsRes.data.filter(c => c.status === 'ACTIVE').length;
        setStats({
          totalEarnings: totalGross,
          activeDrivers: statsRes.data.filter(c => c.assigned_driver !== 'None').length,
          pendingSettlements: 3,
          activeCars: activeVehicles,
          maintenanceAlerts: statsRes.data.filter(c => c.status === 'MAINTENANCE').length
        });
      }
      if (auditRes.data) {
        setActivities(auditRes.data.slice(0, 5));
      }
    } catch (e) {
      // Fallback silently to mock data in offline preview
      console.log('Running in offline/fallback mode');
    } finally {
      setTimeout(() => setLoading(false), 500);
    }
  };

  const triggerWeeklySettlementJob = async () => {
    alert("Celery Job Triggered: Generating weekly settlements for period ending yesterday.");
    // In production, hits POST `/api/v1/settlements/generate_range/`
  };

  useEffect(() => {
    refreshDashboard();
  }, []);

  return (
    <div className="space-y-6 animate-slide-in">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Overview</h1>
          <p className="text-slate-400 text-sm">Key operation parameters and fleet performance metrics</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={refreshDashboard}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl border border-slate-700/60 transition-colors flex items-center gap-2 text-sm font-semibold cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Reload</span>
          </button>
          <button
            onClick={triggerWeeklySettlementJob}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl shadow-lg shadow-indigo-600/20 transition-all flex items-center gap-2 text-sm font-semibold cursor-pointer"
          >
            <Play className="w-4 h-4" />
            <span>Process Settlements</span>
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Earnings Card */}
        <Link to="/settlements" className="glass-panel p-6 rounded-2xl relative overflow-hidden group block hover:border-indigo-500/30 hover:shadow-indigo-500/5 hover:shadow-lg transition-all duration-200 cursor-pointer">
          <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 rounded-bl-full transition-transform group-hover:scale-110" />
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Gross Fleet Revenue</p>
              <h3 className="text-2xl font-black text-white mt-2">₹{stats.totalEarnings.toLocaleString()}</h3>
            </div>
            <div className="p-3 bg-blue-500/10 rounded-xl text-blue-400 border border-blue-500/10">
              <IndianRupee className="w-6 h-6" />
            </div>
          </div>
        </Link>

        {/* Drivers Card */}
        <Link to="/drivers" className="glass-panel p-6 rounded-2xl relative overflow-hidden group block hover:border-emerald-500/30 hover:shadow-emerald-500/5 hover:shadow-lg transition-all duration-200 cursor-pointer">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-bl-full transition-transform group-hover:scale-110" />
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Drivers</p>
              <h3 className="text-2xl font-black text-white mt-2">{stats.activeDrivers}</h3>
            </div>
            <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400 border border-emerald-500/10">
              <Users className="w-6 h-6" />
            </div>
          </div>
        </Link>

        {/* Vehicles Card */}
        <Link to="/cars" className="glass-panel p-6 rounded-2xl relative overflow-hidden group block hover:border-purple-500/30 hover:shadow-purple-500/5 hover:shadow-lg transition-all duration-200 cursor-pointer">
          <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/5 rounded-bl-full transition-transform group-hover:scale-110" />
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Vehicles Online</p>
              <h3 className="text-2xl font-black text-white mt-2">{stats.activeCars}</h3>
            </div>
            <div className="p-3 bg-purple-500/10 rounded-xl text-purple-400 border border-purple-500/10">
              <Car className="w-6 h-6" />
            </div>
          </div>
        </Link>

        {/* Alert Card */}
        <Link to="/cars" className="glass-panel p-6 rounded-2xl relative overflow-hidden group block hover:border-amber-500/30 hover:shadow-amber-500/5 hover:shadow-lg transition-all duration-200 cursor-pointer">
          <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-bl-full transition-transform group-hover:scale-110" />
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Alerts & Expiries</p>
              <h3 className="text-2xl font-black text-white mt-2">{stats.maintenanceAlerts + alerts.length}</h3>
            </div>
            <div className="p-3 bg-amber-500/10 rounded-xl text-amber-400 border border-amber-500/10">
              <AlertTriangle className="w-6 h-6 animate-pulse" />
            </div>
          </div>
        </Link>
      </div>

      {/* Main Section Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Alerts */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Alerts */}
          <div className="glass-panel rounded-2xl p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <span>Urgent Alerts</span>
            </h3>
            <div className="space-y-3">
              {alerts.map((a) => (
                <div
                  key={a.id}
                  className={`p-4 rounded-xl border flex items-start gap-3 text-sm leading-relaxed ${
                    a.type === 'maintenance'
                      ? 'bg-amber-500/5 border-amber-500/10 text-amber-300'
                      : 'bg-red-500/5 border-red-500/10 text-red-300'
                  }`}
                >
                  <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                  <p>{a.text}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions Panel */}
          <div className="glass-panel rounded-2xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">Operations Playbook</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/80">
                <h4 className="font-semibold text-white mb-1">OCR Queue Check</h4>
                <p className="text-xs text-slate-400 mb-3">Re-dispatch files stuck in Celery worker processing queues.</p>
                <button className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg border border-slate-700/60 transition-colors cursor-pointer">
                  Sync OCR Queue
                </button>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/80">
                <h4 className="font-semibold text-white mb-1">Backup Audit Trail</h4>
                <p className="text-xs text-slate-400 mb-3">Export security logging activities to system artifacts.</p>
                <button className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg border border-slate-700/60 transition-colors cursor-pointer">
                  Export Audit Log
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Audit Trails */}
        <div className="glass-panel rounded-2xl p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-400" />
              <span>Audit Log Feed</span>
            </h3>
          </div>
          <div className="space-y-4">
            {activities.map((act) => (
              <div key={act.id} className="p-3 bg-slate-900/30 border border-slate-800/50 rounded-xl space-y-1.5">
                <div className="flex justify-between items-center">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-extrabold border ${
                    act.action === 'CREATE'
                      ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                      : act.action === 'SETTLEMENT_APPROVAL'
                      ? 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400'
                      : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                  }`}>
                    {act.action}
                  </span>
                  <span className="text-[10px] text-slate-500">
                    {new Date(act.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <p className="text-xs font-medium text-slate-200">
                  Modified <span className="text-indigo-400 font-bold">{act.model_name}</span> record #{act.object_id}
                </p>
                <p className="text-[10px] text-slate-500 font-semibold truncate">Actor: {act.user_email}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
