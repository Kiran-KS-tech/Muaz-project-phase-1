import React, { useState, useEffect } from 'react';
import { IndianRupee, FileCheck, CheckCircle2, ShieldAlert, Sliders, Calendar, X } from 'lucide-react';
import api, { mockData } from '../services/api';

export default function Settlements() {
  const [settlements, setSettlements] = useState([]);
  const [loading, setLoading] = useState(false);
  const [driverFilter, setDriverFilter] = useState('ALL');

  // Adjustments Modal State
  const [activeSetForAdjust, setActiveSetForAdjust] = useState(null);
  const [adjustForm, setAdjustForm] = useState({ manual_adjustment: '', manual_adjustment_reason: '' });

  // Payment Confirmation Modal State
  const [activeSetForPay, setActiveSetForPay] = useState(null);
  const [paymentRef, setPaymentRef] = useState('');

  // Custom Generator State
  const [genRange, setGenRange] = useState({ start_date: '', end_date: '' });

  const loadSettlements = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/settlements/');
      setSettlements(response.data?.results || response.data || []);
    } catch (e) {
      setSettlements(mockData.settlements);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettlements();
  }, []);

  const handleApprove = async (id) => {
    try {
      await api.post(`/api/v1/settlements/${id}/approve/`);
      loadSettlements();
    } catch (err) {
      setSettlements(settlements.map(s => s.id === id ? { ...s, status: 'APPROVED' } : s));
      alert("Demo Mode: Approved settlement.");
    }
  };

  const handleAdjust = async (e) => {
    e.preventDefault();
    if (!activeSetForAdjust) return;

    try {
      await api.post(`/api/v1/settlements/${activeSetForAdjust.id}/adjust/`, adjustForm);
      loadSettlements();
    } catch (err) {
      // Mock adjustment update
      const adj = parseFloat(adjustForm.manual_adjustment);
      setSettlements(settlements.map(s => s.id === activeSetForAdjust.id ? {
        ...s,
        manual_adjustment: adj,
        manual_adjustment_reason: adjustForm.manual_adjustment_reason,
        final_settlement_amount: s.net_amount ? (s.net_amount + adj) : (s.final_settlement_amount + adj)
      } : s));
      alert(`Demo Mode: Applied adjustment of ₹${adj}`);
    } finally {
      setActiveSetForAdjust(null);
      setAdjustForm({ manual_adjustment: '', manual_adjustment_reason: '' });
    }
  };

  const handlePay = async (e) => {
    e.preventDefault();
    if (!activeSetForPay || !paymentRef) return;

    try {
      await api.post(`/api/v1/settlements/${activeSetForPay.id}/pay/`, { payment_reference: paymentRef });
      loadSettlements();
    } catch (err) {
      setSettlements(settlements.map(s => s.id === activeSetForPay.id ? {
        ...s,
        status: 'PAID',
        payment_reference: paymentRef,
        paid_at: new Date().toISOString()
      } : s));
      alert(`Demo Mode: Marked as paid. Ref: ${paymentRef}`);
    } finally {
      setActiveSetForPay(null);
      setPaymentRef('');
    }
  };

  const triggerCustomCalculation = async (e) => {
    e.preventDefault();
    if (!genRange.start_date || !genRange.end_date) return;

    try {
      const res = await api.post('/api/v1/settlements/generate_range/', genRange);
      alert(res.data?.status || "Job triggered successfully!");
      loadSettlements();
    } catch (err) {
      alert(`Demo Mode: Triggered calculations for range ${genRange.start_date} to ${genRange.end_date}`);
    }
  };

  return (
    <div className="space-y-6 animate-slide-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Settlement calculations</h1>
          <p className="text-slate-400 text-sm">Review revenues, apply deductions, and dispatch driver payouts</p>
        </div>
      </div>

      {/* Action triggers grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Custom calculations trigger */}
        <div className="lg:col-span-1 glass-panel rounded-2xl p-5 space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Calendar className="w-4 h-4 text-indigo-400" />
            <span>Generate Settlement Range</span>
          </h3>
          <form onSubmit={triggerCustomCalculation} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-400 text-[10px] uppercase font-bold mb-1">Start Date</label>
                <input
                  type="date"
                  required
                  value={genRange.start_date}
                  onChange={(e) => setGenRange({ ...genRange, start_date: e.target.value })}
                  className="w-full glass-input rounded-lg py-1.5 px-3 text-xs"
                />
              </div>
              <div>
                <label className="block text-slate-400 text-[10px] uppercase font-bold mb-1">End Date</label>
                <input
                  type="date"
                  required
                  value={genRange.end_date}
                  onChange={(e) => setGenRange({ ...genRange, end_date: e.target.value })}
                  className="w-full glass-input rounded-lg py-1.5 px-3 text-xs"
                />
              </div>
            </div>
            <button
              type="submit"
              className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow transition-colors cursor-pointer"
            >
              Trigger Settlement Scan
            </button>
          </form>
        </div>

        {/* Financial formula guide */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-5 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2">Fleet Settlement System Formula</h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Payout totals are calculated weekly at midnight using audited OCR uploads and records:
            </p>
            <div className="p-3 bg-slate-900/40 border border-slate-800/80 rounded-xl font-mono text-[11px] text-slate-200">
              Settlement = Gross Earnings (Uber) − Cash Collected − Expenses − Advances − Company Commission (15%)
            </div>
          </div>
          <div className="text-[10px] text-slate-500 mt-2 font-medium">
            * All values are dynamically calculated. Manual adjustments are added as secondary modifiers.
          </div>
        </div>
      </div>

      {/* Settlements Table */}
      <div className="glass-panel rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/40 text-xs font-semibold uppercase tracking-wider text-slate-400">
                <th className="p-4">Driver</th>
                <th className="p-4">Billing Range</th>
                <th className="p-4 text-right">Gross Earnings</th>
                <th className="p-4 text-right">Cash Collected</th>
                <th className="p-4 text-right">Deductions</th>
                <th className="p-4 text-right">Commission (15%)</th>
                <th className="p-4 text-right">Adjustments</th>
                <th className="p-4 text-right">Net Payout</th>
                <th className="p-4">Status</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs font-medium">
              {settlements.map((set) => {
                const totalDeductions = parseFloat(set.expenses_amount || 0) + parseFloat(set.advances_amount || 0);
                return (
                  <tr key={set.id} className="hover:bg-slate-900/20 transition-colors">
                    <td className="p-4 font-bold text-white">{set.driver_name}</td>
                    <td className="p-4 text-slate-400 font-mono">{set.start_date} to {set.end_date}</td>
                    <td className="p-4 text-right text-emerald-400">₹{parseFloat(set.gross_earnings).toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td className="p-4 text-right text-red-400">₹{parseFloat(set.cash_collected).toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td className="p-4 text-right text-red-400/80">₹{totalDeductions.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td className="p-4 text-right text-slate-400">₹{parseFloat(set.commission_amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td className="p-4 text-right text-indigo-400 font-mono">
                      ₹{parseFloat(set.manual_adjustment || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="p-4 text-right text-white font-bold text-sm bg-slate-900/20">
                      ₹{parseFloat(set.final_settlement_amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="p-4">
                      <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                        set.status === 'PAID'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : set.status === 'APPROVED'
                          ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        {set.status}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex gap-1.5 justify-end">
                        <button
                          onClick={() => {
                            setActiveSetForAdjust(set);
                            setAdjustForm({
                              manual_adjustment: set.manual_adjustment?.toString() || '0',
                              manual_adjustment_reason: set.manual_adjustment_reason || ''
                            });
                          }}
                          className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700/60 transition-colors cursor-pointer"
                          title="Apply manual override"
                        >
                          <Sliders className="w-3.5 h-3.5" />
                        </button>
                        {set.status === 'PENDING' && (
                          <button
                            onClick={() => handleApprove(set.id)}
                            className="p-1 rounded bg-indigo-600/20 hover:bg-indigo-650 text-indigo-400 border border-indigo-500/20 hover:border-transparent transition-all cursor-pointer"
                            title="Approve Settlement"
                          >
                            <FileCheck className="w-3.5 h-3.5" />
                          </button>
                        )}
                        {set.status === 'APPROVED' && (
                          <button
                            onClick={() => setActiveSetForPay(set)}
                            className="p-1 rounded bg-emerald-600/20 hover:bg-emerald-600 text-emerald-400 hover:text-white border border-emerald-500/20 hover:border-transparent transition-all cursor-pointer"
                            title="Confirm Payout Dispatch"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Adjustments Modal */}
      {activeSetForAdjust && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setActiveSetForAdjust(null)} />
          <div className="relative w-full max-w-md bg-[#0b1329] border border-slate-800 rounded-3xl p-6 shadow-2xl animate-slide-in">
            <h3 className="text-lg font-bold text-white mb-4">Apply Manual Adjustment: {activeSetForAdjust.driver_name}</h3>
            <form onSubmit={handleAdjust} className="space-y-4">
              <div>
                <label className="block text-slate-400 text-xs font-semibold mb-1.5">Adjustment Amount (₹)</label>
                <input
                  type="number"
                  required
                  value={adjustForm.manual_adjustment}
                  onChange={(e) => setAdjustForm({ ...adjustForm, manual_adjustment: e.target.value })}
                  className="w-full glass-input rounded-xl py-2.5 px-4 text-sm"
                  placeholder="e.g. 500 or -200"
                />
              </div>
              <div>
                <label className="block text-slate-400 text-xs font-semibold mb-1.5">Audit Comment / Reason</label>
                <textarea
                  required
                  value={adjustForm.manual_adjustment_reason}
                  onChange={(e) => setAdjustForm({ ...adjustForm, manual_adjustment_reason: e.target.value })}
                  className="w-full glass-input rounded-xl py-2.5 px-4 text-sm h-20"
                  placeholder="e.g. Fuel allowance offset"
                />
              </div>
              <div className="flex gap-2 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setActiveSetForAdjust(null)}
                  className="px-4 py-2.5 bg-slate-800 text-slate-300 border border-slate-700/60 rounded-xl text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-indigo-600 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/10 cursor-pointer"
                >
                  Apply Override
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Payment Confirmation Modal */}
      {activeSetForPay && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setActiveSetForPay(null)} />
          <div className="relative w-full max-w-md bg-[#0b1329] border border-slate-800 rounded-3xl p-6 shadow-2xl animate-slide-in">
            <h3 className="text-lg font-bold text-white mb-4">Confirm Payment Dispatch</h3>
            <p className="text-xs text-slate-400 leading-normal mb-4">
              Payout of ₹{activeSetForPay.final_settlement_amount} is being confirmed for driver {activeSetForPay.driver_name}. Please verify bank account / UPI ID transfer and log reference below.
            </p>
            <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-xl text-[11px] mb-4 space-y-1">
              <div>Bank Account: <span className="font-mono text-slate-300">{activeSetForPay.bank_account || 'N/A'}</span></div>
              <div>UPI ID: <span className="font-mono text-slate-300">{activeSetForPay.upi_id || 'N/A'}</span></div>
            </div>
            <form onSubmit={handlePay} className="space-y-4">
              <div>
                <label className="block text-slate-400 text-xs font-semibold mb-1.5">Transaction Reference Number</label>
                <input
                  type="text"
                  required
                  value={paymentRef}
                  onChange={(e) => setPaymentRef(e.target.value)}
                  className="w-full glass-input rounded-xl py-2.5 px-4 text-sm"
                  placeholder="e.g. UTR1122883344"
                />
              </div>
              <div className="flex gap-2 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setActiveSetForPay(null)}
                  className="px-4 py-2.5 bg-slate-800 text-slate-300 border border-slate-700/60 rounded-xl text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-emerald-600 text-white rounded-xl text-xs font-semibold shadow-lg shadow-emerald-600/10 cursor-pointer"
                >
                  Confirm Paid Status
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
