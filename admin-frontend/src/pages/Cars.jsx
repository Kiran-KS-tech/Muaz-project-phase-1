import React, { useState, useEffect } from 'react';
import { Search, Plus, Car as CarIcon, AlertCircle, Wrench, RefreshCw, UserCheck, X } from 'lucide-react';
import api, { mockData } from '../services/api';

export default function Cars() {
  const [cars, setCars] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [search, setSearch] = useState('');
  const [fuelFilter, setFuelFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [loading, setLoading] = useState(false);

  // Assignment Modal State
  const [activeCarForAssign, setActiveCarForAssign] = useState(null);
  const [selectedDriverId, setSelectedDriverId] = useState('');

  // Service Log Modal State
  const [activeCarForService, setActiveCarForService] = useState(null);
  const [serviceForm, setServiceForm] = useState({
    service_date: new Date().toISOString().split('T')[0],
    description: '', cost: '', mileage_at_service: '', performed_by: ''
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const carRes = await api.get('/api/v1/cars/');
      const driverRes = await api.get('/api/v1/drivers/');
      setCars(carRes.data?.results || carRes.data || []);
      setDrivers(driverRes.data?.results || driverRes.data || []);
    } catch (e) {
      setCars(mockData.cars);
      setDrivers(mockData.drivers);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAssignDriver = async (e) => {
    e.preventDefault();
    if (!activeCarForAssign) return;

    try {
      await api.post(`/api/v1/cars/${activeCarForAssign.id}/assign_driver/`, { driver_id: selectedDriverId });
      loadData();
    } catch (err) {
      // Mock assignment
      const driverObj = drivers.find(d => d.id.toString() === selectedDriverId);
      setCars(cars.map(c => c.id === activeCarForAssign.id ? { 
        ...c, 
        driver_name: driverObj ? driverObj.name : 'None',
        driver_assignment: driverObj ? driverObj.id : null 
      } : c));
      alert(`Demo Mode: Assigned ${driverObj ? driverObj.name : 'None'} to vehicle.`);
    } finally {
      setActiveCarForAssign(null);
      setSelectedDriverId('');
    }
  };

  const handleLogService = async (e) => {
    e.preventDefault();
    if (!activeCarForService) return;

    try {
      await api.post('/api/v1/cars/records/', {
        car: activeCarForService.id,
        ...serviceForm
      });
      alert("Service history logged successfully.");
    } catch (err) {
      alert(`Demo Mode: Logged service record for ${activeCarForService.registration_number}`);
    } finally {
      setActiveCarForService(null);
      setServiceForm({ service_date: new Date().toISOString().split('T')[0], description: '', cost: '', mileage_at_service: '', performed_by: '' });
    }
  };

  const filteredCars = cars.filter(c => {
    const matchesSearch = c.registration_number.toLowerCase().includes(search.toLowerCase()) ||
                          c.brand.toLowerCase().includes(search.toLowerCase()) ||
                          c.model.toLowerCase().includes(search.toLowerCase());
    const matchesFuel = fuelFilter === 'ALL' || c.fuel_type === fuelFilter;
    const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter;
    return matchesSearch && matchesFuel && matchesStatus;
  });

  return (
    <div className="space-y-6 animate-slide-in">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Vehicle Management</h1>
          <p className="text-slate-400 text-sm">Monitor fleet inventory, assignments, and service scheduling</p>
        </div>
        <button
          onClick={loadData}
          className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700/60 rounded-xl transition-colors flex items-center gap-2 text-sm font-semibold cursor-pointer"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Sync Fleet</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-3 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full glass-input rounded-xl py-2.5 pl-11 pr-4 text-sm"
            placeholder="Search by reg number, brand, model..."
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {/* Fuel types */}
          <select
            value={fuelFilter}
            onChange={(e) => setFuelFilter(e.target.value)}
            className="glass-input rounded-xl py-2 px-4 text-xs font-semibold"
          >
            <option value="ALL">All Fuel Types</option>
            <option value="CNG">CNG</option>
            <option value="PETROL">Petrol</option>
            <option value="DIESEL">Diesel</option>
            <option value="ELECTRIC">Electric</option>
          </select>
          {/* Status types */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="glass-input rounded-xl py-2 px-4 text-xs font-semibold"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="MAINTENANCE">Maintenance</option>
            <option value="OUT_OF_SERVICE">Out of Service</option>
          </select>
        </div>
      </div>

      {/* Grid List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCars.map((car) => (
          <div key={car.id} className="glass-panel rounded-3xl p-6 flex flex-col justify-between space-y-4 hover:border-slate-700 transition-all duration-200">
            {/* Header info */}
            <div className="flex justify-between items-start">
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-500">{car.brand}</span>
                <h3 className="text-lg font-bold text-white leading-tight">{car.model}</h3>
                <span className="inline-block mt-1.5 px-2.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono font-bold text-slate-300">
                  {car.registration_number}
                </span>
              </div>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase ${
                car.status === 'ACTIVE'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : car.status === 'MAINTENANCE'
                  ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  : 'bg-red-500/10 text-red-400 border border-red-500/20'
              }`}>
                {car.status}
              </span>
            </div>

            {/* Middle metadata */}
            <div className="space-y-2.5 py-2.5 border-t border-b border-slate-800/80 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500 font-semibold">Assigned Driver:</span>
                <span className="font-bold text-slate-200">{car.driver_name || 'Unassigned'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-semibold">Fuel System:</span>
                <span className="font-bold text-indigo-400">{car.fuel_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-semibold">Permit Expiry:</span>
                <span className={`font-mono ${new Date(car.permit_expiry) < new Date() ? 'text-red-400 font-bold' : 'text-slate-300'}`}>
                  {car.permit_expiry}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-semibold">Insurance Expiry:</span>
                <span className="font-mono text-slate-300">{car.insurance_expiry}</span>
              </div>
            </div>

            {/* Actions */}
            <div className="grid grid-cols-2 gap-2 pt-2">
              <button
                onClick={() => {
                  setActiveCarForAssign(car);
                  setSelectedDriverId(car.driver_assignment?.toString() || '');
                }}
                className="py-2.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl border border-slate-700/60 transition-colors flex items-center justify-center gap-1.5 text-xs font-semibold cursor-pointer"
              >
                <UserCheck className="w-3.5 h-3.5" />
                <span>Assign Driver</span>
              </button>
              <button
                onClick={() => setActiveCarForService(car)}
                className="py-2.5 px-3 bg-indigo-600/20 hover:bg-indigo-600 text-indigo-400 hover:text-white border border-indigo-500/20 hover:border-transparent rounded-xl transition-all flex items-center justify-center gap-1.5 text-xs font-semibold cursor-pointer"
              >
                <Wrench className="w-3.5 h-3.5" />
                <span>Log Service</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Driver Assignment Modal */}
      {activeCarForAssign && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setActiveCarForAssign(null)} />
          <div className="relative w-full max-w-md bg-[#0b1329] border border-slate-800 rounded-3xl p-6 shadow-2xl animate-slide-in">
            <h3 className="text-lg font-bold text-white mb-4">Assign Driver to {activeCarForAssign.registration_number}</h3>
            <form onSubmit={handleAssignDriver} className="space-y-4">
              <div>
                <label className="block text-slate-400 text-xs font-semibold mb-2">Select Driver</label>
                <select
                  value={selectedDriverId}
                  onChange={(e) => setSelectedDriverId(e.target.value)}
                  className="w-full glass-input rounded-xl py-3 px-4 text-sm"
                >
                  <option value="">Unassign / None</option>
                  {drivers.map(d => (
                    <option key={d.id} value={d.id}>{d.name} ({d.driver_id})</option>
                  ))}
                </select>
              </div>
              <div className="flex gap-2 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setActiveCarForAssign(null)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs font-semibold cursor-pointer border border-slate-700/60"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/10 cursor-pointer"
                >
                  Confirm Allocation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Service Record Log Modal */}
      {activeCarForService && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setActiveCarForService(null)} />
          <div className="relative w-full max-w-md bg-[#0b1329] border border-slate-800 rounded-3xl p-6 shadow-2xl animate-slide-in">
            <button
              onClick={() => setActiveCarForService(null)}
              className="absolute top-4 right-4 p-2 rounded-lg bg-slate-800 text-slate-400"
            >
              <X className="w-4 h-4" />
            </button>
            <h3 className="text-lg font-bold text-white mb-4">Log Service: {activeCarForService.registration_number}</h3>
            <form onSubmit={handleLogService} className="space-y-4">
              <div>
                <label className="block text-slate-400 text-xs font-semibold mb-1.5">Service Date</label>
                <input
                  type="date"
                  required
                  value={serviceForm.service_date}
                  onChange={(e) => setServiceForm({ ...serviceForm, service_date: e.target.value })}
                  className="w-full glass-input rounded-xl py-2.5 px-4 text-sm"
                />
              </div>
              <div>
                <label className="block text-slate-400 text-xs font-semibold mb-1.5">Description</label>
                <input
                  type="text"
                  required
                  value={serviceForm.description}
                  onChange={(e) => setServiceForm({ ...serviceForm, description: e.target.value })}
                  className="w-full glass-input rounded-xl py-2.5 px-4 text-sm"
                  placeholder="e.g. Engine Oil, Air filter change"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-400 text-xs font-semibold mb-1.5">Cost (₹)</label>
                  <input
                    type="number"
                    required
                    value={serviceForm.cost}
                    onChange={(e) => setServiceForm({ ...serviceForm, cost: e.target.value })}
                    className="w-full glass-input rounded-xl py-2.5 px-4 text-sm"
                    placeholder="₹4,500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 text-xs font-semibold mb-1.5">Mileage (km)</label>
                  <input
                    type="number"
                    value={serviceForm.mileage_at_service}
                    onChange={(e) => setServiceForm({ ...serviceForm, mileage_at_service: e.target.value })}
                    className="w-full glass-input rounded-xl py-2.5 px-4 text-sm"
                    placeholder="e.g. 45000"
                  />
                </div>
              </div>
              <div>
                <label className="block text-slate-400 text-xs font-semibold mb-1.5">Workshop Name</label>
                <input
                  type="text"
                  value={serviceForm.performed_by}
                  onChange={(e) => setServiceForm({ ...serviceForm, performed_by: e.target.value })}
                  className="w-full glass-input rounded-xl py-2.5 px-4 text-sm"
                  placeholder="e.g. Maruti Service Point"
                />
              </div>
              <button
                type="submit"
                className="w-full py-3 bg-indigo-600 hover:bg-indigo-505 text-white rounded-xl text-sm font-semibold shadow-lg shadow-indigo-600/20 cursor-pointer"
              >
                Save Record
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
