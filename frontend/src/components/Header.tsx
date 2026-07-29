import React from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../store';

const Header: React.FC = () => {
  const status = useSelector((state: RootState) => state.complaintForm.status);
  
  return (
    <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shadow-sm sticky top-0 z-10">
      <div>
        <h1 className="text-xl font-bold text-blue-700">Pharma Complaint Management System</h1>
        <p className="text-sm text-slate-500 font-medium">AI-Powered Quality Management</p>
      </div>
      <div>
        <span className="px-3 py-1 bg-amber-100 text-amber-800 border border-amber-200 rounded-full text-sm font-semibold shadow-sm">
          {status === 'pending_triage' ? 'Pending Triage' : status}
        </span>
      </div>
    </header>
  );
};

export default Header;
