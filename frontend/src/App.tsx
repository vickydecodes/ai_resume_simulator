import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from '@/pages/Home';
import CompanyDetailPage from '@/pages/CompanyDetail';
import ProfilePage from '@/pages/Profile';
import LoginPage from '@/pages/Login';
import SetupPage from '@/pages/Setup';
import InterviewPage from '@/pages/Interview';
import ResultPage from '@/pages/Result';
import { Toaster } from 'sonner';

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" richColors />
      <Routes>
        {/* Main Target Companies Hub */}
        <Route path="/" element={<HomePage />} />
        
        {/* Company-Specific Hiring Process, Readiness & Assessment Launcher */}
        <Route path="/company/:companyId" element={<CompanyDetailPage />} />

        {/* Candidate Profile & Multi-Resume Portfolio */}
        <Route path="/profile" element={<ProfilePage />} />

        {/* Candidate Authentication */}
        <Route path="/login" element={<LoginPage />} />

        {/* Custom Ad-Hoc Setup */}
        <Route path="/setup" element={<SetupPage />} />

        {/* 20-Question Role-Calibrated Simulation Exam */}
        <Route path="/interview/:id" element={<InterviewPage />} />

        {/* Assessment Scorecard & In-Depth Report */}
        <Route path="/result/:id" element={<ResultPage />} />

        {/* Catch-all redirect to Home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
