import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CandidateNavHeader } from '@/components/CandidateNavHeader';
import { 
  getCurrentUser, 
  updateCandidateDetails, 
  setActiveResume, 
  addCandidateResume, 
  deleteCandidateResume,
  CandidateUser,
  CandidateResume 
} from '@/lib/auth';
import { toast } from 'sonner';
import { 
  User, 
  FileText, 
  Upload, 
  CheckCircle2, 
  Trash2, 
  Star, 
  Eye, 
  Plus, 
  ArrowRight,
  Briefcase,
  Building2,
  Calendar,
  Layers,
  Sparkles,
  X
} from 'lucide-react';

export default function ProfilePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<CandidateUser | null>(getCurrentUser());

  // Form states for profile details
  const [name, setName] = useState(user?.name || '');
  const [title, setTitle] = useState(user?.title || '');
  const [seniority, setSeniority] = useState(user?.targetSeniority || '');

  // Form states for uploading a new resume
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [newResumeFile, setNewResumeFile] = useState<File | null>(null);
  const [newResumeLabel, setNewResumeLabel] = useState('');
  const [newResumeSkills, setNewResumeSkills] = useState('');
  const [uploadLoading, setUploadLoading] = useState(false);

  // Resume Preview Modal State
  const [previewResume, setPreviewResume] = useState<CandidateResume | null>(null);

  const handleUpdateProfile = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      toast.error('Name cannot be empty.');
      return;
    }
    const updated = updateCandidateDetails(name, title, seniority);
    if (updated) {
      setUser({ ...updated });
      toast.success('Candidate profile updated successfully.');
    }
  };

  const handleSetActive = (resumeId: string) => {
    const updated = setActiveResume(resumeId);
    if (updated) {
      setUser({ ...updated });
      toast.success('Active benchmark resume updated.');
    }
  };

  const handleDeleteResume = (resumeId: string) => {
    try {
      const updated = deleteCandidateResume(resumeId);
      if (updated) {
        setUser({ ...updated });
        toast.info('Resume removed from portfolio.');
      }
    } catch (err: any) {
      toast.error(err.message || 'Cannot delete resume.');
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newResumeFile) {
      toast.error('Please choose a resume file to upload.');
      return;
    }

    setUploadLoading(true);
    try {
      // Read file content as text
      const content = await newResumeFile.text();
      const parsedSkills = newResumeSkills
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

      // Default skills extraction if empty
      const fallbackSkills = [
        'Software Architecture',
        'API Design',
        'Data Structures',
        'System Reliability',
      ];

      const skillsToSave = parsedSkills.length > 0 ? parsedSkills : fallbackSkills;
      const labelToSave = newResumeLabel.trim() || newResumeFile.name;
      const sizeKb = Math.round(newResumeFile.size / 1024);

      const updated = addCandidateResume(
        newResumeFile.name,
        content || `Resume Content for ${labelToSave}\nSkills: ${skillsToSave.join(', ')}`,
        labelToSave,
        sizeKb,
        skillsToSave
      );

      if (updated) {
        setUser({ ...updated });
        setNewResumeFile(null);
        setNewResumeLabel('');
        setNewResumeSkills('');
        setShowUploadForm(false);
        toast.success(`Resume "${labelToSave}" uploaded and set as active.`);
      }
    } catch (err: any) {
      console.error(err);
      toast.error('Failed to read and save resume file.');
    } finally {
      setUploadLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
        <CandidateNavHeader />
        <div className="flex-1 flex items-center justify-center p-6">
          <Card className="max-w-md w-full text-center p-8 bg-white border-slate-200">
            <h2 className="text-lg font-bold text-slate-900">Sign in to view your Profile</h2>
            <p className="text-xs text-slate-500 mt-2 mb-6">
              Create an account or use Demo candidate access to manage multiple resumes.
            </p>
            <Button
              onClick={() => navigate('/login')}
              className="bg-slate-900 text-white font-semibold h-9 text-xs"
            >
              Go to Candidate Sign In
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  const activeResume = user.resumes.find((r) => r.isActive) || user.resumes[0];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-16 font-sans">
      <CandidateNavHeader />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        
        {/* HEADER SECTION */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 text-xs font-semibold">
              <User className="w-3.5 h-3.5 text-slate-900" />
              Candidate Profile & Portfolio
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 mt-1">
              Personal Details & Multi-Resume Manager
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              Maintain separate CV variants (e.g. Distributed Systems vs ML vs Product). The selected active resume is dynamically benchmarked against all employer rubrics.
            </p>
          </div>

          <Button
            onClick={() => navigate('/')}
            className="h-9 text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white self-start sm:self-auto shrink-0"
          >
            <Building2 className="w-3.5 h-3.5 mr-1.5" />
            Browse Target Companies <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Button>
        </div>

        {/* 1. PERSONAL DETAILS CARD */}
        <Card className="bg-white border-slate-200 shadow-xs">
          <CardHeader className="pb-3 pt-5 px-6">
            <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-slate-900" />
              Professional Identity
            </CardTitle>
            <CardDescription className="text-xs text-slate-500">
              Identity parameters calibrated into your interview scorecards and reports.
            </CardDescription>
          </CardHeader>
          <CardContent className="px-6 py-2">
            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="space-y-1.5">
                  <Label htmlFor="prof-name" className="text-xs font-semibold text-slate-700">
                    Full Name
                  </Label>
                  <Input
                    id="prof-name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="h-9 text-xs border-slate-300"
                    required
                  />
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="prof-email" className="text-xs font-semibold text-slate-700">
                    Email Address
                  </Label>
                  <Input
                    id="prof-email"
                    value={user.email}
                    disabled
                    className="h-9 text-xs border-slate-200 bg-slate-50 text-slate-500 cursor-not-allowed"
                  />
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="prof-title" className="text-xs font-semibold text-slate-700">
                    Professional Title
                  </Label>
                  <Input
                    id="prof-title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g. Senior Software Engineer"
                    className="h-9 text-xs border-slate-300"
                  />
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="prof-level" className="text-xs font-semibold text-slate-700">
                    Target Seniority
                  </Label>
                  <Input
                    id="prof-level"
                    value={seniority}
                    onChange={(e) => setSeniority(e.target.value)}
                    placeholder="e.g. Senior (IC5 / L5)"
                    className="h-9 text-xs border-slate-300"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <Button
                  type="submit"
                  size="sm"
                  className="h-8 text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white"
                >
                  Save Profile Details
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* 2. MULTI-RESUME PORTFOLIO CARD */}
        <Card className="bg-white border-slate-200 shadow-xs">
          <CardHeader className="pb-3 pt-5 px-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-slate-900" />
                  Multi-Resume Portfolio ({user.resumes.length})
                </CardTitle>
                <Badge variant="outline" className="text-[10px] font-semibold bg-slate-50 text-slate-700 border-slate-300">
                  Active: {activeResume ? activeResume.label : 'None'}
                </Badge>
              </div>
              <CardDescription className="text-xs text-slate-500 mt-0.5">
                Switch which resume represents your candidacy for company evaluations with a single click.
              </CardDescription>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowUploadForm(!showUploadForm)}
              className="h-8 text-xs font-semibold border-slate-200 hover:bg-slate-50 text-slate-900 self-start sm:self-auto"
            >
              <Plus className="w-3.5 h-3.5 mr-1" />
              {showUploadForm ? 'Cancel Upload' : 'Upload Another Resume'}
            </Button>
          </CardHeader>

          <CardContent className="px-6 py-4 space-y-6">
            {/* Collapsible Upload Form */}
            {showUploadForm && (
              <form 
                onSubmit={handleFileUpload}
                className="p-4 rounded-lg border border-slate-300 bg-slate-50/80 space-y-4 animate-in fade-in duration-150"
              >
                <div className="space-y-1">
                  <h4 className="text-xs font-bold text-slate-900">Upload New Resume File</h4>
                  <p className="text-[11px] text-slate-500">
                    Supports .pdf, .docx, and .txt files up to 5MB. Newly uploaded resumes become the active benchmark automatically.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="new-file" className="text-xs font-semibold text-slate-700">
                      Resume File (.txt, .pdf, .docx)
                    </Label>
                    <Input
                      id="new-file"
                      type="file"
                      accept=".txt,.pdf,.docx"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          setNewResumeFile(e.target.files[0]);
                          if (!newResumeLabel) {
                            setNewResumeLabel(e.target.files[0].name.replace(/\.[^/.]+$/, ''));
                          }
                        }
                      }}
                      required
                      className="h-9 text-xs bg-white border-slate-300"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="new-label" className="text-xs font-semibold text-slate-700">
                      Portfolio Label
                    </Label>
                    <Input
                      id="new-label"
                      placeholder="e.g. Distributed Infrastructure Resume"
                      value={newResumeLabel}
                      onChange={(e) => setNewResumeLabel(e.target.value)}
                      className="h-9 text-xs bg-white border-slate-300"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="new-skills" className="text-xs font-semibold text-slate-700">
                    Key Technical Competencies (Comma-separated)
                  </Label>
                  <Input
                    id="new-skills"
                    placeholder="e.g. Python, FastAPI, Distributed Systems, Redis, Kafka, PostgreSQL, Docker"
                    value={newResumeSkills}
                    onChange={(e) => setNewResumeSkills(e.target.value)}
                    className="h-9 text-xs bg-white border-slate-300"
                  />
                  <p className="text-[10px] text-slate-500">
                    Used to calculate match percentages against target employer competencies.
                  </p>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowUploadForm(false)}
                    className="h-8 text-xs text-slate-600"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    size="sm"
                    disabled={uploadLoading || !newResumeFile}
                    className="h-8 text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white"
                  >
                    {uploadLoading ? 'Uploading...' : 'Save and Set as Active'}
                  </Button>
                </div>
              </form>
            )}

            {/* List of resumes */}
            <div className="space-y-3">
              {user.resumes.map((resume) => {
                const isActive = resume.isActive;

                return (
                  <div
                    key={resume.id}
                    className={`p-4 rounded-xl border transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
                      isActive 
                        ? 'border-slate-900 bg-slate-50/70 shadow-xs' 
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
                  >
                    {/* Resume Info */}
                    <div className="space-y-1.5 flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <FileText className={`w-4 h-4 ${isActive ? 'text-slate-900' : 'text-slate-500'}`} />
                        <span className="font-bold text-sm text-slate-900 truncate">
                          {resume.label}
                        </span>
                        {isActive ? (
                          <Badge className="text-[10px] py-0 px-2 font-bold bg-slate-900 text-white border-slate-900">
                            Active Benchmark CV
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="text-[10px] py-0 px-1.5 bg-white text-slate-500 border-slate-200">
                            Standby
                          </Badge>
                        )}
                      </div>

                      <div className="flex items-center gap-3 text-[11px] text-slate-500 flex-wrap">
                        <span className="font-mono text-slate-600">{resume.filename}</span>
                        <span>•</span>
                        <span>{resume.sizeKb} KB</span>
                        <span>•</span>
                        <span>Uploaded {resume.uploadedAt}</span>
                      </div>

                      {/* Skills Tags */}
                      <div className="flex flex-wrap gap-1 pt-1">
                        {resume.skills.map((skill, sIdx) => (
                          <Badge
                            key={sIdx}
                            variant="outline"
                            className="text-[10px] py-0 px-1.5 bg-white text-slate-700 border-slate-200"
                          >
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Actions: Set as Active, Preview, Delete */}
                    <div className="flex items-center gap-2 shrink-0 self-end md:self-center">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPreviewResume(resume)}
                        className="h-8 text-xs border-slate-200 text-slate-700 hover:bg-slate-50"
                      >
                        <Eye className="w-3.5 h-3.5 mr-1 text-slate-500" />
                        Preview
                      </Button>

                      {!isActive ? (
                        <Button
                          variant="default"
                          size="sm"
                          onClick={() => handleSetActive(resume.id)}
                          className="h-8 text-xs bg-slate-900 hover:bg-slate-800 text-white font-semibold"
                        >
                          <Star className="w-3.5 h-3.5 mr-1" />
                          Set as Active
                        </Button>
                      ) : (
                        <div className="h-8 px-2.5 flex items-center gap-1 text-xs font-semibold text-slate-900 bg-slate-200/70 rounded-md">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Current Active
                        </div>
                      )}

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteResume(resume.id)}
                        disabled={user.resumes.length <= 1}
                        className="h-8 w-8 p-0 text-slate-400 hover:text-red-600 hover:bg-red-50 disabled:opacity-30"
                        title={user.resumes.length <= 1 ? 'At least one resume must remain' : 'Delete resume'}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
          <CardFooter className="bg-slate-50/50 border-t border-slate-100 py-3 px-6 flex items-center justify-between">
            <span className="text-[11px] text-slate-500">
              Active resume is automatically passed to company interview calibrators.
            </span>
            <Button
              variant="default"
              size="sm"
              onClick={() => navigate('/')}
              className="h-8 text-xs bg-slate-900 hover:bg-slate-800 text-white font-semibold"
            >
              Test Readiness Against Employers <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </CardFooter>
        </Card>

      </main>

      {/* PREVIEW RESUME MODAL */}
      {previewResume && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <Card className="w-full max-w-2xl bg-white border-slate-200 shadow-xl animate-in fade-in zoom-in-95 duration-150">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-slate-900" />
                  {previewResume.label}
                </CardTitle>
                <CardDescription className="text-xs text-slate-500 mt-0.5">
                  Filename: {previewResume.filename} • {previewResume.sizeKb} KB
                </CardDescription>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setPreviewResume(null)}
                className="h-8 w-8 p-0 rounded-full text-slate-400 hover:text-slate-900"
              >
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            <Separator />
            <CardContent className="pt-4 pb-2">
              <ScrollArea className="h-80 pr-3">
                <pre className="text-xs font-mono text-slate-800 whitespace-pre-wrap leading-relaxed p-3 bg-slate-50 rounded-lg border border-slate-200">
                  {previewResume.content}
                </pre>
              </ScrollArea>
            </CardContent>
            <Separator />
            <CardFooter className="flex items-center justify-between pt-3">
              <Badge variant="outline" className="text-xs bg-slate-50 border-slate-300 text-slate-700">
                Skills: {previewResume.skills.join(', ')}
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPreviewResume(null)}
                className="h-8 text-xs border-slate-200 text-slate-800"
              >
                Close Preview
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}

    </div>
  );
}
