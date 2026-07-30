import React from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../store';

const Header: React.FC = () => {
  const status = useSelector((state: RootState) => state.complaintForm.status);
  
  return (
    <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shadow-sm sticky top-0 z-10">
      <div>
        <h1 className="text-xl font-bold text-blue-700">Log Customer Complaint</h1>
        <p className="text-sm text-slate-500 font-medium">API & PDF Quality Assurance Module</p>
      </div>
      <div>
        {status === 'ready_to_commit' ? (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-100 text-green-800 border border-green-200 rounded-full text-sm font-semibold shadow-sm">
            <span className="text-[10px]">●</span> Ready to Commit
          </span>
        ) : (
          <span className="px-3 py-1 bg-amber-100 text-amber-800 border border-amber-200 rounded-full text-sm font-semibold shadow-sm">
            {status === 'pending_triage' ? 'Pending Triage' : status}
          </span>
        )}
      </div>
    </header>
  );
};

export default Header;
