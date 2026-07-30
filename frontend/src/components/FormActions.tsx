import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setStatus } from '../store/complaintFormSlice';
import { useCreateComplaintMutation, useUpdateComplaintMutation } from '../store/api';
import type { RootState } from '../store';

const FormActions: React.FC = () => {
  const dispatch = useDispatch();
  const formState = useSelector((state: RootState) => state.complaintForm);
  const [createComplaint, { isLoading: isCreating }] = useCreateComplaintMutation();
  const [updateComplaint, { isLoading: isUpdating }] = useUpdateComplaintMutation();

  const handleSave = async () => {
    // Basic validation
    if (!formState.product_name.value || !formState.complaint_description.value) {
      alert('Product Name and Complaint Description are required.');
      return;
    }
    
    const payload = Object.keys(formState).reduce((acc: any, key) => {
      if (!['complaintId', 'status', 'isSaving', 'saveError'].includes(key)) {
        acc[key] = (formState as any)[key].value;
      }
      return acc;
    }, {});
    
    try {
      if (formState.complaintId) {
        await updateComplaint({ id: formState.complaintId, ...payload }).unwrap();
        dispatch(setStatus('ready_to_commit'));
      } else {
        await createComplaint(payload).unwrap();
        dispatch(setStatus('ready_to_commit'));
      }
    } catch (err) {
      alert('Failed to save complaint.');
      console.error(err);
    }
  };

  const isLoading = isCreating || isUpdating;
  const isFormEmpty = !formState.product_name.value && !formState.complaint_description.value;

  return (
    <div className="border-t border-slate-200 bg-white p-4">
      <button 
        type="button"
        onClick={handleSave}
        disabled={isLoading || isFormEmpty}
        className="w-full py-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-xl text-base font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Committing...
          </>
        ) : (
          'Commit to QMS Ledger'
        )}
      </button>
    </div>
  );
};

export default FormActions;
