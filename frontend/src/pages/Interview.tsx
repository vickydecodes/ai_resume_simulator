import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { startInterview, submitAnswer, QuestionResponse } from '@/lib/api';
import { Send, Loader2, Bot, User, HelpCircle } from 'lucide-react';
import { toast } from 'sonner';

interface MessageTurn {
  question: string;
  answer?: string;
  topic: string;
  difficulty: number;
}

export default function InterviewPage() {
  const { id: sessionId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState<QuestionResponse | null>(null);
  const [history, setHistory] = useState<MessageTurn[]>([]);
  const [answerText, setAnswerText] = useState('');

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sessionId) return;

    const init = async () => {
      try {
        setLoading(true);
        const q1 = await startInterview(sessionId);
        setCurrentQuestion(q1);
      } catch (err: any) {
        toast.error('Failed to start interview loop.');
      } finally {
        setLoading(false);
      }
    };

    init();
  }, [sessionId]);

  const handleSubmitAnswer = async () => {
    if (!sessionId || !currentQuestion || !answerText.trim() || submitting) return;

    const textToSubmit = answerText.trim();
    setSubmitting(true);

    try {
      // Append answer to history turn log
      const newTurn: MessageTurn = {
        question: currentQuestion.question,
        answer: textToSubmit,
        topic: currentQuestion.topic,
        difficulty: currentQuestion.difficulty,
      };

      setHistory((prev) => [...prev, newTurn]);
      setAnswerText('');

      const nextResp = await submitAnswer(sessionId, textToSubmit);

      if (nextResp.is_final) {
        toast.success('Interview loop completed! Compiling comprehensive evaluation report...');
        navigate(`/result/${sessionId}`);
        return;
      }

      setCurrentQuestion(nextResp);
    } catch (err: any) {
      toast.error('Failed to submit answer. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmitAnswer();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50">
        <Card className="w-full max-w-3xl p-6 space-y-4">
          <Skeleton className="h-6 w-1/3" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-10 w-full" />
        </Card>
      </div>
    );
  }

  const turnNumber = currentQuestion?.turn_number || 1;
  const totalPlanned = currentQuestion?.total_questions || 8;
  const progressPercent = Math.min(100, Math.round((turnNumber / totalPlanned) * 100));

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8 flex flex-col items-center">
      <div className="w-full max-w-4xl space-y-4">
        {/* Header Progress Card */}
        <Card className="p-4 shadow-sm border-slate-200">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 mb-2">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Mock Technical Interview Loop</h2>
              <p className="text-xs text-slate-500">
                Single-Question Adaptive Engine • Answer clearly and concisely
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="bg-slate-100">
                Topic: {currentQuestion?.topic || 'General'}
              </Badge>
              <Badge variant="secondary">
                Difficulty: {currentQuestion?.difficulty || 3} / 5
              </Badge>
            </div>
          </div>
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-slate-500 font-medium">
              <span>Progress: Turn {turnNumber} of {totalPlanned}</span>
              <span>{progressPercent}% Complete</span>
            </div>
            <Progress value={progressPercent} className="h-2" />
          </div>
        </Card>

        {/* Chat History & Active Question Container */}
        <Card className="shadow-md border-slate-200 flex flex-col h-[580px]">
          <CardHeader className="py-3 px-4 bg-slate-100 border-b border-slate-200">
            <CardTitle className="text-sm font-semibold text-slate-700 flex items-center">
              <Bot className="h-4 w-4 mr-2 text-slate-900" />
              Interview Dialogue Session
            </CardTitle>
          </CardHeader>

          <ScrollArea className="flex-1 p-4" ref={scrollRef}>
            <div className="space-y-6">
              {/* Prior Turn History */}
              {history.map((turn, idx) => (
                <div key={idx} className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="bg-slate-900 text-white rounded-full p-1.5 mt-0.5">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="bg-slate-100 border border-slate-200 rounded-lg p-3 max-w-[85%] text-sm text-slate-900">
                      <div className="text-xs font-semibold text-slate-500 mb-1">
                        Question {idx + 1} ({turn.topic})
                      </div>
                      {turn.question}
                    </div>
                  </div>

                  {turn.answer && (
                    <div className="flex items-start justify-end space-x-3">
                      <div className="bg-slate-900 text-white border border-slate-800 rounded-lg p-3 max-w-[85%] text-sm">
                        <div className="text-xs font-semibold text-slate-300 mb-1">Candidate Answer</div>
                        {turn.answer}
                      </div>
                      <div className="bg-slate-200 text-slate-700 rounded-full p-1.5 mt-0.5">
                        <User className="h-4 w-4" />
                      </div>
                    </div>
                  )}
                  <Separator className="my-2" />
                </div>
              ))}

              {/* Active Current Question Box */}
              {currentQuestion && (
                <div className="flex items-start space-x-3">
                  <div className="bg-slate-900 text-white rounded-full p-1.5 mt-0.5">
                    <HelpCircle className="h-4 w-4" />
                  </div>
                  <div className="bg-white border-2 border-slate-900 rounded-lg p-4 max-w-[90%] shadow-sm text-slate-900">
                    <div className="text-xs font-bold text-slate-900 mb-1 flex items-center justify-between">
                      <span>Active Question (Turn {currentQuestion.turn_number})</span>
                      <Badge variant="outline" className="text-[10px] py-0">
                        {currentQuestion.topic}
                      </Badge>
                    </div>
                    <p className="text-base font-medium leading-relaxed">
                      {currentQuestion.question}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Answer Input Area */}
          <CardFooter className="p-3 bg-slate-50 border-t border-slate-200 flex flex-col space-y-2">
            <div className="w-full relative">
              <Textarea
                placeholder="Type your response here... (Press Cmd+Enter or Ctrl+Enter to submit)"
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={submitting}
                className="pr-24 min-h-[90px] bg-white resize-none"
              />
              <Button
                onClick={handleSubmitAnswer}
                disabled={submitting || !answerText.trim()}
                className="absolute right-3 bottom-3"
                size="sm"
              >
                {submitting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    Submit <Send className="ml-1.5 h-3.5 w-3.5" />
                  </>
                )}
              </Button>
            </div>
            <div className="flex justify-between items-center w-full text-[11px] text-slate-400">
              <span>Pro-tip: Include specific examples and technical trade-offs.</span>
              <span>Cmd/Ctrl + Enter to send</span>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
