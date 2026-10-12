import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getCandidateProfile,
  logoutCandidate,
  getSessionHistory,
  clearSessionHistory,
  CandidateProfile,
  SessionHistoryItem,
} from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';
import { Award, Clock, History, LogOut, LogIn, X, User } from 'lucide-react';

interface CandidateNavHeaderProps {
  candidateProfile?: CandidateProfile | null;
  onLogout?: () => void;
  onLoginClick?: () => void;
}

export const CandidateNavHeader: React.FC<CandidateNavHeaderProps> = ({
  candidateProfile,
  onLogout,
  onLoginClick,
}) => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<CandidateProfile | null>(candidateProfile !== undefined ? candidateProfile : getCandidateProfile());
  const [history, setHistory] = useState<SessionHistoryItem[]>([]);
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  useEffect(() => {
    if (candidateProfile !== undefined) {
      setProfile(candidateProfile);
    } else {
      setProfile(getCandidateProfile());
    }
  }, [candidateProfile]);

  useEffect(() => {
    setHistory(getSessionHistory());
  }, [showHistoryModal]);

  const handleLogout = () => {
    logoutCandidate();
    setProfile(null);
    toast.success('Logged out successfully.');
    if (onLogout) {
      onLogout();
    }
  };

  const handleClearHistory = () => {
    clearSessionHistory();
    setHistory([]);
    toast.info('Interview session history cleared.');
  };

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-border bg-white shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo & Navigation */}
          <div className="flex items-center gap-6">
            <div
              className="flex items-center gap-3 cursor-pointer group"
              onClick={() => navigate('/')}
            >
              <div className="h-9 w-9 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold text-base shadow-sm group-hover:bg-slate-800 transition-colors">
                H
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-base tracking-tight text-slate-900">
                    HireFit
                  </span>
                  <Badge variant="outline" className="text-[10px] py-0 px-2 font-medium bg-slate-50 text-slate-700 border-slate-300">
                    Enterprise
                  </Badge>
                </div>
                <p className="text-[11px] text-slate-500 hidden sm:block">
                  Target Company Hiring & Assessment Platform
                </p>
              </div>
            </div>

            {/* Main Nav Tabs */}
            <nav className="hidden md:flex items-center gap-1 border-l border-slate-200 pl-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/')}
                className="text-xs font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100"
              >
                Target Companies
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/profile')}
                className="text-xs font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100"
              >
                Profile & Resumes
              </Button>
            </nav>
          </div>

          {/* Right Action Bar: Profile, Active Resume, Logout / Login, Past Scorecards */}
          <div className="flex items-center gap-2.5">
            {profile ? (
              <>
                {/* Profile Link & Pill */}
                <div 
                  onClick={() => navigate('/profile')}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-xs cursor-pointer hover:bg-slate-100 transition-colors"
                  title="Manage Candidate Profile & Resumes"
                >
                  <div className="w-5 h-5 rounded-full bg-slate-900 text-white flex items-center justify-center text-[10px] font-bold">
                    {profile.name.charAt(0).toUpperCase()}
                  </div>
                  <span className="font-semibold text-slate-900">{profile.name}</span>
                  <span className="text-slate-400 hidden lg:inline">•</span>
                  <span className="text-slate-500 font-mono text-[11px] hidden lg:inline">{profile.email}</span>
                </div>

                {/* Explicit Logout Button */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="text-xs h-8 text-slate-600 hover:text-red-600 hover:bg-red-50 border border-slate-200"
                >
                  <LogOut className="w-3.5 h-3.5 mr-1 text-slate-500" />
                  Logout
                </Button>
              </>
            ) : (
              /* Explicit Login Button when logged out */
              <Button
                variant="default"
                size="sm"
                onClick={() => navigate('/login')}
                className="text-xs h-8 bg-slate-900 hover:bg-slate-800 text-white font-semibold"
              >
                <LogIn className="w-3.5 h-3.5 mr-1.5" />
                Sign In
              </Button>
            )}

            {/* Past Interviews Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowHistoryModal(true)}
              className="text-xs h-8 border-slate-200 bg-white hover:bg-slate-50 text-slate-800 font-medium"
            >
              <History className="w-3.5 h-3.5 mr-1.5 text-slate-600" />
              Past Scorecards
              {history.length > 0 && (
                <span className="ml-1.5 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-slate-900 text-white">
                  {history.length}
                </span>
              )}
            </Button>
          </div>
        </div>
      </header>

      {/* PAST INTERVIEWS MODAL */}
      {showHistoryModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <Card className="w-full max-w-2xl bg-white border-slate-200 shadow-xl animate-in fade-in zoom-in-95 duration-150">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Award className="w-4 h-4 text-slate-900" />
                  Past Interview Scorecards
                </CardTitle>
                <CardDescription className="text-xs text-slate-500 mt-0.5">
                  Historical simulation results and performance records
                </CardDescription>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowHistoryModal(false)}
                className="h-8 w-8 p-0 rounded-full text-slate-400 hover:text-slate-900"
              >
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            <Separator />
            <CardContent className="pt-4 pb-2">
              {history.length === 0 ? (
                <div className="py-12 text-center space-y-2">
                  <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400">
                    <Clock className="w-5 h-5" />
                  </div>
                  <p className="text-sm font-semibold text-slate-800">No past interviews recorded</p>
                  <p className="text-xs text-slate-500 max-w-sm mx-auto">
                    Select a target company role and complete your 20-question simulation to generate your first scorecard.
                  </p>
                </div>
              ) : (
                <ScrollArea className="h-72 pr-3">
                  <div className="space-y-2.5">
                    {history.map((item) => (
                      <div
                        key={item.sessionId}
                        className="p-3 rounded-lg border border-slate-200 bg-slate-50/60 hover:bg-slate-100/60 transition-colors flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
                      >
                        <div className="space-y-0.5">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-xs text-slate-900">{item.roleTitle}</span>
                            <Badge variant="outline" className="text-[10px] px-1.5 py-0 bg-white text-slate-700 border-slate-300 font-semibold">
                              {item.companyName}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-2 text-[11px] text-slate-500">
                            <span>{new Date(item.createdAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                            {item.overallScore !== undefined && (
                              <>
                                <span>•</span>
                                <span className="font-semibold text-slate-900">Score: {Math.round(item.overallScore)}%</span>
                              </>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          {item.recommendation && (
                            <Badge
                              className={`text-[10px] px-2 py-0.5 font-semibold ${
                                item.recommendation.toLowerCase().includes('strong') || item.recommendation.toLowerCase().includes('hire')
                                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-300'
                                  : 'bg-amber-50 text-amber-700 border border-amber-300'
                              }`}
                            >
                              {item.recommendation}
                            </Badge>
                          )}
                          <Button
                            variant="default"
                            size="sm"
                            onClick={() => {
                              setShowHistoryModal(false);
                              navigate(`/result/${item.sessionId}`);
                            }}
                            className="h-7 text-xs bg-slate-900 text-white hover:bg-slate-800"
                          >
                            View Report
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
            <Separator />
            <CardFooter className="flex items-center justify-between pt-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearHistory}
                disabled={history.length === 0}
                className="text-xs text-slate-500 hover:text-red-600"
              >
                Clear History
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowHistoryModal(false)}
                className="text-xs border-slate-200"
              >
                Close
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}
    </>
  );
};
