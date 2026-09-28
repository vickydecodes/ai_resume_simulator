import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SetupPage from '@/pages/Setup';
import InterviewPage from '@/pages/Interview';
import ResultPage from '@/pages/Result';
import { Toaster } from 'sonner';

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/" element={<SetupPage />} />
        <Route path="/interview/:id" element={<InterviewPage />} />
        <Route path="/result/:id" element={<ResultPage />} />
      </Routes>
    </BrowserRouter>
  );
}
