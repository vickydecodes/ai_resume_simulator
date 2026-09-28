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
import { getInterviewResult, EvaluationReport } from '@/lib/api';
import { Award, CheckCircle2, AlertTriangle, Lightbulb, RotateCcw, AlertCircle, Building2, Briefcase, User } from 'lucide-react';
import { toast } from 'sonner';

export default function ResultPage() {
  const { id: sessionId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState<EvaluationReport | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    const fetchResult = async () => {
      try {
        setLoading(true);
        const data = await getInterviewResult(sessionId);
        setReport(data);
      } catch (err: any) {
        toast.error('Failed to load evaluation report.');
      } finally {
        setLoading(false);
      }
    };

    fetchResult();
  }, [sessionId]);

  if (loading || !report) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50">
        <Card className="w-full max-w-3xl p-6 space-y-4">
          <Skeleton className="h-8 w-1/2" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-40 w-full" />
        </Card>
      </div>
    );
  }

  const {
    candidate_name,
    role_title,
    company_name,
    overall_score,
    estimated_selection_probability,
    category_scores,
    top_strengths,
    top_weaknesses,
    improvement_tips,
    disclaimer
  } = report;

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8 flex flex-col items-center">
      <div className="w-full max-w-4xl space-y-6">
        {/* Header Summary Card */}
        <Card className="shadow-sm border-slate-200">
          <CardHeader>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center space-x-2 text-xs font-semibold text-slate-500 mb-1">
                  <User className="h-3.5 w-3.5" />
                  <span>Candidate: {candidate_name}</span>
                </div>
                <CardTitle className="text-2xl font-bold text-slate-900 flex items-center">
                  <Award className="h-6 w-6 mr-2 text-slate-900" />
                  Interview Evaluation & Performance Report
                </CardTitle>
                <CardDescription className="flex items-center space-x-3 mt-1 text-slate-600">
                  <span className="flex items-center"><Briefcase className="h-3.5 w-3.5 mr-1" /> {role_title}</span>
                  <span>•</span>
                  <span className="flex items-center"><Building2 className="h-3.5 w-3.5 mr-1" /> {company_name}</span>
                </CardDescription>
              </div>
              <Button onClick={() => navigate('/')} variant="outline" size="sm">
                <RotateCcw className="mr-1.5 h-4 w-4" /> Start New Interview
              </Button>
            </div>
          </CardHeader>
        </Card>

        {/* Core Metric Badges */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="p-6 bg-white shadow-sm border-slate-200 flex flex-col justify-between">
            <div>
              <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">Overall Performance Score</span>
              <div className="flex items-baseline space-x-2 mt-2">
                <span className="text-5xl font-extrabold text-slate-900">{overall_score}</span>
                <span className="text-lg font-semibold text-slate-400">/ 100</span>
              </div>
            </div>
            <Progress value={overall_score} className="h-2.5 mt-4" />
          </Card>

          <Card className="p-6 bg-slate-900 text-white shadow-sm border-slate-900 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase text-slate-300 tracking-wider">Estimated Selection Probability</span>
                <Badge variant="secondary" className="bg-slate-800 text-slate-100 border-slate-700">Calibrated</Badge>
              </div>
              <div className="flex items-baseline space-x-2 mt-2">
                <span className="text-5xl font-extrabold text-white">{estimated_selection_probability}%</span>
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-4">
              Estimated competitiveness in a target company hiring loop.
            </p>
          </Card>
        </div>

        {/* Disclaimer Alert */}
        <Alert className="bg-amber-50 border-amber-200 text-amber-900">
          <AlertCircle className="h-4 w-4 text-amber-700" />
          <AlertTitle className="font-semibold text-amber-900">Algorithmic Estimation Disclaimer</AlertTitle>
          <AlertDescription className="text-xs text-amber-800 leading-relaxed">
            {disclaimer}
          </AlertDescription>
        </Alert>

        {/* Category Breakdown & Feedback Tabs */}
        <Card className="shadow-sm border-slate-200">
          <CardHeader>
            <CardTitle className="text-lg font-bold">Detailed Performance Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="breakdown" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="breakdown">Category Scores</TabsTrigger>
                <TabsTrigger value="strengths">Strengths & Gaps</TabsTrigger>
                <TabsTrigger value="remediation">Improvement Plan</TabsTrigger>
              </TabsList>

              {/* Tab 1: Category Scores */}
              <TabsContent value="breakdown" className="space-y-4 pt-4">
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm font-medium mb-1">
                      <span className="text-slate-700">Resume-Role Fit (25%)</span>
                      <span className="font-bold">{category_scores.resume_fit}%</span>
                    </div>
                    <Progress value={category_scores.resume_fit} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm font-medium mb-1">
                      <span className="text-slate-700">Technical Knowledge (35%)</span>
                      <span className="font-bold">{category_scores.technical_knowledge}%</span>
                    </div>
                    <Progress value={category_scores.technical_knowledge} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm font-medium mb-1">
                      <span className="text-slate-700">Communication Clarity (15%)</span>
                      <span className="font-bold">{category_scores.communication}%</span>
                    </div>
                    <Progress value={category_scores.communication} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm font-medium mb-1">
                      <span className="text-slate-700">Problem Solving & Architecture (15%)</span>
                      <span className="font-bold">{category_scores.problem_solving}%</span>
                    </div>
                    <Progress value={category_scores.problem_solving} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm font-medium mb-1">
                      <span className="text-slate-700">Company & Product Awareness (10%)</span>
                      <span className="font-bold">{category_scores.company_awareness}%</span>
                    </div>
                    <Progress value={category_scores.company_awareness} className="h-2" />
                  </div>
                </div>
              </TabsContent>

              {/* Tab 2: Strengths & Weaknesses */}
              <TabsContent value="strengths" className="space-y-4 pt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2 border border-slate-200 rounded-lg p-4 bg-slate-50">
                    <h4 className="text-sm font-bold text-emerald-800 flex items-center">
                      <CheckCircle2 className="h-4 w-4 mr-1.5 text-emerald-600" /> Key Strengths
                    </h4>
                    <ul className="space-y-1.5 text-xs text-slate-700 list-disc list-inside">
                      {top_strengths.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="space-y-2 border border-slate-200 rounded-lg p-4 bg-slate-50">
                    <h4 className="text-sm font-bold text-rose-800 flex items-center">
                      <AlertTriangle className="h-4 w-4 mr-1.5 text-rose-600" /> Identified Weaknesses
                    </h4>
                    <ul className="space-y-1.5 text-xs text-slate-700 list-disc list-inside">
                      {top_weaknesses.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </TabsContent>

              {/* Tab 3: Improvement Plan */}
              <TabsContent value="remediation" className="space-y-4 pt-4">
                <div className="border border-slate-200 rounded-lg p-4 bg-slate-50 space-y-3">
                  <h4 className="text-sm font-bold text-slate-900 flex items-center">
                    <Lightbulb className="h-4 w-4 mr-1.5 text-amber-500" /> Concrete Improvement Tips
                  </h4>
                  <div className="space-y-2">
                    {improvement_tips.map((tip, idx) => (
                      <div key={idx} className="flex items-start space-x-2 text-xs text-slate-700">
                        <span className="font-bold text-slate-900 min-w-[20px]">{idx + 1}.</span>
                        <span>{tip}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
          <CardFooter className="bg-slate-50 border-t border-slate-200 flex justify-between items-center py-3">
            <span className="text-xs text-slate-500">Session ID: {sessionId}</span>
            <Button onClick={() => navigate('/')} size="sm">
              Practice Another Role
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
