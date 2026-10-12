import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { CandidateNavHeader } from '@/components/CandidateNavHeader';
import { getCurrentUser, getActiveResume } from '@/lib/auth';
import { 
  getAllCompanies, 
  saveCustomCompanyToStorage, 
  calculateResumeReadiness, 
  CompanyProfile 
} from '@/lib/companies';
import { scrapeCompanyProfile } from '@/lib/api';
import { toast } from 'sonner';
import { 
  Building2, 
  Search, 
  ArrowRight, 
  CheckCircle2, 
  FileText, 
  Plus,
  Loader2,
  DollarSign,
  Globe,
  TrendingUp,
  X,
  Compass
} from 'lucide-react';

export default function HomePage() {
  const navigate = useNavigate();
  const user = getCurrentUser();
  const activeResume = getActiveResume(user);

  const [companiesList, setCompaniesList] = useState<CompanyProfile[]>(getAllCompanies());
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTrack, setSelectedTrack] = useState<string>('all');

  // Scrape Company Modal State
  const [showScrapeModal, setShowScrapeModal] = useState(false);
  const [scrapeNameInput, setScrapeNameInput] = useState('');
  const [scrapeUrlInput, setScrapeUrlInput] = useState('');
  const [isScraping, setIsScraping] = useState(false);
  const [scrapeError, setScrapeError] = useState<string | null>(null);

  // Sync on mount
  useEffect(() => {
    setCompaniesList(getAllCompanies());
  }, []);

  const handleScrapeCompany = async (e: React.FormEvent) => {
    e.preventDefault();
    setScrapeError(null);

    const name = scrapeNameInput.trim();
    if (!name) {
      setScrapeError('Please enter a company name (e.g. Netflix, Databricks, Uber).');
      return;
    }

    setIsScraping(true);
    try {
      toast.info(`Scraping profile and estimating worth for ${name} via BeautifulSoup...`);
      const scraped = await scrapeCompanyProfile(name, scrapeUrlInput.trim() || undefined);

      // Save to localStorage & directory
      const updated = saveCustomCompanyToStorage(scraped as CompanyProfile);
      setCompaniesList(updated);

      toast.success(`Successfully analyzed ${scraped.name}! Valuation: ${scraped.estimatedWorth}`);
      setShowScrapeModal(false);
      setScrapeNameInput('');
      setScrapeUrlInput('');

      // Navigate to the newly scraped company page!
      navigate(`/company/${scraped.id}`);
    } catch (err: any) {
      console.error(err);
      setScrapeError(err.message || 'Failed to scrape company intelligence. Please verify the name or website.');
      toast.error('Scraping failed. Please check inputs.');
    } finally {
      setIsScraping(false);
    }
  };

  // Filter companies based on search and track
  const filteredCompanies = companiesList.filter((company) => {
    const matchesSearch = 
      company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      company.industry.toLowerCase().includes(searchTerm.toLowerCase()) ||
      company.competencies.some((c) => c.toLowerCase().includes(searchTerm.toLowerCase())) ||
      company.roles.some((r) => r.title.toLowerCase().includes(searchTerm.toLowerCase()));

    if (!matchesSearch) return false;

    if (selectedTrack === 'all') return true;
    return company.roles.some((r) => r.track === selectedTrack);
  });

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-16 font-sans">
      <CandidateNavHeader />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        
        {/* EXECUTIVE BANNER */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 text-xs font-semibold">
              <Building2 className="w-3.5 h-3.5 text-slate-900" />
              Target Company Directory & Web Scraper
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
              Benchmark Your Candidacy Against Top Companies
            </h1>
            <p className="text-sm text-slate-600 leading-relaxed">
              Explore pre-calibrated enterprise employers or <strong>search and scrape any custom company</strong> using BeautifulSoup to extract their market worth, engineering culture, and 20-question hiring rubric.
            </p>
          </div>

          {/* Active Resume Quick Snapshot Card */}
          <div className="bg-slate-50 rounded-lg border border-slate-200 p-4 min-w-[280px] space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                Active Benchmark Resume
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/profile')}
                className="h-6 text-[11px] text-slate-900 font-semibold p-0 hover:bg-transparent hover:underline"
              >
                Change CV
              </Button>
            </div>
            
            {activeResume ? (
              <div>
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-slate-900 shrink-0" />
                  <span className="text-xs font-bold text-slate-900 truncate" title={activeResume.label}>
                    {activeResume.label}
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {activeResume.skills.slice(0, 3).map((s, idx) => (
                    <Badge key={idx} variant="outline" className="text-[10px] py-0 px-1.5 bg-white text-slate-700 border-slate-200">
                      {s}
                    </Badge>
                  ))}
                  {activeResume.skills.length > 3 && (
                    <span className="text-[10px] text-slate-400 self-center">
                      +{activeResume.skills.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-xs text-slate-500">
                No resume selected.{' '}
                <span 
                  onClick={() => navigate('/profile')} 
                  className="text-slate-900 font-bold underline cursor-pointer"
                >
                  Upload one in profile
                </span>
              </div>
            )}
          </div>
        </div>

        {/* SEARCH & ACTIONS BAR */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          {/* Search Box */}
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <Input
              placeholder="Search companies, valuation, or skills (e.g. Google, Databricks, Kafka)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 h-10 text-xs bg-white border-slate-200 focus-visible:ring-slate-900 shadow-xs"
            />
          </div>

          <div className="flex items-center gap-2">
            {/* Scrape New Company Action Button */}
            <Button
              onClick={() => setShowScrapeModal(true)}
              className="h-10 text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white shrink-0 shadow-xs"
            >
              <Plus className="w-3.5 h-3.5 mr-1.5" />
              Scrape & Add Any Company
            </Button>
          </div>
        </div>

        {/* Track Filter Buttons */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
          {[
            { id: 'all', label: 'All Companies' },
            { id: 'tech', label: 'Engineering' },
            { id: 'data', label: 'Data & AI' },
            { id: 'pm', label: 'Product' },
            { id: 'sales', label: 'Enterprise Sales' },
            { id: 'finance', label: 'Finance' },
          ].map((track) => (
            <Button
              key={track.id}
              variant={selectedTrack === track.id ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedTrack(track.id)}
              className={`h-8 text-xs font-semibold shrink-0 ${
                selectedTrack === track.id
                  ? 'bg-slate-900 text-white hover:bg-slate-800'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
            >
              {track.label}
            </Button>
          ))}
        </div>

        {/* COMPANIES GRID */}
        {filteredCompanies.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center space-y-3">
            <Building2 className="w-10 h-10 text-slate-400 mx-auto" />
            <h3 className="text-sm font-bold text-slate-800">No matching target companies found</h3>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              You can instantly scrape and add "{searchTerm}" using our BeautifulSoup intelligence engine.
            </p>
            <Button
              variant="default"
              size="sm"
              onClick={() => {
                setScrapeNameInput(searchTerm);
                setShowScrapeModal(true);
              }}
              className="h-8 text-xs bg-slate-900 text-white font-semibold"
            >
              <Plus className="w-3.5 h-3.5 mr-1" />
              Scrape "{searchTerm}" Profile & Worth
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCompanies.map((company) => {
              // Calculate Readiness against Active Resume
              const readiness = calculateResumeReadiness(
                activeResume ? activeResume.skills : [],
                company.competencies
              );

              return (
                <Card 
                  key={company.id}
                  className="bg-white border-slate-200 hover:border-slate-300 shadow-xs hover:shadow-sm transition-all flex flex-col justify-between group cursor-pointer"
                  onClick={() => navigate(`/company/${company.id}`)}
                >
                  <CardHeader className="pb-3 pt-5 px-5">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold text-sm shadow-xs">
                          {company.name.charAt(0)}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <CardTitle className="text-base font-bold text-slate-900 group-hover:text-slate-700 transition-colors">
                              {company.name}
                            </CardTitle>
                            {company.ticker && (
                              <Badge variant="outline" className="text-[10px] font-mono py-0 px-1 bg-slate-50 text-slate-600 border-slate-200">
                                {company.ticker}
                              </Badge>
                            )}
                            {company.isCustomScraped && (
                              <Badge className="text-[9px] py-0 px-1.5 bg-emerald-50 text-emerald-800 border border-emerald-300">
                                Scraped
                              </Badge>
                            )}
                          </div>
                          <CardDescription className="text-xs text-slate-500 truncate max-w-[200px]">
                            {company.industry}
                          </CardDescription>
                        </div>
                      </div>

                      {/* Readiness Score Badge */}
                      <Badge 
                        className={`text-xs px-2.5 py-0.5 font-bold ${
                          readiness.score >= 80 
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-300' 
                            : readiness.score >= 65
                            ? 'bg-blue-50 text-blue-700 border-blue-300'
                            : 'bg-amber-50 text-amber-700 border-amber-300'
                        } border`}
                      >
                        {readiness.score}% Fit
                      </Badge>
                    </div>

                    {/* Financial Worth Badge if available */}
                    {company.estimatedWorth && (
                      <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center gap-1.5 text-xs text-slate-700">
                        <DollarSign className="w-3.5 h-3.5 text-emerald-700 shrink-0" />
                        <span className="font-semibold text-slate-900">Estimated Worth:</span>
                        <span className="text-slate-600 truncate">{company.estimatedWorth}</span>
                      </div>
                    )}
                  </CardHeader>

                  <CardContent className="px-5 py-2 space-y-4 flex-1">
                    <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                      {company.description}
                    </p>

                    {/* Resume Match Gauge */}
                    <div className="space-y-1.5 p-3 rounded-lg bg-slate-50 border border-slate-200">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="font-semibold text-slate-700">Resume Readiness</span>
                        <span className="font-bold text-slate-900">{readiness.matchedSkills.length} of {company.competencies.length} competencies</span>
                      </div>
                      <Progress value={readiness.score} className="h-1.5 bg-slate-200" />
                    </div>

                    {/* Available Roles */}
                    <div className="space-y-1.5">
                      <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                        Calibrated Roles
                      </span>
                      <div className="space-y-1">
                        {company.roles.map((role) => (
                          <div 
                            key={role.id}
                            className="flex items-center justify-between text-xs py-1 px-2 rounded bg-white border border-slate-100"
                          >
                            <span className="font-medium text-slate-800 truncate">{role.title}</span>
                            <Badge variant="outline" className="text-[10px] py-0 px-1 border-slate-200 text-slate-500 uppercase font-semibold">
                              {role.level}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Key Competency Tags */}
                    <div className="space-y-1">
                      <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                        Primary Competencies
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {company.competencies.slice(0, 4).map((comp, idx) => {
                          const isMatched = readiness.matchedSkills.includes(comp);
                          return (
                            <Badge
                              key={idx}
                              variant="outline"
                              className={`text-[10px] py-0 px-1.5 font-medium ${
                                isMatched 
                                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300' 
                                  : 'bg-white text-slate-600 border-slate-200'
                              }`}
                            >
                              {isMatched ? '✓ ' : ''}{comp}
                            </Badge>
                          );
                        })}
                        {company.competencies.length > 4 && (
                          <span className="text-[10px] text-slate-400 self-center">
                            +{company.competencies.length - 4} more
                          </span>
                        )}
                      </div>
                    </div>
                  </CardContent>

                  <CardFooter className="pt-3 pb-4 px-5 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between">
                    <span className="text-[11px] text-slate-500 font-medium">
                      20-Question Simulation (2 Rounds)
                    </span>
                    <Button
                      variant="default"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/company/${company.id}`);
                      }}
                      className="h-8 text-xs bg-slate-900 hover:bg-slate-800 text-white font-semibold"
                    >
                      View Rubric & Test <ArrowRight className="w-3.5 h-3.5 ml-1" />
                    </Button>
                  </CardFooter>
                </Card>
              );
            })}
          </div>
        )}

      </main>

      {/* SCRAPE COMPANY MODAL */}
      {showScrapeModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <Card className="w-full max-w-lg bg-white border-slate-200 shadow-xl animate-in fade-in zoom-in-95 duration-150">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Globe className="w-4 h-4 text-slate-900" />
                  Scrape & Load Any Target Company
                </CardTitle>
                <CardDescription className="text-xs text-slate-500 mt-0.5">
                  BeautifulSoup intelligence extracts market worth, revenue, culture, and platform competencies.
                </CardDescription>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowScrapeModal(false)}
                disabled={isScraping}
                className="h-8 w-8 p-0 rounded-full text-slate-400 hover:text-slate-900"
              >
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            <Separator />
            <form onSubmit={handleScrapeCompany}>
              <CardContent className="pt-4 pb-2 space-y-4">
                {scrapeError && (
                  <div className="p-2.5 rounded-lg border border-red-200 bg-red-50 text-red-700 text-xs">
                    {scrapeError}
                  </div>
                )}

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700 block">
                    Company Name <span className="text-red-500">*</span>
                  </label>
                  <Input
                    placeholder="e.g. Netflix, Databricks, Uber, Palantir, OpenAI, Airbnb..."
                    value={scrapeNameInput}
                    onChange={(e) => setScrapeNameInput(e.target.value)}
                    disabled={isScraping}
                    required
                    className="h-9 text-xs border-slate-300 focus-visible:ring-slate-900"
                  />
                  <p className="text-[11px] text-slate-500">
                    We will fetch Wikipedia public infobox data and official domains to assess enterprise worth.
                  </p>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700 block">
                    Website URL (Optional)
                  </label>
                  <Input
                    placeholder="e.g. https://www.netflix.com or leave empty for auto-discovery"
                    value={scrapeUrlInput}
                    onChange={(e) => setScrapeUrlInput(e.target.value)}
                    disabled={isScraping}
                    className="h-9 text-xs border-slate-300 focus-visible:ring-slate-900"
                  />
                </div>

                {isScraping && (
                  <div className="p-3 rounded-lg border border-slate-200 bg-slate-50 text-xs text-slate-700 space-y-2 animate-pulse">
                    <div className="flex items-center gap-2 font-semibold text-slate-900">
                      <Loader2 className="w-4 h-4 animate-spin text-slate-900" />
                      BeautifulSoup Scraper Active
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Extracting Wikipedia infobox, revenue figures, headcount, tech stack, and generating calibrated 20-question hiring rubric...
                    </p>
                  </div>
                )}
              </CardContent>

              <Separator />
              <CardFooter className="flex items-center justify-between pt-3">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowScrapeModal(false)}
                  disabled={isScraping}
                  className="text-xs text-slate-600"
                >
                  Cancel
                </Button>

                <Button
                  type="submit"
                  disabled={isScraping || !scrapeNameInput.trim()}
                  className="h-8 text-xs font-bold bg-slate-900 hover:bg-slate-800 text-white"
                >
                  {isScraping ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                      Scraping & Synthesizing...
                    </>
                  ) : (
                    <>
                      <Globe className="w-3.5 h-3.5 mr-1.5" />
                      Scrape Profile & Calculate Worth
                    </>
                  )}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </div>
      )}

    </div>
  );
}
