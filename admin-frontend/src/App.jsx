import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { LayoutDashboard, Users, Car, CreditCard, LogOut, ShieldAlert, Bell, Menu, X, User } from 'lucide-react';

// Import Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Drivers from './pages/Drivers';
import Cars from './pages/Cars';
import Settlements from './pages/Settlements';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('mock_user');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

// Main Layout Component
const AppLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userEmail, setUserEmail] = useState('admin@fleetmanage.com');
  const [userRole, setUserRole] = useState('SUPER_ADMIN');

  useEffect(() => {
    const mockEmail = localStorage.getItem('mock_user_email') || 'admin@fleetmanage.com';
    const mockRole = localStorage.getItem('mock_user_role') || 'Super Admin';
    setUserEmail(mockEmail);
    setUserRole(mockRole);
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const navLinks = [
    { to: '/', name: 'Dashboard', icon: LayoutDashboard },
    { to: '/drivers', name: 'Drivers', icon: Users },
    { to: '/cars', name: 'Vehicles', icon: Car },
    { to: '/settlements', name: 'Settlements', icon: CreditCard },
  ];

  return (
    <div className="flex h-screen bg-[#0b1329] overflow-hidden text-slate-200">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex flex-col w-64 glass-panel border-r border-slate-800">
        {/* Brand */}
        <div className="h-20 flex items-center px-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🚖</span>
            <div>
              <h1 className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
                FleetManager
              </h1>
              <p className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">Control Panel</p>
            </div>
          </div>
        </div>

        {/* User Card */}
        <div className="p-4 border-b border-slate-800/60 bg-slate-900/40">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
              {userEmail.charAt(0).toUpperCase()}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-semibold truncate">{userEmail}</p>
              <span className="inline-block px-2 py-0.5 mt-0.5 text-[9px] font-extrabold text-indigo-300 bg-indigo-500/10 border border-indigo-500/20 rounded-full uppercase">
                {userRole}
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          {navLinks.map((link) => {
            const IconComponent = link.icon;
            const isActive = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600/30 to-purple-600/10 text-white font-medium border-l-4 border-indigo-500 pl-3'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/40'
                }`}
              >
                <IconComponent className={`w-5 h-5 transition-transform duration-200 group-hover:scale-105 ${isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-300'}`} />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Logout Trigger */}
        <div className="p-4 border-t border-slate-800">
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 px-4 py-3 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-colors duration-200"
          >
            <LogOut className="w-5 h-5" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
          <aside className="relative flex flex-col w-72 max-w-xs bg-[#0b1329] border-r border-slate-800 h-full p-6 animate-slide-in">
            <button
              onClick={() => setMobileMenuOpen(false)}
              className="absolute top-4 right-4 p-2 rounded-lg bg-slate-800 text-slate-400"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-3 mb-8">
              <span className="text-3xl">🚖</span>
              <h1 className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                FleetManager
              </h1>
            </div>
            <nav className="flex-1 space-y-2">
              {navLinks.map((link) => {
                const IconComponent = link.icon;
                const isActive = location.pathname === link.to;
                return (
                  <Link
                    key={link.to}
                    to={link.to}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl ${
                      isActive ? 'bg-indigo-600/20 text-white border-l-4 border-indigo-500' : 'text-slate-400'
                    }`}
                  >
                    <IconComponent className="w-5 h-5" />
                    <span>{link.name}</span>
                  </Link>
                );
              })}
            </nav>
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-3 px-4 py-3 text-slate-400 hover:text-red-400 mt-auto border-t border-slate-800 pt-4"
            >
              <LogOut className="w-5 h-5" />
              <span>Sign Out</span>
            </button>
          </aside>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-20 flex items-center justify-between px-6 md:px-8 border-b border-slate-800/80 glass-panel">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="md:hidden p-2 rounded-lg bg-slate-800 text-slate-300"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <h2 className="text-lg font-bold text-white capitalize">
                {location.pathname === '/' ? 'Dashboard' : location.pathname.substring(1)}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Notification Badge */}
            <div className="relative p-2 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors border border-slate-700/50 cursor-pointer">
              <Bell className="w-5 h-5 text-slate-300" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-indigo-500 ring-2 ring-slate-900" />
            </div>

            {/* User status */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>Mock-API Mode</span>
            </div>
          </div>
        </header>

        {/* Page Content Router Container */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#0b1329]">
          {children}
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <AppLayout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/drivers" element={<Drivers />} />
                  <Route path="/cars" element={<Cars />} />
                  <Route path="/settlements" element={<Settlements />} />
                </Routes>
              </AppLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}
