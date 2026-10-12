import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CandidateNavHeader } from '@/components/CandidateNavHeader';
import { getCurrentUser, loginUser, registerUser, DEMO_USER } from '@/lib/auth';
import { toast } from 'sonner';
import { LogIn, UserPlus, CheckCircle2, ShieldCheck, ArrowRight, Sparkles, Building2, Briefcase } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const existingUser = getCurrentUser();

  const [activeTab, setActiveTab] = useState<'signin' | 'register'>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [title, setTitle] = useState('Senior Software Engineer');
  const [seniority, setSeniority] = useState('Senior (IC5 / L5)');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const redirectTo = (location.state as any)?.from || '/';

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email.trim() || !email.includes('@')) {
      setError('Please enter a valid email address.');
      return;
    }
    setLoading(true);
    try {
      const user = loginUser(email, name);
      toast.success(`Welcome back, ${user.name}`);
      navigate(redirectTo);
    } catch (err: any) {
      setError('Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!name.trim()) {
      setError('Full name is required.');
      return;
    }
    if (!email.trim() || !email.includes('@')) {
      setError('Please enter a valid email address.');
      return;
    }
    setLoading(true);
    try {
      const user = registerUser(name, email, title, seniority);
      toast.success(`Account created successfully. Welcome, ${user.name}`);
      navigate(redirectTo);
    } catch (err: any) {
      setError('Failed to create account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoSignIn = () => {
    setLoading(true);
    try {
      const user = loginUser(DEMO_USER.email, DEMO_USER.name);
      toast.success(`Logged in with Demo Candidate profile (${user.name})`);
      navigate(redirectTo);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <CandidateNavHeader />

      <main className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-md space-y-6">
          {/* Header Brand */}
          <div className="text-center space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-slate-200 bg-white text-xs font-semibold text-slate-700 shadow-xs">
              <ShieldCheck className="w-3.5 h-3.5 text-slate-900" />
              Enterprise Candidate Assessment Portal
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Welcome to HireFit
            </h1>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Target company technical & aptitude evaluation calibrated against real hiring rubrics.
            </p>
          </div>

          {/* If already logged in banner */}
          {existingUser && (
            <Alert className="border-slate-200 bg-white text-slate-800 shadow-xs">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <div className="flex-1">
                <AlertDescription className="text-xs text-slate-600">
                  Signed in as <span className="font-semibold text-slate-900">{existingUser.name}</span> ({existingUser.email}).
                </AlertDescription>
                <div className="mt-2 flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => navigate('/')}
                    className="h-7 text-xs bg-slate-900 hover:bg-slate-800 text-white"
                  >
                    Go to Target Companies <ArrowRight className="w-3 h-3 ml-1" />
                  </Button>
                </div>
              </div>
            </Alert>
          )}

          {/* Auth Card */}
          <Card className="border-slate-200 bg-white shadow-sm">
            <CardHeader className="pb-3 pt-5 px-6">
              <Tabs
                value={activeTab}
                onValueChange={(val) => {
                  setError(null);
                  setActiveTab(val as 'signin' | 'register');
                }}
                className="w-full"
              >
                <TabsList className="grid grid-cols-2 w-full bg-slate-100 p-0.5">
                  <TabsTrigger
                    value="signin"
                    className="text-xs font-semibold data-[state=active]:bg-white data-[state=active]:text-slate-900 shadow-none"
                  >
                    <LogIn className="w-3.5 h-3.5 mr-1.5" />
                    Sign In
                  </TabsTrigger>
                  <TabsTrigger
                    value="register"
                    className="text-xs font-semibold data-[state=active]:bg-white data-[state=active]:text-slate-900 shadow-none"
                  >
                    <UserPlus className="w-3.5 h-3.5 mr-1.5" />
                    Create Account
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </CardHeader>

            <CardContent className="px-6 pt-2 pb-6">
              {error && (
                <div className="mb-4 p-2.5 rounded-lg border border-red-200 bg-red-50 text-red-700 text-xs">
                  {error}
                </div>
              )}

              {activeTab === 'signin' ? (
                <form onSubmit={handleSignIn} className="space-y-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="signin-email" className="text-xs font-semibold text-slate-700">
                      Email Address
                    </Label>
                    <Input
                      id="signin-email"
                      type="email"
                      placeholder="e.g. alex.johnson@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="h-9 text-xs border-slate-300 focus-visible:ring-slate-900"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="signin-password" className="text-xs font-semibold text-slate-700">
                        Password
                      </Label>
                      <span className="text-[11px] text-slate-400">Default: any value</span>
                    </div>
                    <Input
                      id="signin-password"
                      type="password"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="h-9 text-xs border-slate-300 focus-visible:ring-slate-900"
                    />
                  </div>

                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full h-9 text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white"
                  >
                    <LogIn className="w-3.5 h-3.5 mr-1.5" />
                    Sign In to Candidate Portal
                  </Button>
                </form>
              ) : (
                <form onSubmit={handleRegister} className="space-y-3.5">
                  <div className="space-y-1.5">
                    <Label htmlFor="reg-name" className="text-xs font-semibold text-slate-700">
                      Full Name
                    </Label>
                    <Input
                      id="reg-name"
                      type="text"
                      placeholder="e.g. Alex Johnson"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                      className="h-9 text-xs border-slate-300 focus-visible:ring-slate-900"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="reg-email" className="text-xs font-semibold text-slate-700">
                      Work / Personal Email
                    </Label>
                    <Input
                      id="reg-email"
                      type="email"
                      placeholder="alex.johnson@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="h-9 text-xs border-slate-300 focus-visible:ring-slate-900"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2.5">
                    <div className="space-y-1.5">
                      <Label htmlFor="reg-title" className="text-xs font-semibold text-slate-700">
                        Professional Title
                      </Label>
                      <Input
                        id="reg-title"
                        type="text"
                        placeholder="Backend Engineer"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        className="h-9 text-xs border-slate-300"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="reg-level" className="text-xs font-semibold text-slate-700">
                        Target Level
                      </Label>
                      <Input
                        id="reg-level"
                        type="text"
                        placeholder="Senior (IC5 / L5)"
                        value={seniority}
                        onChange={(e) => setSeniority(e.target.value)}
                        className="h-9 text-xs border-slate-300"
                      />
                    </div>
                  </div>

                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full h-9 text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white mt-1"
                  >
                    <UserPlus className="w-3.5 h-3.5 mr-1.5" />
                    Register Candidate Profile
                  </Button>
                </form>
              )}

              <div className="mt-5 space-y-3">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <Separator className="w-full border-slate-200" />
                  </div>
                  <div className="relative flex justify-center text-[11px] uppercase">
                    <span className="bg-white px-2 text-slate-400 font-medium tracking-wider">
                      Or Quick Demo Access
                    </span>
                  </div>
                </div>

                <Button
                  type="button"
                  variant="outline"
                  onClick={handleDemoSignIn}
                  disabled={loading}
                  className="w-full h-9 text-xs font-semibold border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-800"
                >
                  <Briefcase className="w-3.5 h-3.5 mr-1.5 text-slate-600" />
                  One-Click Demo Candidate (Alex Johnson)
                </Button>
              </div>
            </CardContent>

            <CardFooter className="bg-slate-50/60 border-t border-slate-100 py-3 px-6 flex justify-center">
              <p className="text-[11px] text-slate-500 text-center">
                Preloaded with 3 verified resumes (Backend, ML, FullStack) and benchmark datasets.
              </p>
            </CardFooter>
          </Card>
        </div>
      </main>
    </div>
  );
}
