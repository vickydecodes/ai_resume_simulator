import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { CandidateNavHeader } from '@/components/CandidateNavHeader';
import { getCandidateProfile, saveSessionHistory } from '@/lib/auth';
import { getInterviewResult, EvaluationReport, QuestionReviewItem, ATSResumeOptimization } from '@/lib/api';
import { 
  Award, 
  CheckCircle2, 
  AlertTriangle, 
  Lightbulb, 
  RotateCcw, 
  AlertCircle, 
  Building2, 
  Briefcase, 
  User, 
  Printer, 
  Calendar, 
  FileCheck2,
  Copy,
  Check,
  XCircle,
  Sparkles,
  Target
} from 'lucide-react';
import { toast } from 'sonner';

export default function ResultPage() {
  const { id: sessionId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [copiedBulletIdx, setCopiedBulletIdx] = useState<number | null>(null);

  const fetchResult = async () => {
    if (!sessionId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await getInterviewResult(sessionId);
      setReport(data);

      // Save to candidate session history
      const currentCand = getCandidateProfile();
      const candEmail = currentCand?.email || 'verified@candidate.com';
      const candName = data.candidate_name || currentCand?.name || 'Candidate';
      saveSessionHistory({
        sessionId: data.session_id,
        candidateEmail: candEmail,
        candidateName: candName,
        companyName: data.company_name,
        roleTitle: data.role_title,
        overallScore: data.overall_score,
        recommendation: data.hiring_recommendation || (data.overall_score >= 80 ? 'Strong Hire' : data.overall_score >= 65 ? 'Hire' : 'Needs Upskilling'),
        createdAt: new Date().toISOString(),
      });
    } catch (err: any) {
      setError(err.message || 'Failed to load evaluation report.');
      toast.error('Failed to load evaluation report.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResult();
  }, [sessionId]);

  const handlePrint = () => {
    toast.info('Formatting printable PDF report...');
    setTimeout(() => {
      window.print();
    }, 200);
  };

  const copyBullet = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedBulletIdx(idx);
    toast.success('Optimized bullet point copied to clipboard!');
    setTimeout(() => setCopiedBulletIdx(null), 2500);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <CandidateNavHeader />
        <div className="max-w-4xl mx-auto p-4 sm:p-8 space-y-4">
          <Card className="p-6 space-y-4 border border-slate-200 bg-white">
            <Skeleton className="h-8 w-1/2" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-40 w-full" />
          </Card>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen bg-slate-50">
        <CandidateNavHeader />
        <div className="max-w-md mx-auto mt-20 p-4">
          <Card className="p-6 space-y-4 text-center border border-slate-200 bg-white shadow-sm">
            <Alert variant="destructive" className="text-left border-red-200 bg-red-50 text-red-900">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertTitle className="text-xs font-bold">Evaluation Report Error</AlertTitle>
              <AlertDescription className="text-xs mt-1">
                {error || 'Unable to load evaluation report. The session may still be processing or expired.'}
              </AlertDescription>
            </Alert>
            <div className="flex flex-col gap-2 pt-2">
              <Button onClick={fetchResult} className="w-full bg-slate-900 hover:bg-slate-800 text-white">
                <RotateCcw className="mr-2 h-4 w-4" /> Retry Loading Report
              </Button>
              <Button onClick={() => navigate('/')} variant="outline" className="w-full border-slate-200">
                Back to Dashboard
              </Button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  const {
    candidate_name,
    role_title,
    company_name,
    overall_score,
    estimated_selection_probability,
    hiring_recommendation,
    category_scores,
    top_strengths,
    top_weaknesses,
    improvement_tips,
    questions_review = [],
    ats_optimization,
    disclaimer,
  } = report;

  const reportDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const correctQuestionsCount = questions_review.filter((q) => q.is_correct).length;
  const totalQuestionsCount = questions_review.length || 20;

  return (
    <>
      <style>{`
        @media print {
          @page {
            margin: 1.2cm;
            size: A4 portrait;
          }
          body {
            background-color: #ffffff !important;
            color: #0f172a !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          .no-print {
            display: none !important;
          }
          .print-only {
            display: block !important;
          }
          .print-card {
            border: 1px solid #cbd5e1 !important;
            box-shadow: none !important;
            page-break-inside: avoid;
          }
        }
        @media screen {
          .print-only {
            display: none !important;
          }
        }
      `}</style>

      <div className="min-h-screen bg-slate-50 text-slate-900 pb-16 font-sans">
        <CandidateNavHeader candidateProfile={{ name: candidate_name, email: 'verified@candidate.com', isLoggedIn: true }} />

        <main className="max-w-5xl mx-auto px-4 sm:px-6 pt-6 space-y-6">
          
          {/* Header Summary Card */}
          <Card className="border border-slate-200 bg-white shadow-xs print-card">
            <CardHeader className="pb-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex flex-wrap items-center gap-3 text-xs font-semibold text-slate-500 mb-1.5">
                    <span className="flex items-center text-slate-900">
                      <User className="h-3.5 w-3.5 mr-1 text-slate-700" /> Candidate: {candidate_name}
                    </span>
                    <span>•</span>
                    <span className="flex items-center">
                      <Calendar className="h-3.5 w-3.5 mr-1" /> Evaluated: {reportDate}
                    </span>
                  </div>
                  <CardTitle className="text-xl sm:text-2xl font-black text-slate-900 flex items-center">
                    <Award className="h-6 w-6 mr-2 text-slate-900 shrink-0" />
                    Interview Performance & Evaluation Report
                  </CardTitle>
                  <CardDescription className="flex items-center gap-3 mt-1 text-slate-600">
                    <span className="flex items-center font-bold text-slate-900">
                      <Briefcase className="h-3.5 w-3.5 mr-1 text-slate-600" /> {role_title}
                    </span>
                    <span>•</span>
                    <span className="flex items-center font-bold text-slate-900">
                      <Building2 className="h-3.5 w-3.5 mr-1 text-slate-600" /> {company_name}
                    </span>
                  </CardDescription>
                </div>

                <div className="flex items-center gap-2 no-print shrink-0">
                  <Button 
                    onClick={handlePrint} 
                    className="bg-slate-900 hover:bg-slate-800 text-white shadow-xs text-xs h-9 font-bold"
                    size="sm"
                  >
                    <Printer className="mr-1.5 h-4 w-4" /> Download / Print PDF
                  </Button>
                  <Button onClick={() => navigate('/')} variant="outline" size="sm" className="text-xs h-9 border-slate-200 bg-white">
                    <RotateCcw className="mr-1.5 h-3.5 w-3.5" /> Start Another Simulation
                  </Button>
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Core Metric Gauges Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Overall Score */}
            <Card className="p-5 border border-slate-200 bg-white shadow-xs print-card flex flex-col justify-between">
              <div>
                <span className="text-xs font-bold uppercase text-slate-500 tracking-wider">
                  Overall Score
                </span>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-4xl font-black text-slate-900">{overall_score}</span>
                  <span className="text-sm font-semibold text-slate-400">/ 100</span>
                </div>
              </div>
              <div className="mt-4">
                <Progress value={overall_score} className="h-2 bg-slate-100" />
                <div className="flex items-center justify-between text-[11px] text-slate-500 mt-1.5">
                  <span>Questions Correct:</span>
                  <span className="font-bold text-slate-900">{correctQuestionsCount} / {totalQuestionsCount}</span>
                </div>
              </div>
            </Card>

            {/* Selection Probability */}
            <Card className="p-5 border border-slate-200 bg-white shadow-xs print-card flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase text-slate-500 tracking-wider">
                    Offer Probability
                  </span>
                  <Badge variant="outline" className="text-[10px] py-0 border-slate-300 text-slate-700 bg-slate-50 font-semibold">
                    Calibrated
                  </Badge>
                </div>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-4xl font-black text-slate-900">{estimated_selection_probability}%</span>
                </div>
              </div>
              <p className="text-[11px] text-slate-500 mt-4 leading-tight">
                Statistical likelihood of passing {company_name}'s hiring bar based on rubric calibration.
              </p>
            </Card>

            {/* ATS Match Score */}
            <Card className="p-5 border border-slate-200 bg-white shadow-xs print-card flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase text-slate-500 tracking-wider">
                    ATS Resume Match
                  </span>
                  <Badge className={`text-[10px] py-0 font-bold ${
                    (ats_optimization?.match_score || 0) >= 75
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-300'
                      : 'bg-amber-50 text-amber-800 border border-amber-300'
                  }`}>
                    {hiring_recommendation || 'Evaluated'}
                  </Badge>
                </div>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-4xl font-black text-slate-900">
                    {ats_optimization?.match_score ?? 78}%
                  </span>
                </div>
              </div>
              <div className="mt-4">
                <Progress value={ats_optimization?.match_score ?? 78} className="h-2 bg-slate-100" />
                <div className="flex items-center justify-between text-[11px] text-slate-500 mt-1.5">
                  <span>Matched Core Skills:</span>
                  <span className="font-bold text-slate-900">{ats_optimization?.matched_skills?.length || 4} Keywords</span>
                </div>
              </div>
            </Card>
          </div>

          {/* Disclaimer Alert */}
          <Alert className="border border-slate-200 bg-white text-slate-700 print-card py-2.5">
            <AlertCircle className="h-4 w-4 text-slate-600" />
            <AlertTitle className="text-xs font-bold text-slate-900">Algorithmic Calibration Disclaimer</AlertTitle>
            <AlertDescription className="text-[11px] text-slate-500 leading-relaxed mt-0.5">
              {disclaimer}
            </AlertDescription>
          </Alert>

          {/* COMPREHENSIVE TABS: Performance, Question Review (20), ATS Optimizer */}
          <Card className="border border-slate-200 bg-white shadow-xs print-card">
            <CardContent className="p-4 sm:p-6">
              {/* Screen Mode: Interactive Tabs */}
              <div className="no-print">
                <Tabs defaultValue="breakdown" className="w-full">
                  <TabsList className="grid w-full grid-cols-3 h-10 p-1 bg-slate-100 rounded-lg">
                    <TabsTrigger value="breakdown" className="text-xs font-bold">
                      Performance Overview
                    </TabsTrigger>
                    <TabsTrigger value="questions" className="text-xs font-bold">
                      Question Review ({totalQuestionsCount})
                    </TabsTrigger>
                    <TabsTrigger value="ats" className="text-xs font-bold">
                      ATS Resume Optimizer
                    </TabsTrigger>
                  </TabsList>

                  {/* TAB 1: PERFORMANCE BREAKDOWN */}
                  <TabsContent value="breakdown" className="space-y-6 pt-5">
                    {/* Category Scores */}
                    <div className="space-y-3.5">
                      <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                        Core Competency Scores
                      </h4>

                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-xs font-semibold mb-1">
                            <span className="text-slate-600">Resume-Role Fit (25%)</span>
                            <span className="font-bold text-slate-900">{category_scores.resume_fit}%</span>
                          </div>
                          <Progress value={category_scores.resume_fit} className="h-2 bg-slate-100" />
                        </div>

                        <div>
                          <div className="flex justify-between text-xs font-semibold mb-1">
                            <span className="text-slate-600">Technical & Domain Knowledge (35%)</span>
                            <span className="font-bold text-slate-900">{category_scores.technical_knowledge}%</span>
                          </div>
                          <Progress value={category_scores.technical_knowledge} className="h-2 bg-slate-100" />
                        </div>

                        <div>
                          <div className="flex justify-between text-xs font-semibold mb-1">
                            <span className="text-slate-600">Communication Clarity & Structure (15%)</span>
                            <span className="font-bold text-slate-900">{category_scores.communication}%</span>
                          </div>
                          <Progress value={category_scores.communication} className="h-2 bg-slate-100" />
                        </div>

                        <div>
                          <div className="flex justify-between text-xs font-semibold mb-1">
                            <span className="text-slate-600">Problem Solving & Architecture (15%)</span>
                            <span className="font-bold text-slate-900">{category_scores.problem_solving}%</span>
                          </div>
                          <Progress value={category_scores.problem_solving} className="h-2 bg-slate-100" />
                        </div>

                        <div>
                          <div className="flex justify-between text-xs font-semibold mb-1">
                            <span className="text-slate-600">Company & Domain Awareness (10%)</span>
                            <span className="font-bold text-slate-900">{category_scores.company_awareness}%</span>
                          </div>
                          <Progress value={category_scores.company_awareness} className="h-2 bg-slate-100" />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    {/* Strengths & Weaknesses */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2.5 border border-emerald-200 rounded-lg p-4 bg-emerald-50/50">
                        <h4 className="text-xs font-bold text-emerald-900 flex items-center">
                          <CheckCircle2 className="h-4 w-4 mr-1.5 text-emerald-600" /> Key Strengths
                        </h4>
                        <ul className="space-y-2 text-xs text-slate-700 list-disc list-inside">
                          {top_strengths.map((item, idx) => (
                            <li key={idx} className="leading-relaxed">{item}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="space-y-2.5 border border-rose-200 rounded-lg p-4 bg-rose-50/50">
                        <h4 className="text-xs font-bold text-rose-900 flex items-center">
                          <AlertTriangle className="h-4 w-4 mr-1.5 text-rose-600" /> Identified Weaknesses
                        </h4>
                        <ul className="space-y-2 text-xs text-slate-700 list-disc list-inside">
                          {top_weaknesses.map((item, idx) => (
                            <li key={idx} className="leading-relaxed">{item}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Concrete Improvement Plan */}
                    <div className="border border-slate-200 rounded-lg p-4 bg-slate-50 space-y-3">
                      <h4 className="text-xs font-bold text-slate-900 flex items-center">
                        <Lightbulb className="h-4 w-4 mr-1.5 text-amber-500" /> Concrete Action & Remediation Plan
                      </h4>
                      <div className="space-y-2">
                        {improvement_tips.map((tip, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-xs text-slate-800">
                            <span className="font-bold text-slate-900 min-w-[20px]">{idx + 1}.</span>
                            <span className="leading-relaxed">{tip}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </TabsContent>

                  {/* TAB 2: PER-QUESTION DETAILED REVIEW (20 QUESTIONS) */}
                  <TabsContent value="questions" className="space-y-4 pt-5">
                    <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                      <div>
                        <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                          Full 20-Question Breakdown
                        </h4>
                        <p className="text-[11px] text-slate-500 mt-0.5">
                          Review candidate selections against verified rubric keys with full concept rationales.
                        </p>
                      </div>
                      <Badge variant="outline" className="text-xs border-slate-300 text-slate-800 bg-white font-bold">
                        {correctQuestionsCount} of {totalQuestionsCount} Correct
                      </Badge>
                    </div>

                    <div className="space-y-3.5">
                      {questions_review.map((q) => {
                        return (
                          <div
                            key={q.turn_number}
                            className={`p-4 rounded-lg border transition-colors space-y-3 ${
                              q.is_correct
                                ? 'border-emerald-200 bg-emerald-50/20'
                                : 'border-rose-200 bg-rose-50/20'
                            }`}
                          >
                            {/* Question Header */}
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                              <div className="flex items-center gap-2">
                                <div className={`w-6 h-6 rounded-md flex items-center justify-center text-xs font-bold ${
                                  q.is_correct
                                    ? 'bg-emerald-600 text-white'
                                    : 'bg-rose-600 text-white'
                                }`}>
                                  {q.turn_number}
                                </div>
                                <span className="font-bold text-xs text-slate-900">
                                  {q.stage_title}
                                </span>
                              </div>

                              <div className="flex items-center gap-2">
                                <Badge variant="secondary" className="text-[10px] py-0 bg-slate-100 text-slate-700">
                                  {q.topic}
                                </Badge>
                                <Badge className={`text-[10px] py-0 font-bold ${
                                  q.is_correct
                                    ? 'bg-emerald-50 text-emerald-800 border border-emerald-300'
                                    : 'bg-rose-50 text-rose-800 border border-rose-300'
                                }`}>
                                  {q.is_correct ? 'Correct' : 'Incorrect'}
                                </Badge>
                              </div>
                            </div>

                            {/* Question Prompt */}
                            <p className="text-xs sm:text-sm font-semibold text-slate-900 leading-relaxed">
                              {q.question}
                            </p>

                            {/* Candidate vs Correct Option comparison */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs pt-1">
                              <div className="p-2.5 rounded-md bg-white border border-slate-200 space-y-1">
                                <span className="text-[10px] font-bold uppercase text-slate-500 block">
                                  Candidate Selection:
                                </span>
                                <p className="font-medium text-slate-900">
                                  {q.candidate_selected_option || q.candidate_answer || 'No answer submitted'}
                                </p>
                              </div>

                              <div className="p-2.5 rounded-md bg-white border border-slate-200 space-y-1">
                                <span className="text-[10px] font-bold uppercase text-emerald-700 block">
                                  Verified Solution Key: Option {q.correct_option}
                                </span>
                                <p className="font-medium text-slate-900">
                                  Standard verified answer
                                </p>
                              </div>
                            </div>

                            {/* Concept Explanation */}
                            {q.explanation && (
                              <div className="p-3 rounded-md bg-white border border-slate-200 text-xs text-slate-700 leading-relaxed">
                                <span className="font-bold text-slate-900">Rationale & Concept: </span>
                                {q.explanation}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </TabsContent>

                  {/* TAB 3: ATS RESUME OPTIMIZER */}
                  <TabsContent value="ats" className="space-y-6 pt-5">
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                        ATS Keyword & Resume Match Optimization
                      </h4>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        Bridge keyword gaps and use AI-tailored high-impact bullet points to increase recruiter callback rates.
                      </p>
                    </div>

                    {/* Matched vs Missing Keywords */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {/* Matched Skills */}
                      <div className="p-4 rounded-lg border border-emerald-200 bg-emerald-50/40 space-y-2.5">
                        <div className="flex items-center justify-between">
                          <h5 className="text-xs font-bold text-emerald-900 flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Matched Core Competencies
                          </h5>
                          <Badge variant="outline" className="text-[10px] bg-white border-emerald-300 text-emerald-800 font-bold">
                            {ats_optimization?.matched_skills?.length || 0} Found
                          </Badge>
                        </div>
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {ats_optimization?.matched_skills?.map((skill, idx) => (
                            <Badge key={idx} className="bg-white text-emerald-800 border border-emerald-300 text-xs font-medium">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {/* Missing Keywords */}
                      <div className="p-4 rounded-lg border border-amber-200 bg-amber-50/40 space-y-2.5">
                        <div className="flex items-center justify-between">
                          <h5 className="text-xs font-bold text-amber-900 flex items-center gap-1.5">
                            <Target className="w-3.5 h-3.5 text-amber-600" /> High-Priority Keyword Gaps
                          </h5>
                          <Badge variant="outline" className="text-[10px] bg-white border-amber-300 text-amber-800 font-bold">
                            {ats_optimization?.missing_skills?.length || 0} Gaps
                          </Badge>
                        </div>
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {ats_optimization?.missing_skills?.map((skill, idx) => (
                            <Badge key={idx} className="bg-white text-amber-800 border border-amber-300 text-xs font-medium">
                              + {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>

                    <Separator />

                    {/* 3 AI-Optimized Resume Bullet Points */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <h5 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                            <Sparkles className="w-3.5 h-3.5 text-slate-700" />
                            3 AI-Optimized Resume Bullets (Tailored for {company_name})
                          </h5>
                          <p className="text-[11px] text-slate-500 mt-0.5">
                            Quantified, action-verb driven bullets designed for ATS parser passes.
                          </p>
                        </div>
                      </div>

                      <div className="space-y-3">
                        {ats_optimization?.optimized_bullet_points?.map((bullet, idx) => (
                          <div
                            key={idx}
                            className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/60 hover:bg-slate-100/60 transition-colors flex items-start justify-between gap-3"
                          >
                            <div className="space-y-1 flex-1">
                              <Badge variant="outline" className="text-[10px] bg-white border-slate-300 text-slate-700 mb-1 font-semibold">
                                Bullet #{idx + 1}
                              </Badge>
                              <p className="text-xs sm:text-sm font-medium text-slate-900 leading-relaxed">
                                {bullet}
                              </p>
                            </div>

                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => copyBullet(bullet, idx)}
                              className="h-8 text-xs shrink-0 border-slate-300 bg-white hover:bg-slate-50"
                            >
                              {copiedBulletIdx === idx ? (
                                <>
                                  <Check className="w-3 h-3 text-emerald-600 mr-1" /> Copied
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3 h-3 mr-1" /> Copy
                                </>
                              )}
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </div>

              {/* Print Mode: Complete Unified View for Clean PDF Export */}
              <div className="print-only space-y-6">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3">
                    1. Competency Category Scores
                  </h3>
                  <div className="space-y-2.5">
                    <div className="flex justify-between text-xs py-1 border-b border-slate-200">
                      <span>Resume-Role Fit:</span>
                      <span className="font-bold">{category_scores.resume_fit}%</span>
                    </div>
                    <div className="flex justify-between text-xs py-1 border-b border-slate-200">
                      <span>Technical & Domain Knowledge:</span>
                      <span className="font-bold">{category_scores.technical_knowledge}%</span>
                    </div>
                    <div className="flex justify-between text-xs py-1 border-b border-slate-200">
                      <span>Communication Clarity:</span>
                      <span className="font-bold">{category_scores.communication}%</span>
                    </div>
                    <div className="flex justify-between text-xs py-1 border-b border-slate-200">
                      <span>Problem Solving & Architecture:</span>
                      <span className="font-bold">{category_scores.problem_solving}%</span>
                    </div>
                    <div className="flex justify-between text-xs py-1 border-b border-slate-200">
                      <span>Company Awareness:</span>
                      <span className="font-bold">{category_scores.company_awareness}%</span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div className="border border-slate-300 rounded p-3 bg-slate-50">
                    <h4 className="text-xs font-bold text-slate-900 mb-2">Key Strengths</h4>
                    <ul className="text-[11px] space-y-1 list-disc list-inside">
                      {top_strengths.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="border border-slate-300 rounded p-3 bg-slate-50">
                    <h4 className="text-xs font-bold text-slate-900 mb-2">Identified Weaknesses</h4>
                    <ul className="text-[11px] space-y-1 list-disc list-inside">
                      {top_weaknesses.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="pt-2 border border-slate-300 rounded p-3 bg-slate-50">
                  <h4 className="text-xs font-bold text-slate-900 mb-2">Concrete Action Plan</h4>
                  <div className="space-y-1.5 text-[11px]">
                    {improvement_tips.map((tip, idx) => (
                      <div key={idx} className="flex items-start space-x-1.5">
                        <span className="font-bold">{idx + 1}.</span>
                        <span>{tip}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>

            <Separator />
            <CardFooter className="flex justify-between items-center py-3 bg-slate-50 border-t border-slate-200">
              <span className="text-xs text-slate-500">Session ID: {sessionId}</span>
              <div className="flex items-center gap-2 no-print">
                <Button onClick={handlePrint} variant="outline" size="sm" className="text-xs border-slate-300 bg-white">
                  <Printer className="mr-1.5 h-3.5 w-3.5" /> Print / Save as PDF
                </Button>
                <Button onClick={() => navigate('/')} size="sm" className="text-xs bg-slate-900 hover:bg-slate-800 text-white">
                  Practice Another Target
                </Button>
              </div>
            </CardFooter>
          </Card>
        </main>
      </div>
    </>
  );
}
