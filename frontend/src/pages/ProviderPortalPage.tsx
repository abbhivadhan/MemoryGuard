/**
 * Provider Portal Page
 * Main entry point for healthcare provider portal
 */
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import PatientList from '../components/provider/PatientList';
import ProviderDashboard from '../components/provider/ProviderDashboard';

const ProviderPortalPage: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/provider/patients" replace />} />
      <Route path="/patients" element={<PatientList />} />
      <Route path="/patients/:patientId" element={<ProviderDashboard />} />
    </Routes>
  );
};

export default ProviderPortalPage;
