import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { createSession } from '@/lib/api';
import { Upload, Briefcase, Building2, Loader2, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

export default function SetupPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [company, setCompany] = useState('');
  const [role, setRole] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      const ext = selected.name.split('.').pop()?.toLowerCase();
      if (ext !== 'pdf' && ext !== 'docx') {
        setError('Please upload a PDF or DOCX file.');
        setFile(null);
        return;
      }
      if (selected.size > 5 * 1024 * 1024) {
        setError('File size must be under 5 MB.');
        setFile(null);
        return;
      }
      setError(null);
      setFile(selected);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please upload your resume document.');
      return;
    }
    if (!company.trim()) {
      setError('Please enter a target company name.');
      return;
    }
    if (!role.trim()) {
      setError('Please enter a target role title.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      toast.info('Ingesting resume, scraping company intelligence, and profiling target role...');
      
      const response = await createSession(file, company.trim(), role.trim());
      toast.success('Analysis complete! Initializing mock interview session...');
      
      navigate(`/interview/${response.session_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to initialize session.');
      toast.error('Initialization error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50">
      <Card className="w-full max-w-xl shadow-md border-slate-200">
        <CardHeader className="space-y-1">
          <div className="flex items-center space-x-2">
            <Briefcase className="h-6 w-6 text-slate-900" />
            <CardTitle className="text-2xl font-bold">HireFit AI</CardTitle>
          </div>
          <CardDescription className="text-slate-600">
            Target-Company & Role-Specific Adaptive Interview Simulator
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="resume">Candidate Resume (PDF / DOCX)</Label>
              <div className="flex items-center space-x-2 border border-slate-200 rounded-md p-2 bg-white">
                <Upload className="h-5 w-5 text-slate-500" />
                <Input
                  id="resume"
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  disabled={loading}
                  className="border-none focus-visible:ring-0 text-slate-700 cursor-pointer"
                />
              </div>
              {file && (
                <p className="text-xs text-slate-500">Selected file: {file.name} ({(file.size / 1024).toFixed(1)} KB)</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="company">Target Company Name</Label>
              <div className="relative">
                <Building2 className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                <Input
                  id="company"
                  placeholder="e.g. Stripe, Google, Acme Corp"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  disabled={loading}
                  className="pl-9"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">Target Role Title</Label>
              <div className="relative">
                <Briefcase className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                <Input
                  id="role"
                  placeholder="e.g. Senior Software Engineer, Product Manager"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  disabled={loading}
                  className="pl-9"
                />
              </div>
            </div>
          </CardContent>

          <CardFooter>
            <Button type="submit" disabled={loading} className="w-full h-11 text-base">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing Resume & Company Intel...
                </>
              ) : (
                'Start Adaptive Mock Interview'
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
