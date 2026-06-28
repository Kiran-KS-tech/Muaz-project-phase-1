import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to append JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for automatic token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const res = await axios.post(`${API_BASE_URL}/api/v1/accounts/token/refresh/`, { refresh });
          localStorage.setItem('access_token', res.data.access);
          api.defaults.headers.common['Authorization'] = `Bearer ${res.data.access}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh token expired or invalid
          localStorage.clear();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Mock fallback data to ensure Frontend is instantly runnable and testable
export const mockData = {
  stats: {
    totalEarnings: 342500,
    activeDrivers: 18,
    pendingSettlements: 5,
    activeCars: 14,
    maintenanceAlerts: 2,
  },
  drivers: [
    { id: 1, driver_id: 'DRV-101', name: 'Aarav Sharma', phone: '+91 9876543210', status: 'ACTIVE', joining_date: '2025-01-10', license_number: 'DL-14202100034', license_expiry: '2028-09-15', bank_account: '918273645012', upi_id: 'aarav@okaxis' },
    { id: 2, driver_id: 'DRV-102', name: 'Rohan Verma', phone: '+91 8765432109', status: 'ACTIVE', joining_date: '2025-02-14', license_number: 'MH-12201987451', license_expiry: '2027-04-10', bank_account: '109283746564', upi_id: 'rohanv@okicici' },
    { id: 3, driver_id: 'DRV-103', name: 'Kabir Singh', phone: '+91 7654321098', status: 'PENDING', joining_date: '2026-05-20', license_number: 'HR-26202045612', license_expiry: '2026-07-28', bank_account: '554321098765', upi_id: 'kabirs@okhdfc' },
    { id: 4, driver_id: 'DRV-104', name: 'Vikram Malhotra', phone: '+91 9998887776', status: 'SUSPENDED', joining_date: '2024-11-05', license_number: 'DL-01201865432', license_expiry: '2025-12-05', bank_account: '987654321098', upi_id: 'vikram@okaxis' }
  ],
  cars: [
    { id: 1, registration_number: 'DL-1CA-5643', brand: 'Maruti Suzuki', model: 'Ertiga', year: 2022, fuel_type: 'CNG', status: 'ACTIVE', driver_name: 'Aarav Sharma', insurance_expiry: '2026-10-12', permit_expiry: '2027-01-20', fitness_expiry: '2027-05-14', pollution_expiry: '2026-08-30' },
    { id: 2, registration_number: 'MH-12-PQ-8876', brand: 'Hyundai', model: 'Aura', year: 2023, fuel_type: 'CNG', status: 'MAINTENANCE', driver_name: 'Rohan Verma', insurance_expiry: '2026-03-04', permit_expiry: '2028-04-12', fitness_expiry: '2028-09-02', pollution_expiry: '2026-07-15' },
    { id: 3, registration_number: 'HR-26-AS-0912', brand: 'Tata', model: 'Tigor EV', year: 2023, fuel_type: 'ELECTRIC', status: 'ACTIVE', driver_name: 'None', insurance_expiry: '2026-12-18', permit_expiry: '2028-03-24', fitness_expiry: '2028-03-24', pollution_expiry: '2026-11-20' }
  ],
  settlements: [
    { id: 1, driver_name: 'Aarav Sharma', start_date: '2026-06-15', end_date: '2026-06-21', gross_earnings: 12500, cash_collected: 3200, expenses_amount: 1450, advances_amount: 1000, commission_amount: 1875, final_settlement_amount: 4975, status: 'PENDING' },
    { id: 2, driver_name: 'Rohan Verma', start_date: '2026-06-15', end_date: '2026-06-21', gross_earnings: 14200, cash_collected: 2100, expenses_amount: 1850, advances_amount: 0, commission_amount: 2130, final_settlement_amount: 8120, status: 'APPROVED' },
    { id: 3, driver_name: 'Vikram Malhotra', start_date: '2026-06-15', end_date: '2026-06-21', gross_earnings: 11800, cash_collected: 4000, expenses_amount: 900, advances_amount: 2000, commission_amount: 1770, final_settlement_amount: 3130, status: 'PAID', payment_reference: 'TXN9988221' }
  ],
  activities: [
    { id: 1, action: 'CREATE', model_name: 'Driver', object_id: '3', timestamp: '2026-06-28T14:30:00Z', user_email: 'manager@fleet.com' },
    { id: 2, action: 'SETTLEMENT_APPROVAL', model_name: 'Settlement', object_id: '2', timestamp: '2026-06-28T12:15:00Z', user_email: 'owner@fleet.com' },
    { id: 3, action: 'OCR_COMPLETE', model_name: 'EarningUpload', object_id: '12', timestamp: '2026-06-28T10:45:00Z', user_email: 'System' }
  ]
};

export default api;
