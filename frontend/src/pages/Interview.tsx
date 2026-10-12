import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { CandidateNavHeader } from '@/components/CandidateNavHeader';
import { 
  getFullInterview, 
  submitAllAnswers, 
  FullInterviewResponse, 
  QuestionItem, 
  BatchAnswerItem 
} from '@/lib/api';
import { 
  Loader2, 
  CheckCircle2, 
  Check, 
  AlertCircle, 
  ChevronLeft, 
  ChevronRight, 
  FileCheck,
  Building2,
  Bookmark,
  Clock,
  Play,
  Pause,
  GraduationCap,
  Award,
  Info,
  XCircle
} from 'lucide-react';
import { toast } from 'sonner';

interface AnswerEntry {
  text: string;
  selectedOption: string;
}

export default function InterviewPage() {
  const { id: sessionId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Full Interview Questions from backend
  const [interviewData, setInterviewData] = useState<FullInterviewResponse | null>(null);
  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  // Interactive Learning Mode: 'exam' (strict) vs 'practice' (instant feedback)
  const [interviewMode, setInterviewMode] = useState<'exam' | 'practice'>('exam');

  // Realistic 30-Minute Timer (1800 seconds)
  const [timeLeft, setTimeLeft] = useState<number>(1800);
  const [timerRunning, setTimerRunning] = useState<boolean>(true);

  // Flagged for Review questions (Set of turn numbers)
  const [flaggedTurns, setFlaggedTurns] = useState<Set<number>>(new Set());

  // Form answers mapped by question turn number (1-indexed)
  const [answers, setAnswers] = useState<Record<number, AnswerEntry>>({});

  const storageKey = sessionId ? `hirefit_answers_v4_${sessionId}` : null;
  const flagsStorageKey = sessionId ? `hirefit_flags_v4_${sessionId}` : null;

  // Initialize and load full questions upfront
  useEffect(() => {
    if (!sessionId) return;

    const init = async () => {
      try {
        setLoading(true);
        setLoadError(null);

        const data = await getFullInterview(sessionId);
        setInterviewData(data);
        setQuestions(data.questions || []);

        // Restore saved answers from localStorage if available
        let restoredAnswers: Record<number, AnswerEntry> = {};
        if (storageKey) {
          const cached = localStorage.getItem(storageKey);
          if (cached) {
            try {
              restoredAnswers = JSON.parse(cached);
            } catch (e) {
              console.warn('Failed to parse cached answers');
            }
          }
        }

        // Restore flagged questions
        if (flagsStorageKey) {
          const cachedFlags = localStorage.getItem(flagsStorageKey);
          if (cachedFlags) {
            try {
              const parsedFlags = JSON.parse(cachedFlags);
              if (Array.isArray(parsedFlags)) {
                setFlaggedTurns(new Set(parsedFlags));
              }
            } catch (e) {
              console.warn('Failed to parse cached flags');
            }
          }
        }

        // Initialize any missing entries
        const initialMap: Record<number, AnswerEntry> = { ...restoredAnswers };
        (data.questions || []).forEach((q) => {
          if (!initialMap[q.turn_number]) {
            initialMap[q.turn_number] = {
              text: q.user_answer || '',
              selectedOption: q.selected_option || '',
            };
          }
        });

        setAnswers(initialMap);
      } catch (err: any) {
        setLoadError(err.message || 'Failed to load interview questions.');
        toast.error('Failed to load interview questions.');
      } finally {
        setLoading(false);
      }
    };

    init();
  }, [sessionId]);

  // Timer countdown hook
  useEffect(() => {
    if (!timerRunning || timeLeft <= 0) return;
    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          toast.warning('30-minute time allocation has expired! Please submit your interview.');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [timerRunning, timeLeft]);

  // Synchronize answers with localStorage on modification
  const updateAnswer = (turnNum: number, updater: (prev: AnswerEntry) => AnswerEntry) => {
    setAnswers((prev) => {
      const currentEntry = prev[turnNum] || { text: '', selectedOption: '' };
      const updated = { ...prev, [turnNum]: updater(currentEntry) };
      if (storageKey) {
        localStorage.setItem(storageKey, JSON.stringify(updated));
      }
      return updated;
    });
  };

  const toggleFlagTurn = (turnNum: number) => {
    setFlaggedTurns((prev) => {
      const updated = new Set(prev);
      if (updated.has(turnNum)) {
        updated.delete(turnNum);
        toast.info(`Unflagged Question ${turnNum}`);
      } else {
        updated.add(turnNum);
        toast.info(`Flagged Question ${turnNum} for review`);
      }
      if (flagsStorageKey) {
        localStorage.setItem(flagsStorageKey, JSON.stringify(Array.from(updated)));
      }
      return updated;
    });
  };

  const currentQ = questions[currentIndex];
  const currentAnswer = currentQ ? (answers[currentQ.turn_number] || {
    text: '',
    selectedOption: '',
  }) : null;

  const isQuestionAnswered = (q: QuestionItem): boolean => {
    const a = answers[q.turn_number];
    if (!a) return false;
    return Boolean(a.selectedOption && a.selectedOption.trim().length > 0);
  };

  const answeredCount = questions.filter(isQuestionAnswered).length;
  const totalCount = questions.length || 20;
  const progressPercent = totalCount > 0 ? Math.round((answeredCount / totalCount) * 100) : 0;
  const isCurrentFlagged = currentQ ? flaggedTurns.has(currentQ.turn_number) : false;

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSubmitAll = async () => {
    if (!sessionId || submitting || questions.length === 0) return;

    if (answeredCount < totalCount) {
      const confirmed = window.confirm(
        `You have answered ${answeredCount} of ${totalCount} questions. Unanswered questions will receive zero points. Submit now?`
      );
      if (!confirmed) return;
    }

    setSubmitting(true);
    try {
      const batchPayload: BatchAnswerItem[] = questions.map((q) => {
        const a = answers[q.turn_number] || { text: '', selectedOption: '' };
        const rationaleText = a.text.trim() ? `\n\nRationale / Working: ${a.text.trim()}` : '';
        const submissionText = (a.selectedOption || 'No option selected') + rationaleText;

        return {
          turn_number: q.turn_number,
          answer: submissionText,
          selected_option: a.selectedOption || undefined,
        };
      });

      toast.info('Evaluating answers against company rubric...');
      await submitAllAnswers(sessionId, batchPayload);

      if (storageKey) localStorage.removeItem(storageKey);
      if (flagsStorageKey) localStorage.removeItem(flagsStorageKey);

      toast.success('Evaluation finalized! Loading performance scorecard...');
      navigate(`/result/${sessionId}`);
    } catch (err: any) {
      toast.error(err.message || 'Failed to submit answers. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <CandidateNavHeader />
        <div className="max-w-4xl mx-auto p-4 sm:p-8 space-y-4">
          <Card className="p-6 space-y-4 border border-slate-200 bg-white">
            <Skeleton className="h-7 w-1/3" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-28 w-full" />
            <div className="grid grid-cols-5 gap-2 pt-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          </Card>
        </div>
      </div>
    );
  }

  if (loadError || !currentQ) {
    return (
      <div className="min-h-screen bg-slate-50">
        <CandidateNavHeader />
        <div className="max-w-md mx-auto mt-20 p-4">
          <Card className="p-6 border border-slate-200 bg-white text-center space-y-4 shadow-sm">
            <Alert variant="destructive" className="text-left border-red-200 bg-red-50 text-red-900">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertTitle className="text-xs font-bold">Interview Session Unavailable</AlertTitle>
              <AlertDescription className="text-xs mt-1">
                {loadError || 'The session could not be reached. Please create a new simulation.'}
              </AlertDescription>
            </Alert>
            <Button onClick={() => navigate('/')} className="w-full bg-slate-900 hover:bg-slate-800 text-white">
              Return to Setup Dashboard
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  const roleCategory = interviewData?.role_category || 'tech';
  const companyProfile = interviewData?.company_profile;

  // Practice mode feedback calculation for current question
  const isPracticeMode = interviewMode === 'practice';
  const hasSelectedCurrent = Boolean(currentAnswer?.selectedOption);
  const isOptionCorrect = Boolean(
    hasSelectedCurrent &&
    currentAnswer?.selectedOption &&
    currentQ?.correct_option &&
    currentAnswer.selectedOption.trim().startsWith(currentQ.correct_option.trim())
  );

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-16 font-sans">
      <CandidateNavHeader candidateProfile={{ name: interviewData?.candidate_name || 'Candidate', email: 'verified@candidate.com', isLoggedIn: true }} />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 pt-6 space-y-5">
        
        {/* TOP INTERVIEW CONTROL BAR */}
        <Card className="border border-slate-200 bg-white shadow-xs">
          <div className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
            {/* Title & Metadata */}
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-base font-bold text-slate-900">
                  {interviewData?.company_name} — {interviewData?.role_title}
                </h2>
                <Badge variant="outline" className="text-[11px] font-semibold border-slate-300 text-slate-700 bg-slate-50 capitalize">
                  {roleCategory} Assessment
                </Badge>
                <Badge variant="secondary" className="text-[10px] uppercase font-bold bg-slate-100 text-slate-800">
                  {interviewData?.difficulty_level || 'MEDIUM'}
                </Badge>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Candidate: <span className="font-semibold text-slate-800">{interviewData?.candidate_name}</span> • 20 Total Calibrated Turns
              </p>
            </div>

            {/* Controls: Mode Switcher, 30-Min Timer, Submit */}
            <div className="flex flex-wrap items-center gap-2.5">
              {/* Practice vs Exam Mode Toggle */}
              <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50 p-0.5">
                <Button
                  type="button"
                  variant={interviewMode === 'exam' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setInterviewMode('exam')}
                  className={`h-7 px-2.5 text-xs font-semibold ${
                    interviewMode === 'exam' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Award className="w-3 h-3 mr-1" />
                  Exam Mode
                </Button>
                <Button
                  type="button"
                  variant={interviewMode === 'practice' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setInterviewMode('practice')}
                  className={`h-7 px-2.5 text-xs font-semibold ${
                    interviewMode === 'practice' ? 'bg-slate-900 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <GraduationCap className="w-3.5 h-3.5 mr-1" />
                  Practice Mode
                </Button>
              </div>

              {/* 30-Minute Timer Badge */}
              <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs font-mono font-bold ${
                timeLeft < 180
                  ? 'border-red-300 bg-red-50 text-red-700 animate-pulse'
                  : timeLeft < 300
                  ? 'border-amber-300 bg-amber-50 text-amber-800'
                  : 'border-slate-200 bg-slate-50 text-slate-700'
              }`}>
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                <span>{formatTimer(timeLeft)}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setTimerRunning(!timerRunning)}
                  className="h-5 w-5 p-0 hover:bg-transparent text-slate-400 hover:text-slate-700 ml-0.5"
                >
                  {timerRunning ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                </Button>
              </div>

              {/* Submit Final Button */}
              <Button
                type="button"
                onClick={handleSubmitAll}
                disabled={submitting}
                size="sm"
                className="bg-slate-900 hover:bg-slate-800 text-white text-xs h-8 px-3 font-bold shadow-xs"
              >
                {submitting ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <>
                    <FileCheck className="h-3.5 w-3.5 mr-1" />
                    Submit Scorecard ({answeredCount}/20)
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Company Context Bar if available */}
          {companyProfile && companyProfile.what_they_do && (
            <div className="mx-4 mb-3 p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-start gap-2">
              <Building2 className="h-4 w-4 text-slate-600 shrink-0 mt-0.5" />
              <div className="flex-1">
                <span className="font-bold text-slate-900">{interviewData?.company_name} Context: </span>
                <span className="text-slate-600">{companyProfile.what_they_do}</span>
              </div>
            </div>
          )}

          {/* 20-QUESTION STEPPER & NAVIGATION BAR */}
          <div className="px-4 pb-3 border-t border-slate-100 pt-3">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
              <div className="flex items-center gap-3">
                <span className="font-bold text-slate-800">Question Stepper:</span>
                <span className="flex items-center gap-1 text-[11px]">
                  <span className="w-2 h-2 rounded-full bg-emerald-600 inline-block" /> Answered ({answeredCount})
                </span>
                <span className="flex items-center gap-1 text-[11px]">
                  <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" /> Flagged ({flaggedTurns.size})
                </span>
              </div>
              <span className="font-mono text-[11px] font-semibold text-slate-700">
                {progressPercent}% Complete
              </span>
            </div>

            <div className="grid grid-cols-5 sm:grid-cols-10 gap-1.5">
              {questions.map((q, idx) => {
                const isActive = idx === currentIndex;
                const answered = isQuestionAnswered(q);
                const isFlagged = flaggedTurns.has(q.turn_number);

                return (
                  <Button
                    key={q.turn_number}
                    type="button"
                    variant={isActive ? 'default' : answered ? 'secondary' : 'outline'}
                    size="sm"
                    onClick={() => setCurrentIndex(idx)}
                    className={`h-8 text-[11px] font-bold flex items-center justify-center gap-1 transition-all relative ${
                      isActive
                        ? 'bg-slate-900 text-white border-slate-900 ring-2 ring-slate-900 ring-offset-1 shadow-xs'
                        : answered
                        ? 'bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100'
                        : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    <span>Q{q.turn_number}</span>
                    {isFlagged && (
                      <Bookmark className="w-2.5 h-2.5 text-amber-500 fill-amber-500 absolute top-1 right-1" />
                    )}
                    {answered && !isFlagged && (
                      <Check className="h-2.5 w-2.5 text-emerald-600 shrink-0" />
                    )}
                  </Button>
                );
              })}
            </div>
            <Progress value={progressPercent} className="h-1.5 mt-2 bg-slate-100" />
          </div>
        </Card>

        {/* ACTIVE QUESTION CARD */}
        <Card className="border border-slate-200 bg-white shadow-xs">
          <CardHeader className="py-3 px-4 sm:px-6 bg-slate-50/70 border-b border-slate-100">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-md bg-slate-900 text-white flex items-center justify-center text-xs font-bold">
                  {currentQ.turn_number}
                </div>
                <CardTitle className="text-sm font-bold text-slate-900">
                  Question {currentQ.turn_number} of {totalCount}
                </CardTitle>
                <Badge variant="outline" className="text-[10px] py-0 bg-white border-slate-300 text-slate-700">
                  {currentQ.stage_title}
                </Badge>
              </div>

              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="text-[10px] py-0.5 bg-slate-100 text-slate-700 font-medium">
                  Topic: {currentQ.topic}
                </Badge>
                {/* Bookmark / Flag Button */}
                <Button
                  type="button"
                  variant={isCurrentFlagged ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => toggleFlagTurn(currentQ.turn_number)}
                  className={`h-7 px-2.5 text-xs gap-1 ${
                    isCurrentFlagged
                      ? 'bg-amber-100 border-amber-300 text-amber-900 hover:bg-amber-200'
                      : 'border-slate-200 bg-white text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Bookmark className={`w-3.5 h-3.5 ${isCurrentFlagged ? 'fill-amber-600 text-amber-600' : ''}`} />
                  {isCurrentFlagged ? 'Flagged' : 'Flag for Review'}
                </Button>
              </div>
            </div>
          </CardHeader>

          <CardContent className="p-4 sm:p-6 space-y-5">
            {/* Question Text */}
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 text-slate-900 space-y-2">
              <p className="text-sm sm:text-base font-semibold leading-relaxed whitespace-pre-wrap">
                {currentQ.question}
              </p>

              {currentQ.company_context && (
                <div className="flex items-center gap-1.5 text-xs text-slate-500 pt-2 border-t border-slate-200">
                  <Info className="h-3.5 w-3.5 text-slate-600 shrink-0" />
                  <span>{currentQ.company_context}</span>
                </div>
              )}
            </div>

            {/* Answer Options */}
            {currentQ.options && currentQ.options.length > 0 && (
              <div className="space-y-3">
                <div className="text-xs font-bold text-slate-700 flex items-center justify-between">
                  <span>Candidate Response Options:</span>
                  <span className="text-[11px] font-normal text-slate-500">Select an option to record answer</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {currentQ.options.map((opt, oIdx) => {
                    const isSelected = currentAnswer?.selectedOption === opt;
                    const isCorrectInPractice = isPracticeMode && hasSelectedCurrent && opt.startsWith(currentQ.correct_option || '');

                    return (
                      <Button
                        key={oIdx}
                        type="button"
                        variant={isSelected ? 'default' : 'outline'}
                        onClick={() => {
                          updateAnswer(currentQ.turn_number, (prev) => ({
                            ...prev,
                            selectedOption: opt,
                          }));
                        }}
                        className={`h-auto min-h-[52px] text-left p-3.5 justify-start items-start whitespace-normal text-xs transition-all ${
                          isCorrectInPractice
                            ? 'border-emerald-500 bg-emerald-50 text-emerald-900 ring-1 ring-emerald-500 font-semibold'
                            : isSelected
                            ? 'bg-slate-900 text-white hover:bg-slate-800 border-slate-900 shadow-xs'
                            : 'border-slate-200 bg-white text-slate-800 hover:bg-slate-50'
                        }`}
                      >
                        <div className={`rounded-full p-0.5 mr-2.5 mt-0.5 shrink-0 ${
                          isSelected ? 'bg-white text-slate-900' : 'bg-slate-100 text-slate-400'
                        }`}>
                          {isSelected ? (
                            <Check className="h-3 w-3 stroke-[3]" />
                          ) : (
                            <div className="h-3 w-3 rounded-full border border-slate-300" />
                          )}
                        </div>
                        <span className="leading-relaxed flex-1 font-medium">{opt}</span>
                      </Button>
                    );
                  })}
                </div>

                {/* Optional Rationale / Calculation notes */}
                <div className="pt-2">
                  <Input
                    placeholder="Brief rationale, working notes, or calculation steps (optional)..."
                    value={currentAnswer?.text || ''}
                    onChange={(e) => {
                      updateAnswer(currentQ.turn_number, (prev) => ({
                        ...prev,
                        text: e.target.value,
                      }));
                    }}
                    className="h-9 text-xs border-slate-300 bg-white"
                  />
                </div>
              </div>
            )}

            {/* PRACTICE MODE INSTANT EXPLANATION BANNER */}
            {isPracticeMode && hasSelectedCurrent && (
              <Alert className={`border ${
                isOptionCorrect
                  ? 'border-emerald-300 bg-emerald-50 text-emerald-900'
                  : 'border-amber-300 bg-amber-50 text-amber-900'
              }`}>
                <div className="flex items-start gap-2">
                  {isOptionCorrect ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 mt-0.5 shrink-0" />
                  ) : (
                    <XCircle className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
                  )}
                  <div className="space-y-1 text-xs">
                    <AlertTitle className="font-bold">
                      {isOptionCorrect ? 'Correct Answer' : `Incorrect Choice (Correct Key: ${currentQ.correct_option})`}
                    </AlertTitle>
                    <AlertDescription className="text-xs leading-relaxed text-slate-800">
                      {currentQ.correct_answer_explanation || 'No rationale available for this question.'}
                    </AlertDescription>
                  </div>
                </div>
              </Alert>
            )}
          </CardContent>

          {/* QUESTION FOOTER NAVIGATION */}
          <CardFooter className="p-4 sm:px-6 bg-slate-50/70 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
                disabled={currentIndex === 0}
                className="text-xs h-8.5 border-slate-200 bg-white text-slate-700"
              >
                <ChevronLeft className="h-3.5 w-3.5 mr-1" /> Previous Question
              </Button>

              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setCurrentIndex((prev) => Math.min(totalCount - 1, prev + 1))}
                disabled={currentIndex === totalCount - 1}
                className="text-xs h-8.5 border-slate-200 bg-white text-slate-700"
              >
                Next Question <ChevronRight className="h-3.5 w-3.5 ml-1" />
              </Button>
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
              <Button
                type="button"
                onClick={handleSubmitAll}
                disabled={submitting}
                className="w-full sm:w-auto bg-slate-900 hover:bg-slate-800 text-white text-xs px-5 h-8.5 font-bold shadow-xs"
              >
                {submitting ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 mr-2 animate-spin" />
                    Evaluating 20 Answers...
                  </>
                ) : (
                  <>
                    <FileCheck className="h-3.5 w-3.5 mr-1.5" />
                    Submit Final Interview ({answeredCount}/{totalCount})
                  </>
                )}
              </Button>
            </div>
          </CardFooter>
        </Card>
      </main>
    </div>
  );
}
