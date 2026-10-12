import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { CandidateNavHeader } from '@/components/CandidateNavHeader';
import { 
  getCurrentUser, 
  getActiveResume, 
  getCandidateActiveResumeFile 
} from '@/lib/auth';
import { 
  getCompanyById, 
  calculateResumeReadiness, 
  CompanyRole 
} from '@/lib/companies';
import { createSession } from '@/lib/api';
import { toast } from 'sonner';
import { 
  Building2, 
  ArrowLeft, 
  Play, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  ShieldCheck, 
  Layers, 
  Briefcase, 
  ChevronRight,
  Loader2,
  SlidersHorizontal,
  Compass,
  DollarSign
} from 'lucide-react';

export default function CompanyDetailPage() {
  const { companyId } = useParams<{ companyId: string }>();
  const navigate = useNavigate();

  const company = companyId ? getCompanyById(companyId) : undefined;
  const user = getCurrentUser();
  const activeResume = getActiveResume(user);

  // Selected role (default to first role)
  const [selectedRole, setSelectedRole] = useState<CompanyRole | undefined>(
    company?.roles && company.roles.length > 0 ? company.roles[0] : undefined
  );
  const [difficulty, setDifficulty] = useState<'low' | 'medium' | 'hard'>(
    selectedRole?.difficulty || 'medium'
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!company) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
        <CandidateNavHeader />
        <div className="flex-1 flex items-center justify-center p-6">
          <Card className="max-w-md w-full text-center p-8 bg-white border-slate-200">
            <Building2 className="w-10 h-10 text-slate-400 mx-auto" />
            <h2 className="text-base font-bold text-slate-900 mt-3">Target Company Not Found</h2>
            <p className="text-xs text-slate-500 mt-1 mb-6">
              The requested employer rubric could not be found in the directory.
            </p>
            <Button
              onClick={() => navigate('/')}
              className="bg-slate-900 text-white font-semibold h-9 text-xs"
            >
              Back to Companies Directory
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  // Calculate Resume Readiness against Company Competencies
  const readiness = calculateResumeReadiness(
    activeResume ? activeResume.skills : [],
    company.competencies
  );

  const handleStartInterview = async () => {
    setError(null);

    if (!user) {
      toast.error('Please sign in before starting the interview.');
      navigate('/login', { state: { from: `/company/${company.id}` } });
      return;
    }

    if (!activeResume) {
      setError('No active resume found in your profile. Please add one in Profile & Resumes.');
      return;
    }

    const resumeFile = getCandidateActiveResumeFile(user);
    if (!resumeFile) {
      setError('Unable to load active resume file for calibration.');
      return;
    }

    const targetRoleTitle = selectedRole?.title || `${company.name} Specialist`;
    const targetJd = selectedRole?.jobDescription || `Standard hiring rubric for ${company.name} ${targetRoleTitle}`;

    setLoading(true);
    try {
      const res = await createSession(
        resumeFile,
        company.name,
        targetRoleTitle,
        targetJd,
        difficulty
      );
      toast.success(`Calibrated 20 questions for ${company.name} — ${targetRoleTitle}!`);
      navigate(`/interview/${res.session_id}`);
    } catch (err: any) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
        'Failed to calibrate interview simulation. Please ensure the backend is running.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-16 font-sans">
      <CandidateNavHeader />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 space-y-8">
        
        {/* TOP BREADCRUMB & BACK BUTTON */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
            className="text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 p-0 h-8 px-2"
          >
            <ArrowLeft className="w-3.5 h-3.5 mr-1.5" />
            Back to Companies Directory
          </Button>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 hidden sm:inline">Active CV:</span>
            <Badge 
              variant="outline" 
              className="text-xs font-medium bg-white text-slate-700 border-slate-300 cursor-pointer hover:bg-slate-100"
              onClick={() => navigate('/profile')}
              title="Click to switch active resume"
            >
              <FileText className="w-3 h-3 mr-1 text-slate-900" />
              {activeResume ? activeResume.label : 'None'}
            </Badge>
          </div>
        </div>

        {/* 1. COMPANY HEADER OVERVIEW CARD */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-xs flex flex-col md:flex-row md:items-start justify-between gap-6">
          <div className="space-y-3 max-w-3xl">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold text-lg shadow-sm">
                {company.name.charAt(0)}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
                    {company.name}
                  </h1>
                  {company.ticker && (
                    <Badge variant="outline" className="text-xs font-mono bg-slate-50 text-slate-600 border-slate-200">
                      {company.ticker}
                    </Badge>
                  )}
                  <Badge className="text-xs bg-slate-100 text-slate-700 border-slate-200">
                    Verified Rubric
                  </Badge>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  {company.industry} • Headquarters: {company.headquarters}
                </p>
              </div>
            </div>

            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              {company.description}
            </p>

            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-1">
              <span className="font-semibold text-slate-900 block">Engineering & Hiring Culture:</span>
              <p className="text-slate-600 leading-relaxed">
                {company.culture}
              </p>
            </div>

            {/* Estimated Worth & Financial Valuation Scale */}
            {company.estimatedWorth && (
              <div className="p-3.5 rounded-lg bg-emerald-50/60 border border-emerald-200 text-xs text-slate-800 flex items-start gap-3">
                <div className="p-1.5 rounded-md bg-emerald-100 text-emerald-800 shrink-0 mt-0.5">
                  <DollarSign className="w-4 h-4" />
                </div>
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 text-xs">
                      Enterprise Worth: {company.estimatedWorth}
                    </span>
                    {company.isCustomScraped && (
                      <Badge className="text-[9px] py-0 px-1.5 bg-emerald-100 text-emerald-800 border-emerald-300">
                        BeautifulSoup Scraped
                      </Badge>
                    )}
                  </div>
                  <p className="text-slate-600 leading-relaxed text-[11px]">
                    {company.worthBreakdown || 'Capital market valuation calibrated from public equity benchmarks and SEC filings.'}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Quick Readiness Score Dial */}
          <div className="bg-slate-50 rounded-xl border border-slate-200 p-5 flex flex-col items-center justify-center text-center min-w-[220px] self-center md:self-start">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Active CV Readiness
            </span>
            <div className="my-2">
              <span className={`text-4xl font-extrabold tracking-tight ${
                readiness.score >= 80 ? 'text-emerald-700' : readiness.score >= 65 ? 'text-blue-700' : 'text-amber-700'
              }`}>
                {readiness.score}%
              </span>
            </div>
            <p className="text-[11px] font-medium text-slate-600">
              {readiness.matchedSkills.length} of {company.competencies.length} Competencies
            </p>
            <div className="w-full mt-3">
              <Progress value={readiness.score} className="h-1.5 bg-slate-200" />
            </div>
          </div>
        </div>

        {/* 2. TWO-COLUMN LAYOUT: HIRING PROCESS & RESUME BENCHMARK */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* HIRING PROCESS CARD */}
          <Card className="bg-white border-slate-200 shadow-xs">
            <CardHeader className="pb-3 pt-5 px-6">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Compass className="w-4 h-4 text-slate-900" />
                  Hiring Process & Stages
                </CardTitle>
                <Badge variant="outline" className="text-[10px] font-semibold bg-slate-50 text-slate-700 border-slate-300">
                  20 Total MCQs
                </Badge>
              </div>
              <CardDescription className="text-xs text-slate-500">
                Evaluation structure calibrated against real {company.name} interview standards.
              </CardDescription>
            </CardHeader>
            <CardContent className="px-6 py-3 space-y-4">
              {company.hiringStages.map((stage, idx) => (
                <div 
                  key={idx}
                  className="p-3.5 rounded-lg border border-slate-200 bg-slate-50 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900">
                      {stage.title}
                    </span>
                    <Badge className="text-[10px] py-0 px-2 font-bold bg-slate-900 text-white">
                      {stage.questionCount} Questions
                    </Badge>
                  </div>
                  <div className="text-[11px] text-slate-500 font-medium">
                    Format: <span className="text-slate-800">{stage.format}</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed bg-white p-2.5 rounded border border-slate-100">
                    {stage.focus}
                  </p>
                </div>
              ))}

              <div className="p-3 rounded-lg bg-blue-50/60 border border-blue-200 text-xs text-blue-900 flex items-start gap-2.5">
                <ShieldCheck className="w-4 h-4 text-blue-700 shrink-0 mt-0.5" />
                <div className="space-y-0.5">
                  <span className="font-semibold text-blue-900">30-Minute Calibrated Examination</span>
                  <p className="text-[11px] text-blue-700">
                    Test begins with 10 platform aptitude questions, followed immediately by 10 domain systems questions. No coding terminal required.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* ACTIVE RESUME FIT & COMPETENCIES CARD */}
          <Card className="bg-white border-slate-200 shadow-xs">
            <CardHeader className="pb-3 pt-5 px-6">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-slate-900" />
                  Active CV Benchmark Analysis
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate('/profile')}
                  className="h-6 text-[11px] text-slate-900 font-semibold p-0 hover:bg-transparent hover:underline"
                >
                  Switch CV
                </Button>
              </div>
              <CardDescription className="text-xs text-slate-500">
                Evaluation of your active resume against {company.name}'s competency baseline.
              </CardDescription>
            </CardHeader>
            <CardContent className="px-6 py-3 space-y-4">
              {/* Matched Competencies */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-900 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Matched Competencies ({readiness.matchedSkills.length})
                  </span>
                  <span className="text-[11px] text-emerald-700 font-semibold">Strong Alignment</span>
                </div>
                <div className="flex flex-wrap gap-1.5 p-3 rounded-lg bg-slate-50 border border-slate-200">
                  {readiness.matchedSkills.length > 0 ? (
                    readiness.matchedSkills.map((skill, sIdx) => (
                      <Badge
                        key={sIdx}
                        className="text-[10px] py-0.5 px-2 font-medium bg-emerald-50 text-emerald-800 border border-emerald-300"
                      >
                        ✓ {skill}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-xs text-slate-400 italic">No direct keyword overlap found.</span>
                  )}
                </div>
              </div>

              {/* Assessment Focus / Gap Areas */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-900 flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                    Target Competencies Evaluated in Test ({readiness.missingSkills.length})
                  </span>
                  <span className="text-[11px] text-amber-700 font-semibold">Will Be Assessed</span>
                </div>
                <div className="flex flex-wrap gap-1.5 p-3 rounded-lg bg-slate-50 border border-slate-200">
                  {readiness.missingSkills.length > 0 ? (
                    readiness.missingSkills.map((skill, sIdx) => (
                      <Badge
                        key={sIdx}
                        variant="outline"
                        className="text-[10px] py-0.5 px-2 font-medium bg-white text-slate-700 border-slate-300"
                      >
                        • {skill}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-xs text-emerald-700 font-medium">All baseline competencies represented in CV!</span>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 3. ROLE SELECTION & START INTERVIEW LAUNCHER */}
        <Card className="bg-white border-slate-900 shadow-sm">
          <CardHeader className="pb-3 pt-5 px-6">
            <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-slate-900" />
              Configure & Attend Simulation Test
            </CardTitle>
            <CardDescription className="text-xs text-slate-500">
              Select your target role and question calibration level to initialize your 20-question test.
            </CardDescription>
          </CardHeader>

          <CardContent className="px-6 py-3 space-y-5">
            {error && (
              <Alert className="border-red-200 bg-red-50 text-red-800">
                <AlertCircle className="w-4 h-4 text-red-600" />
                <AlertTitle className="text-xs font-bold">Unable to Launch Interview</AlertTitle>
                <AlertDescription className="text-xs mt-0.5">{error}</AlertDescription>
              </Alert>
            )}

            {/* Role Options */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-900 block">
                Target Role Track
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {company.roles.map((role) => {
                  const isSelected = selectedRole?.id === role.id;
                  return (
                    <div
                      key={role.id}
                      onClick={() => {
                        setSelectedRole(role);
                        setDifficulty(role.difficulty);
                      }}
                      className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                        isSelected
                          ? 'border-slate-900 bg-slate-50 shadow-xs'
                          : 'border-slate-200 bg-white hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-xs text-slate-900">{role.title}</span>
                        <Badge variant="outline" className="text-[10px] py-0 px-1.5 font-bold uppercase border-slate-300 text-slate-700">
                          {role.level}
                        </Badge>
                      </div>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {role.requiredSkills.map((req, rIdx) => (
                          <Badge key={rIdx} variant="outline" className="text-[9px] py-0 px-1 bg-white border-slate-200 text-slate-600">
                            {req}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Difficulty Calibration */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-900 block">
                Question Difficulty Calibration
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { id: 'low', label: 'Foundational', sub: 'Core Principles' },
                  { id: 'medium', label: 'Mid-Senior', sub: 'Standard Rubric' },
                  { id: 'hard', label: 'Staff / Principal', sub: 'Edge Cases & Scale' },
                ].map((diff) => (
                  <Button
                    key={diff.id}
                    type="button"
                    variant={difficulty === diff.id ? 'default' : 'outline'}
                    onClick={() => setDifficulty(diff.id as any)}
                    className={`h-auto py-2.5 flex flex-col items-center justify-center ${
                      difficulty === diff.id
                        ? 'bg-slate-900 text-white hover:bg-slate-800'
                        : 'bg-white border-slate-200 text-slate-800 hover:bg-slate-50'
                    }`}
                  >
                    <span className="text-xs font-bold">{diff.label}</span>
                    <span className={`text-[10px] ${difficulty === diff.id ? 'text-slate-300' : 'text-slate-400'}`}>
                      {diff.sub}
                    </span>
                  </Button>
                ))}
              </div>
            </div>

            {/* Selected Role Job Description Preview */}
            {selectedRole && (
              <div className="space-y-1.5">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                  Calibrated Job Specification Context
                </span>
                <ScrollArea className="h-28 p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700 font-mono leading-relaxed">
                  <pre className="whitespace-pre-wrap font-sans text-xs">
                    {selectedRole.jobDescription}
                  </pre>
                </ScrollArea>
              </div>
            )}
          </CardContent>

          <CardFooter className="bg-slate-50 border-t border-slate-200 py-4 px-6 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="text-xs text-slate-500 text-center sm:text-left">
              Using active CV: <span className="font-semibold text-slate-900">{activeResume?.label || 'None'}</span>
            </div>

            <Button
              size="lg"
              onClick={handleStartInterview}
              disabled={loading}
              className="w-full sm:w-auto h-10 px-6 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-sm"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Calibrating 20 Questions...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2 fill-current" />
                  Attend Interview / Start 20-Question Test
                </>
              )}
            </Button>
          </CardFooter>
        </Card>

      </main>
    </div>
  );
}
