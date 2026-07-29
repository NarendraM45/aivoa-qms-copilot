import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { resetForm } from '../store/complaintFormSlice';
import { useCreateComplaintMutation, useUpdateComplaintMutation } from '../store/api';
import type { RootState } from '../store';

const FormActions: React.FC = () => {
  const dispatch = useDispatch();
  const formState = useSelector((state: RootState) => state.complaintForm);
  const [createComplaint, { isLoading: isCreating }] = useCreateComplaintMutation();
  const [updateComplaint, { isLoading: isUpdating }] = useUpdateComplaintMutation();

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset the form? All data will be lost.')) {
      dispatch(resetForm());
    }
  };

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
        alert('Complaint updated successfully!');
      } else {
        await createComplaint(payload).unwrap();
        alert('Complaint created successfully!');
      }
    } catch (err) {
      alert('Failed to save complaint.');
      console.error(err);
    }
  };

  const isLoading = isCreating || isUpdating;

  return (
    <div className="border-t border-slate-200 bg-slate-50 p-4 flex items-center justify-between mt-auto">
      <button 
        type="button" 
        onClick={handleReset}
        className="px-4 py-2 border border-slate-300 text-slate-700 bg-white hover:bg-slate-50 rounded-md font-medium transition-colors"
      >
        Reset Form
      </button>
      <button 
        type="button"
        onClick={handleSave}
        disabled={isLoading}
        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors disabled:opacity-70 flex items-center"
      >
        {isLoading ? 'Saving...' : 'Save Complaint'}
      </button>
    </div>
  );
};

export default FormActions;
