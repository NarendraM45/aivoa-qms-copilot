import React from 'react';
import FormSection from './FormSection';
import AIFormField from './AIFormField';
import FormActions from './FormActions';
import RiskAssessmentPanel from './RiskAssessment';

const ComplaintForm: React.FC = () => {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-200 bg-white">
        <h2 className="text-lg font-bold text-slate-800">Complaint Details</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 md:p-6 bg-slate-50">
        <FormSection title="1. Origin & Customer Details">
          <AIFormField fieldName="complaint_source" label="Complaint Source" type="select" 
            options={[
              {value: 'phone', label: 'Phone'}, {value: 'email', label: 'Email'}, 
              {value: 'letter', label: 'Letter'}, {value: 'portal', label: 'Portal'}, 
              {value: 'sales_rep', label: 'Sales Rep'}, {value: 'pharmacy', label: 'Pharmacy'}
            ]} 
          />
          <AIFormField fieldName="customer_name" label="Customer Name" type="text" />
        </FormSection>

        <FormSection title="2. Product & Batch Identification">
          <AIFormField fieldName="product_name" label="Product Name" type="text" />
          <AIFormField fieldName="product_strength" label="Product Strength" type="text" />
          <AIFormField fieldName="batch_number" label="Batch Number" type="text" />
          <AIFormField fieldName="manufacturing_date" label="Manufacturing Date" type="date" />
          <AIFormField fieldName="expiry_date" label="Expiry Date" type="date" />
          <div className="flex gap-2">
            <div className="flex-1"><AIFormField fieldName="quantity_affected" label="Quantity" type="number" /></div>
            <div className="flex-1"><AIFormField fieldName="quantity_unit" label="Unit" type="select" options={[
              {value: 'tablets', label: 'Tablets'}, {value: 'capsules', label: 'Capsules'},
              {value: 'vials', label: 'Vials'}, {value: 'bottles', label: 'Bottles'},
              {value: 'kg', label: 'Kg'}, {value: 'g', label: 'g'}, {value: 'mL', label: 'mL'}
            ]} /></div>
          </div>
        </FormSection>

        <FormSection title="3. Complaint Details">
          <AIFormField fieldName="complaint_type" label="Complaint Type" type="select" options={[
            {value: 'product_quality', label: 'Product Quality'}, {value: 'packaging', label: 'Packaging'},
            {value: 'adverse_event', label: 'Adverse Event'}, {value: 'delivery', label: 'Delivery'},
            {value: 'documentation', label: 'Documentation'}, {value: 'other', label: 'Other'}
          ]} />
          <AIFormField fieldName="complaint_date" label="Complaint Date" type="date" />
          <div className="col-span-1 md:col-span-2">
            <AIFormField fieldName="complaint_description" label="Complaint Description" type="textarea" />
          </div>
        </FormSection>

        <FormSection title="4. Initial Assessment & Priority">
          <AIFormField fieldName="initial_severity" label="Initial Severity" type="select" options={[
            {value: 'low', label: 'Low'}, {value: 'medium', label: 'Medium'},
            {value: 'high', label: 'High'}, {value: 'critical', label: 'Critical'}
          ]} />
          <AIFormField fieldName="priority" label="Priority" type="select" options={[
            {value: 'low', label: 'Low'}, {value: 'medium', label: 'Medium'},
            {value: 'high', label: 'High'}, {value: 'urgent', label: 'Urgent'}
          ]} />
        </FormSection>

        <div className="mt-6">
          <RiskAssessmentPanel />
        </div>
      </div>

      <FormActions />
    </div>
  );
};

export default ComplaintForm;
