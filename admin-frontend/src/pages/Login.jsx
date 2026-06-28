import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, LogIn, AlertCircle } from 'lucide-react';
import api from '../services/api';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Attempt API log-in
      const response = await api.post('/api/v1/accounts/login/', { email, password });
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('mock_user_email', response.data.user.email);
      localStorage.setItem('mock_user_role', response.data.user.role);
      navigate('/');
    } catch (apiError) {
      // Fallback: If local API fails or isn't running, check for demo credentials
      if (email === 'admin@fleetmanage.com' && password === 'adminpassword123') {
        localStorage.setItem('mock_user', 'true');
        localStorage.setItem('mock_user_email', 'admin@fleetmanage.com');
        localStorage.setItem('mock_user_role', 'Super Admin');
        navigate('/');
      } else {
        setError(apiError.response?.data?.non_field_errors?.[0] || 'Authentication failed. Use demo login for offline preview.');
      }
    } finally {
      setLoading(false);
    }
  };

  const triggerDemoLogin = () => {
    localStorage.setItem('mock_user', 'true');
    localStorage.setItem('mock_user_email', 'demo@fleetmanage.com');
    localStorage.setItem('mock_user_role', 'Fleet Owner');
    navigate('/');
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[#0b1329] overflow-hidden p-6">
      {/* Background gradients */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-indigo-500/10 blur-[80px]" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full bg-purple-500/10 blur-[80px]" />

      <div className="w-full max-w-md animate-slide-in">
        {/* Logo Header */}
        <div className="text-center mb-8">
          <span className="text-5xl inline-block mb-3 drop-shadow-[0_10px_10px_rgba(59,130,246,0.3)]">🚖</span>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
            FleetManager Admin
          </h1>
          <p className="text-slate-400 text-sm mt-2">Manage your fleet, settlements & drivers in real-time</p>
        </div>

        {/* Card */}
        <div className="glass-panel rounded-3xl p-8 shadow-2xl relative border border-slate-800">
          <h2 className="text-xl font-bold text-white mb-6">Sign In</h2>
          
          {error && (
            <div className="flex items-center gap-2 p-3 mb-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-slate-300 text-xs font-semibold uppercase tracking-wider mb-1.5">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3 w-5 h-5 text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full glass-input rounded-xl py-3 pl-11 pr-4 text-sm"
                  placeholder="name@company.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-300 text-xs font-semibold uppercase tracking-wider mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-3 w-5 h-5 text-slate-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full glass-input rounded-xl py-3 pl-11 pr-4 text-sm"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 mt-2 rounded-xl font-semibold bg-gradient-to-r from-indigo-500 via-indigo-600 to-purple-600 hover:opacity-90 active:scale-[0.99] text-white shadow-lg shadow-indigo-500/20 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  <span>Authenticate</span>
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center my-6">
            <div className="flex-1 border-t border-slate-800" />
            <span className="text-[10px] uppercase font-bold text-slate-500 px-3 tracking-wider">Preview Environment</span>
            <div className="flex-1 border-t border-slate-800" />
          </div>

          {/* Quick Demo Bypass */}
          <div className="space-y-2.5">
            <button
              onClick={triggerDemoLogin}
              className="w-full py-3 rounded-xl border border-slate-700/60 hover:border-indigo-500/40 hover:bg-indigo-500/5 text-slate-300 hover:text-indigo-400 font-medium text-sm transition-all duration-200 cursor-pointer"
            >
              Access with Offline Mock Data
            </button>
            <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-xl text-[11px] text-slate-500 leading-normal">
              <span className="font-bold text-slate-400">Demo Credentials (Live Mode):</span><br />
              Email: <code className="text-indigo-300">admin@fleetmanage.com</code><br />
              Password: <code className="text-indigo-300">adminpassword123</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
