import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { CandidateNavHeader } from '@/components/CandidateNavHeader';
import { 
  PRELOADED_ROLE_CONFIGS, 
  PreloadedRoleConfig, 
  createSampleResumeForConfig 
} from '@/lib/presets';
import { 
  getCandidateProfile, 
  loginCandidate, 
  logoutCandidate, 
  CandidateProfile 
} from '@/lib/auth';
import { createSession } from '@/lib/api';
import { 
  Upload, 
  Building2, 
  Loader2, 
  AlertCircle, 
  FileText, 
  Check, 
  User, 
  Mail, 
  SlidersHorizontal,
  ArrowRight,
  ShieldCheck,
  Briefcase,
  LogIn,
  LogOut,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';

export default function SetupPage() {
  const navigate = useNavigate();

  // Candidate Authentication State
  const [profile, setProfile] = useState<CandidateProfile | null>(getCandidateProfile());
  const [nameInput, setNameInput] = useState(profile ? profile.name : '');
  const [emailInput, setEmailInput] = useState(profile ? profile.email : '');
  const [file, setFile] = useState<File | null>(null);

  // Selected Target Preloaded Config (Default: Google SDE-2)
  const [selectedConfig, setSelectedConfig] = useState<PreloadedRoleConfig>(PRELOADED_ROLE_CONFIGS[0]);

  // Optional custom override toggle
  const [isCustomMode, setIsCustomMode] = useState(false);
  const [customCompany, setCustomCompany] = useState('');
  const [customRole, setCustomRole] = useState('');
  const [customJd, setCustomJd] = useState('');

  const [difficulty, setDifficulty] = useState<'low' | 'medium' | 'hard'>('medium');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-initialize sample resume if candidate is logged in and hasn't selected a file yet
  useEffect(() => {
    if (profile && !file && selectedConfig) {
      const sample = createSampleResumeForConfig(selectedConfig);
      setFile(sample);
    }
  }, [profile, selectedConfig]);

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!nameInput.trim()) {
      toast.error('Please enter your full name.');
      return;
    }
    if (!emailInput.trim() || !emailInput.includes('@')) {
      toast.error('Please enter a valid email address.');
      return;
    }
    const newProfile = loginCandidate(nameInput, emailInput, file?.name);
    setProfile(newProfile);
    if (!file) {
      const sample = createSampleResumeForConfig(selectedConfig);
      setFile(sample);
    }
    toast.success(`Logged in as ${newProfile.name}`);
  };

  const handleQuickDemoLogin = () => {
    const demoName = 'Alex Johnson';
    const demoEmail = 'alex.johnson@example.com';
    setNameInput(demoName);
    setEmailInput(demoEmail);
    const newProfile = loginCandidate(demoName, demoEmail);
    setProfile(newProfile);
    const sample = createSampleResumeForConfig(selectedConfig);
    setFile(sample);
    toast.success('Signed in with Demo Candidate profile');
  };

  const handleLogout = () => {
    logoutCandidate();
    setProfile(null);
    setNameInput('');
    setEmailInput('');
    setFile(null);
    toast.info('Logged out from candidate session.');
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      const ext = selected.name.split('.').pop()?.toLowerCase();
      if (ext !== 'pdf' && ext !== 'docx' && ext !== 'txt') {
        setError('Please upload a PDF, DOCX, or TXT resume file.');
        return;
      }
      if (selected.size > 5 * 1024 * 1024) {
        setError('File size must be under 5 MB.');
        return;
      }
      setError(null);
      setFile(selected);
      if (profile) {
        loginCandidate(profile.name, profile.email, selected.name);
      }
      toast.success(`Resume attached: ${selected.name}`);
    }
  };

  const handleSelectPreloaded = (config: PreloadedRoleConfig) => {
    setSelectedConfig(config);
    setDifficulty(config.difficulty);
    setIsCustomMode(false);
    setError(null);
    // If using sample resume, update to this config's verified sample
    if (file && file.name.includes('Resume.txt')) {
      const sample = createSampleResumeForConfig(config);
      setFile(sample);
    }
    toast.info(`Selected ${config.company} — ${config.role}`);
  };

  const handleLoadSampleResume = () => {
    const sample = createSampleResumeForConfig(selectedConfig);
    setFile(sample);
    setError(null);
    toast.success(`Loaded verified sample resume for ${selectedConfig.role}`);
  };

  const handleStartInterview = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // If not logged in, require login first
    if (!profile) {
      if (!nameInput.trim() || !emailInput.trim()) {
        setError('Please sign in with your Name and Email to proceed.');
        return;
      }
      const newProfile = loginCandidate(nameInput, emailInput, file?.name);
      setProfile(newProfile);
    }

    if (!file) {
      setError('Please upload your resume (PDF/DOCX/TXT) or click "Load Verified Sample Resume".');
      return;
    }

    const targetCompany = isCustomMode ? customCompany.trim() : selectedConfig.company;
    const targetRole = isCustomMode ? customRole.trim() : selectedConfig.role;
    const targetJd = isCustomMode ? customJd.trim() : selectedConfig.jobDescription;

    if (!targetCompany) {
      setError('Target company name is required.');
      return;
    }
    if (!targetRole) {
      setError('Target role title is required.');
      return;
    }

    setLoading(true);
    try {
      const res = await createSession(file, targetCompany, targetRole, targetJd, difficulty);
      toast.success(`Calibrated 20 questions for ${targetCompany} ${targetRole}!`);
      navigate(`/interview/${res.session_id}`);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || 'Failed to start interview. Please ensure backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  const activeCompanyName = isCustomMode ? (customCompany || 'Custom Target') : selectedConfig.company;
  const activeRoleName = isCustomMode ? (customRole || 'Custom Role') : selectedConfig.role;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-16 font-sans">
      <CandidateNavHeader 
        candidateProfile={profile} 
        onLogout={handleLogout}
        onLoginClick={() => {
          const el = document.getElementById('loginSection');
          el?.scrollIntoView({ behavior: 'smooth' });
        }}
      />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        
        {/* HEADER TITLE */}
        <div className="space-y-1.5 border-b border-slate-200 pb-5">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Corporate Assessment System</span>
            <Badge variant="outline" className="text-[10px] bg-white border-slate-300 text-slate-700">
              Deterministic 20-Question Framework
            </Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
            Target Company & Role Interview Calibration
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 max-w-2xl leading-relaxed">
            Login with your credentials, attach your resume, and select a pre-configured target company role (such as Google SDE-2 or Stripe Backend). 
            HireFit AI evaluates your profile and generates 10 aptitude questions and 10 domain questions calibrated specifically to that company.
          </p>
        </div>

        {error && (
          <Alert variant="destructive" className="border-red-200 bg-red-50 text-red-900">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertTitle className="text-xs font-bold">Configuration Alert</AlertTitle>
            <AlertDescription className="text-xs">{error}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-8">
          
          {/* STEP 1: CANDIDATE LOGIN & RESUME */}
          <Card id="loginSection" className="border border-slate-200 bg-white shadow-xs">
            <CardHeader className="pb-3 border-b border-slate-100">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-slate-900 text-white text-[11px] font-bold flex items-center justify-center">1</span>
                    Candidate Account & Resume Ingestion
                  </CardTitle>
                  <CardDescription className="text-xs text-slate-500 mt-0.5">
                    {profile ? 'Authenticated candidate credentials and active resume' : 'Sign in with your name and email to proceed'}
                  </CardDescription>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-slate-500">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span className="text-[11px]">Private Local Session</span>
                </div>
              </div>
            </CardHeader>

            <CardContent className="pt-5 space-y-5">
              {/* If candidate is NOT logged in: Show Login Form */}
              {!profile ? (
                <div className="space-y-4 p-4 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                        <LogIn className="w-3.5 h-3.5 text-slate-700" /> Candidate Sign In
                      </h3>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        Enter your credentials to link interview scorecards and resume analysis.
                      </p>
                    </div>

                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleQuickDemoLogin}
                      className="text-xs h-7 border-slate-300 bg-white hover:bg-slate-100"
                    >
                      <Sparkles className="w-3 h-3 mr-1 text-slate-600" /> Quick Demo Login
                    </Button>
                  </div>

                  <form onSubmit={handleLoginSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                    <div className="space-y-1">
                      <Label htmlFor="loginName" className="text-[11px] font-semibold text-slate-700">Full Name *</Label>
                      <Input
                        id="loginName"
                        placeholder="e.g. Alex Johnson"
                        value={nameInput}
                        onChange={(e) => setNameInput(e.target.value)}
                        className="h-8.5 text-xs border-slate-300 bg-white"
                        required
                      />
                    </div>
                    <div className="space-y-1">
                      <Label htmlFor="loginEmail" className="text-[11px] font-semibold text-slate-700">Email Address *</Label>
                      <Input
                        id="loginEmail"
                        type="email"
                        placeholder="e.g. alex.johnson@example.com"
                        value={emailInput}
                        onChange={(e) => setEmailInput(e.target.value)}
                        className="h-8.5 text-xs border-slate-300 bg-white"
                        required
                      />
                    </div>
                    <div className="sm:col-span-2 pt-1">
                      <Button type="submit" size="sm" className="w-full sm:w-auto h-8 text-xs bg-slate-900 hover:bg-slate-800 text-white font-semibold">
                        <LogIn className="w-3 h-3 mr-1.5" /> Sign In & Continue
                      </Button>
                    </div>
                  </form>
                </div>
              ) : (
                /* If candidate is logged in: Show Active Session Status with Logout Button */
                <div className="p-3.5 rounded-lg bg-emerald-50/50 border border-emerald-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold shrink-0">
                      {profile.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xs text-slate-900">{profile.name}</span>
                        <Badge className="bg-emerald-100 text-emerald-800 border-emerald-300 text-[10px] font-semibold">
                          ✓ Signed In
                        </Badge>
                      </div>
                      <p className="text-[11px] text-slate-600 font-mono mt-0.5">{profile.email}</p>
                    </div>
                  </div>

                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleLogout}
                    className="h-7 text-xs border-slate-300 bg-white hover:bg-red-50 hover:text-red-600 text-slate-700"
                  >
                    <LogOut className="w-3 h-3 mr-1" /> Logout / Switch Account
                  </Button>
                </div>
              )}

              {/* Resume File Upload Zone */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <Label className="font-semibold text-slate-700 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-slate-500" /> Candidate Resume (PDF, DOCX, TXT) *
                  </Label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleLoadSampleResume}
                    className="h-6 text-[11px] text-slate-600 hover:text-slate-900 font-medium px-2"
                  >
                    Load Verified Sample Resume
                  </Button>
                </div>

                <div className="border border-dashed border-slate-300 hover:border-slate-400 rounded-lg p-4 bg-slate-50/70 transition-colors">
                  <input
                    type="file"
                    id="resumeUpload"
                    accept=".pdf,.docx,.txt"
                    onChange={handleFileChange}
                    className="hidden"
                    disabled={loading}
                  />
                  <Label htmlFor="resumeUpload" className="cursor-pointer flex flex-col sm:flex-row items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-md bg-white border border-slate-200 flex items-center justify-center text-slate-700 shrink-0">
                        <Upload className="w-4 h-4" />
                      </div>
                      <div className="text-left">
                        <p className="text-xs font-bold text-slate-900">
                          {file ? file.name : 'Select or drop candidate resume file'}
                        </p>
                        <p className="text-[11px] text-slate-500">
                          {file ? `${(file.size / 1024).toFixed(1)} KB attached` : 'Supports PDF, DOCX, or TXT under 5 MB'}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {file && (
                        <Badge className="bg-emerald-50 text-emerald-800 border-emerald-300 font-medium text-[11px]">
                          <Check className="w-3 h-3 mr-1 text-emerald-600" /> Active Resume Attached
                        </Badge>
                      )}
                      <span className="text-xs font-semibold text-slate-700 bg-white border border-slate-200 px-3 py-1.5 rounded-md hover:bg-slate-100">
                        Browse File
                      </span>
                    </div>
                  </Label>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* STEP 2: PRELOADED COMPANY & ROLE SELECTION */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-slate-900 text-white text-[11px] font-bold flex items-center justify-center">2</span>
                  Target Company & Calibrated Role Catalog
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Select a preloaded enterprise track (like Google SDE-2) to evaluate your resume against that company.
                </p>
              </div>

              {/* Custom Target Toggle */}
              <Button
                type="button"
                variant={isCustomMode ? 'default' : 'outline'}
                size="sm"
                onClick={() => setIsCustomMode(!isCustomMode)}
                className={`text-xs h-7.5 ${isCustomMode ? 'bg-slate-900 text-white' : 'border-slate-300 text-slate-700'}`}
              >
                <Briefcase className="w-3 h-3 mr-1.5" />
                {isCustomMode ? 'Using Custom Position' : 'Enter Custom Role'}
              </Button>
            </div>

            {/* PRELOADED CARDS CATALOG */}
            {!isCustomMode ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {PRELOADED_ROLE_CONFIGS.map((cfg) => {
                  const isSelected = selectedConfig.id === cfg.id;

                  return (
                    <Card
                      key={cfg.id}
                      onClick={() => handleSelectPreloaded(cfg)}
                      className={`cursor-pointer transition-all border p-3.5 flex flex-col justify-between rounded-lg ${
                        isSelected
                          ? 'border-slate-900 ring-2 ring-slate-900 bg-white shadow-md'
                          : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/50'
                      }`}
                    >
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-black text-slate-900 flex items-center gap-1.5">
                            <Building2 className="w-3.5 h-3.5 text-slate-700" />
                            {cfg.company}
                          </span>
                          <Badge variant="outline" className="text-[10px] font-semibold py-0 px-1.5 border-slate-300 text-slate-600 bg-slate-50">
                            {cfg.department}
                          </Badge>
                        </div>

                        <div>
                          <h3 className="text-xs font-bold text-slate-900 leading-snug">
                            {cfg.role}
                          </h3>
                          <p className="text-[11px] text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                            {cfg.description}
                          </p>
                        </div>
                      </div>

                      <div className="pt-3 mt-3 border-t border-slate-100 flex items-center justify-between">
                        <Badge className="text-[10px] py-0 px-1.5 bg-slate-100 text-slate-700 border-slate-200 font-medium">
                          {cfg.badge}
                        </Badge>
                        {isSelected ? (
                          <span className="w-4 h-4 rounded-full bg-slate-900 text-white flex items-center justify-center">
                            <Check className="w-2.5 h-2.5 stroke-[3]" />
                          </span>
                        ) : (
                          <span className="text-[11px] text-slate-400 font-semibold group-hover:text-slate-600">Select</span>
                        )}
                      </div>
                    </Card>
                  );
                })}
              </div>
            ) : (
              /* Custom Role Input Container */
              <Card className="border border-slate-200 bg-white p-5 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="customComp" className="text-xs font-semibold text-slate-700">Company Name *</Label>
                    <Input
                      id="customComp"
                      placeholder="e.g. Netflix, Uber, Airbnb"
                      value={customCompany}
                      onChange={(e) => setCustomCompany(e.target.value)}
                      className="h-9 text-xs border-slate-300 bg-white"
                      required={isCustomMode}
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="customRoleTitle" className="text-xs font-semibold text-slate-700">Role Title *</Label>
                    <Input
                      id="customRoleTitle"
                      placeholder="e.g. Staff Distributed Systems Engineer"
                      value={customRole}
                      onChange={(e) => setCustomRole(e.target.value)}
                      className="h-9 text-xs border-slate-300 bg-white"
                      required={isCustomMode}
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="customJdText" className="text-xs font-semibold text-slate-700">Target Job Description (Optional)</Label>
                  <Textarea
                    id="customJdText"
                    placeholder="Paste job description requirements to refine question rubrics and ATS matching..."
                    value={customJd}
                    onChange={(e) => setCustomJd(e.target.value)}
                    rows={4}
                    className="text-xs border-slate-300 bg-white font-mono"
                  />
                </div>
              </Card>
            )}
          </div>

          {/* STEP 3: DIFFICULTY CALIBRATION & LAUNCH BAR */}
          <Card className="border border-slate-200 bg-white shadow-xs">
            <CardContent className="p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="space-y-1 text-center sm:text-left">
                <div className="flex items-center gap-2 justify-center sm:justify-start">
                  <SlidersHorizontal className="w-3.5 h-3.5 text-slate-600" />
                  <span className="text-xs font-bold text-slate-800">Difficulty Calibration:</span>
                  <div className="flex items-center gap-1">
                    {(['low', 'medium', 'hard'] as const).map((lvl) => (
                      <Button
                        key={lvl}
                        type="button"
                        variant={difficulty === lvl ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setDifficulty(lvl)}
                        disabled={loading}
                        className={`h-7 px-2.5 text-[11px] font-semibold capitalize ${
                          difficulty === lvl
                            ? 'bg-slate-900 text-white'
                            : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                        }`}
                      >
                        {lvl}
                      </Button>
                    ))}
                  </div>
                </div>
                <p className="text-[11px] text-slate-500">
                  Target: <strong className="text-slate-900">{activeCompanyName}</strong> • Role: <strong className="text-slate-900">{activeRoleName}</strong> (20 Questions Total)
                </p>
              </div>

              <Button
                type="button"
                onClick={handleStartInterview}
                disabled={loading}
                className="w-full sm:w-auto h-11 px-8 text-sm font-bold bg-slate-900 hover:bg-slate-800 text-white shadow-xs flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Analyzing Resume & Initializing 20 Questions...
                  </>
                ) : (
                  <>
                    <span>Start {activeCompanyName} Simulation</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
