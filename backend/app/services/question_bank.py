from typing import Dict, Any, List

def detect_role_category(role_title: str) -> str:
    """Detect candidate role track among the 5 core tracks."""
    r = role_title.lower()
    if any(k in r for k in ["product manager", "product management", "pm ", "tpm", "group product manager", "associate product manager"]):
        return "pm"
    if any(k in r for k in ["data scientist", "data science", "machine learning", "ml engineer", "ai engineer", "deep learning", "nlp", "computer vision", "data analyst"]):
        return "data"
    if any(k in r for k in ["investment banking", "consultant", "consulting", "private equity", "equity research", "corporate strategy", "finance", "financial", "m&a"]):
        return "finance"
    if any(k in r for k in ["sales", "account executive", "bdr", "sdr", "business development", "marketing", "recruiter", "talent", "customer success", "csm"]):
        return "sales"
    return "tech"

def is_non_tech_role(role_title: str) -> bool:
    """Helper for backward compatibility."""
    return detect_role_category(role_title) != "tech"

def get_questions_for_track(track: str, role_title: str, company_name: str) -> List[Dict[str, Any]]:
    """Return 20 role-specific questions (10 Aptitude + 10 Domain) tailored to the company."""
    
    if track == "pm":
        # =========================================================================
        # PRODUCT MANAGEMENT (PM) TRACK: 10 Metrics/Aptitude + 10 Product Sense
        # =========================================================================
        return [
            # 10 Quantitative Metrics & Aptitude Questions
            {
                "turn_number": 1,
                "stage_title": "Round 1: Product Metrics & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Total Addressable Market (TAM) Sizing",
                "question": f"At {company_name}, you are evaluating a new B2B product line. If there are 200,000 potential enterprise businesses globally, with an estimated penetration rate of 4% over 3 years and an average annual contract value (ACV) of $25,000, what is the 3-year serviceable obtainable revenue?",
                "options": [
                    "A) $100,000,000",
                    "B) $200,000,000",
                    "C) $50,000,000",
                    "D) $20,000,000"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Penetrated businesses = 200,000 * 4% = 8,000 customers. Revenue = 8,000 * $25,000 = $200,000,000.",
                "company_context": f"Market sizing rigor ensures new product bets at {company_name} meet hurdle rates."
            },
            {
                "turn_number": 2,
                "stage_title": "Round 1: Product Metrics & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Funnel Conversion Rate & Drop-off Math",
                "question": f"In {company_name}'s core onboarding flow: 100,000 users visit the sign-up page; 60% create an account; 50% of registered users complete profile setup; and 40% of those invite a teammate within 7 days. How many viral teammate invites are generated from the initial cohort?",
                "options": [
                    "A) 12,000 users",
                    "B) 15,000 users",
                    "C) 24,000 users",
                    "D) 8,000 users"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Registered = 100k * 0.6 = 60,000. Profile completed = 60k * 0.5 = 30,000. Teammate invited = 30k * 0.4 = 12,000.",
                "company_context": f"Funnel drop-off analytics pinpoint onboarding bottlenecks across {company_name}'s web applications."
            },
            {
                "turn_number": 3,
                "stage_title": "Round 1: Product Metrics & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "A/B Testing Statistical Significance & Minimum Detectable Effect",
                "question": f"You run an A/B experiment at {company_name} testing a new checkout flow against a baseline conversion rate of 5.0%. To reliably detect a Minimum Detectable Effect (MDE) of 10% relative lift (from 5.0% to 5.5%) with 80% statistical power and 95% confidence level, which rule of thumb applies to your sample size?",
                "options": [
                    "A) Smaller relative lifts (MDE) require significantly larger sample sizes per variant",
                    "B) Testing for a 10% lift requires fewer users than testing for a 50% lift",
                    "C) Sample size depends only on duration, not conversion baseline",
                    "D) P-values under 0.50 are sufficient to declare statistical significance"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Because sample size scales inversely with the square of the effect size (N ~ 1 / MDE^2), detecting small percentage lifts requires exponentially larger traffic volume.",
                "company_context": f"{company_name}'s experimentation culture relies on statistically sound sample sizing."
            },
            {
                "turn_number": 4,
                "stage_title": "Round 1: Product Metrics & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "RICE Prioritization Framework Scoring",
                "question": f"Using the RICE framework (Score = Reach * Impact * Confidence / Effort), evaluate Feature X: Reach = 10,000 users/month, Impact = 2.0 (High), Confidence = 80% (0.8), Effort = 4 person-months. What is the RICE score for Feature X?",
                "options": [
                    "A) 4,000",
                    "B) 2,500",
                    "C) 1,600",
                    "D) 5,000"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "RICE Score = (10,000 * 2.0 * 0.8) / 4 = 16,000 / 4 = 4,000.",
                "company_context": f"Product roadmaps at {company_name} use objective scoring frameworks to justify sprint tradeoffs."
            },
            {
                "turn_number": 5,
                "stage_title": "Round 1: Product Metrics & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "User Retention Cohort Curve & Asymptotic Flatness",
                "question": f"When analyzing weekly retention cohort curves at {company_name}, what does an asymptotic flattening of the retention curve beyond Week 8 signify about Product-Market Fit?",
                "options": [
                    "A) The product has zero churn and requires no marketing",
                    "B) A core group of sticky users finds sustained long-term value, indicating healthy product-market fit",
                    "C) The database query has terminated prematurely",
                    "D) All users will churn by Month 6"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "A retention curve that flattens parallel to the x-axis proves that churn approaches zero for a retained core, establishing true product-market fit.",
                "company_context": f"Long-term cohort curve stabilization is a primary validation milestone at {company_name}."
            },
            {
                "turn_number": 6,
                "stage_title": "Round 1: Product Metrics & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Customer Lifetime Value (LTV) to CAC Payback",
                "question": f"At {company_name}, an enterprise product generates $4,000 monthly gross profit per subscriber. If the monthly churn rate is 2% and the Customer Acquisition Cost (CAC) is $60,000, what is the LTV:CAC ratio and how many months does CAC payback take?",
                "options": [
                    "A) LTV:CAC is 3.3:1 with a 15-month payback period",
                    "B) LTV:CAC is 1.5:1 with a 24-month payback period",
                    "C) LTV:CAC is 5.0:1 with a 10-month payback period",
                    "D) LTV:CAC is 2.0:1 with a 30-month payback period"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "LTV = Monthly Gross Profit / Churn Rate = $4,000 / 0.02 = $200,000. LTV:CAC = $200k / $60k = 3.33:1. Payback = $60,000 / $4,000 per month = 15 months.",
                "company_context": f"Unit economics benchmarks at {company_name} target LTV:CAC >= 3:1."
            },
            {
                "turn_number": 7,
                "stage_title": "Round 1: Product Metrics & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "DAU/MAU Stickiness Ratio",
                "question": f"A mobile app at {company_name} records 3,000,000 Daily Active Users (DAU) and 10,000,000 Monthly Active Users (MAU). What is its stickiness ratio, and what does this metric communicate?",
                "options": [
                    "A) 30% stickiness (the average active user engages roughly 9 days out of a 30-day month)",
                    "B) 3.3% stickiness (low utility app)",
                    "C) 60% stickiness (viral product)",
                    "D) 15% stickiness (infrequent utility)"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Stickiness = DAU / MAU = 3M / 10M = 30%. In consumer applications, 30% indicates strong habitual engagement (30% of 30 days ~ 9 days per month).",
                "company_context": f"DAU/MAU tracking reflects user habit formation across {company_name}'s product ecosystem."
            },
            {
                "turn_number": 8,
                "stage_title": "Round 1: Product Metrics & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Net Promoter Score (NPS) Arithmetic",
                "question": f"In a survey of 1,000 {company_name} users: 650 rate 9-10 (Promoters), 200 rate 7-8 (Passives), and 150 rate 0-6 (Detractors). What is the resulting Net Promoter Score (NPS)?",
                "options": [
                    "A) +50",
                    "B) +65",
                    "C) +35",
                    "D) +80"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "% Promoters = 650/1000 = 65%. % Detractors = 150/1000 = 15%. NPS = % Promoters - % Detractors = 65 - 15 = +50.",
                "company_context": f"NPS benchmarks above +40 denote high customer satisfaction at {company_name}."
            },
            {
                "turn_number": 9,
                "stage_title": "Round 1: Product Metrics & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Viral Coefficient (K-Factor) Growth Modeling",
                "question": f"Viral Coefficient K is defined as: (Number of invites sent per user) * (Conversion rate per invite). If an existing user sends an average of 4 invites with a 30% acceptance rate, what is K and will the product experience organic exponential viral growth?",
                "options": [
                    "A) K = 1.2, resulting in exponential organic growth (K > 1.0)",
                    "B) K = 0.75, resulting in plateaued growth",
                    "C) K = 0.30, requiring heavy paid acquisition",
                    "D) K = 1.0, steady state with zero growth"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "K = 4 * 0.30 = 1.2. Because K > 1.0, each new user generates more than one additional user, initiating self-sustaining viral loops.",
                "company_context": f"Viral expansion dynamics enable product-led scale at {company_name}."
            },
            {
                "turn_number": 10,
                "stage_title": "Round 1: Product Metrics & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Marketplace Take-Rate & Gross Merchandise Value (GMV)",
                "question": f"In a platform marketplace feature at {company_name}, third-party sellers process $500,000,000 in annual Gross Merchandise Value (GMV). If {company_name} takes a blended commission take-rate of 6.5% and incurs payment processing fees of 1.5%, what is the platform's net take revenue?",
                "options": [
                    "A) $25,000,000",
                    "B) $32,500,000",
                    "C) $40,000,000",
                    "D) $15,000,000"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Net take-rate = 6.5% - 1.5% = 5.0%. Net take revenue = $500,000,000 * 5.0% = $25,000,000.",
                "company_context": f"Platform marketplace economics at {company_name} balance take-rates against seller retention."
            },

            # 10 Product Sense & Strategic Execution Questions
            {
                "turn_number": 11,
                "stage_title": "Round 2: Strategic Product Sense & Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "North Star Metric Selection",
                "question": f"When leading a flagship product line at {company_name}, why is choosing a single North Star Metric (e.g., Weekly Active Workspaces completing an action) superior to tracking 20 unweighted dashboard metrics?",
                "options": [
                    "A) It allows executive teams to fire underperforming engineers faster",
                    "B) It aligns cross-functional engineering, design, and growth teams toward customer value creation and serves as the leading indicator of sustainable revenue",
                    "C) It prevents data scientists from needing SQL access",
                    "D) It ensures marketing budgets are never spent on user acquisition"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "A true North Star metric aligns cross-functional priorities around the core moment where the user derives enduring value from the product.",
                "company_context": f"At {company_name}, product teams rally around explicit North Star metrics to prevent misaligned priorities."
            },
            {
                "turn_number": 12,
                "stage_title": "Round 2: Strategic Product Sense & Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Balancing Engineering Tech Debt vs New Feature Velocity",
                "question": f"Your engineering lead at {company_name} reports that legacy architecture is slowing sprint velocity by 40% and requests spending 2 full sprints exclusively on refactoring. How should you navigate this trade-off?",
                "options": [
                    "A) Reject all tech debt work because product managers only get promoted on new feature launches",
                    "B) Allocate a consistent 20-30% capacity budget every sprint for foundational technical improvements, connecting the refactoring milestones directly to system reliability and future feature velocity",
                    "C) Completely freeze all product releases for the next 6 months",
                    "D) Outsource the codebase to external contract developers"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Sustainable product velocity requires negotiating an ongoing allocation (e.g. 20%) for platform health rather than feast-or-famine refactor freezes.",
                "company_context": f"Collaboration between PMs and Staff Engineers at {company_name} maintains high technical standards."
            },
            {
                "turn_number": 13,
                "stage_title": "Round 2: Strategic Product Sense & Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Handling a Negative Experiment Result",
                "question": f"An A/B test for a highly anticipated feature at {company_name} shows a 4% lift in click-through rate but a statistically significant 2.5% decrease in overall 7-day retention. What is the correct product decision?",
                "options": [
                    "A) Ship the feature anyway and celebrate the CTR increase",
                    "B) Halt the rollout, synthesize user qualitative session replays to understand why the feature induces friction, and iterate or scrap it",
                    "C) Change the experiment metrics retroactively until the feature looks successful",
                    "D) Fire the data scientist who ran the experiment"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Shallow engagement metrics (CTR) must never cannibalize downstream core retention. A disciplined PM investigates the user friction before rolling out.",
                "company_context": f"Customer retention is the ultimate benchmark of product quality at {company_name}."
            },
            {
                "turn_number": 14,
                "stage_title": "Round 2: Strategic Product Sense & Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Enterprise Customization Requests vs Product Coherence",
                "question": f"A Tier-1 enterprise customer at {company_name} offers a $1M contract renewal on the condition that you build a proprietary bespoke feature into the core SaaS platform. How should you evaluate this?",
                "options": [
                    "A) Agree immediately and hardcode custom logic specifically for their company into the codebase",
                    "B) Probe their underlying business workflow to see if an extensible, generic capability (e.g. webhook or API) solves their problem for all enterprise customers without compromising architecture",
                    "C) Refuse to speak to enterprise customers because consumer PMs don't do B2B",
                    "D) Promise the feature verbally and delay delivery indefinitely"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Top PMs avoid bespoke one-off technical debt by abstracting enterprise requirements into extensible platform capabilities that benefit the broader customer base.",
                "company_context": f"Product scalability at {company_name} depends on building unified platforms rather than bespoke point solutions."
            },
            {
                "turn_number": 15,
                "stage_title": "Round 2: Strategic Product Sense & Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Cross-Functional Launch Alignment & Risk Mitigation",
                "question": f"Two weeks before a major GA product launch at {company_name}, your legal and privacy team flags that a data logging feature may conflict with upcoming EU regulatory requirements. What is your action?",
                "options": [
                    "A) Launch anyway and hope regulators don't notice",
                    "B) Partner with engineering to isolate the non-compliant telemetry behind a feature flag for EU regions, preserving the global launch timeline while maintaining full legal compliance",
                    "C) Cancel the entire project permanently",
                    "D) Blame the legal team in a company-wide email"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Using regional feature gating and decoupling regulatory dependencies allows product momentum to proceed while honoring compliance.",
                "company_context": f"Global launches at {company_name} demand rigorous regulatory governance."
            },
            {
                "turn_number": 16,
                "stage_title": "Round 2: Strategic Product Sense & Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Zero-to-One Product Discovery: Identifying Real Customer Pain",
                "question": f"In user interviews for a zero-to-one product bet at {company_name}, 8 out of 10 users say: 'Yes, that sounds like a great idea, I would definitely use that.' Why must an experienced PM remain cautious?",
                "options": [
                    "A) Users are notoriously polite in hypothetical interviews; validation requires measuring actual past behavior, willingness to pay, or commitments of time/data rather than opinions",
                    "B) 8 out of 10 is not a statistically significant sample size",
                    "C) Users always lie to product managers",
                    "D) Zero-to-one products should never interview customers"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "As established in 'The Mom Test', hypothetical compliments are false positives. Validation comes from past workarounds, pain intensity, and pre-orders.",
                "company_context": f"Discovery interviews at {company_name} focus on concrete historical evidence of customer pain."
            },
            {
                "turn_number": 17,
                "stage_title": "Round 2: Strategic Product Sense & Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Competitive Response & Strategic Moats",
                "question": f"A well-funded startup launches a clone of {company_name}'s core feature at half the price. What is the most effective long-term product response?",
                "options": [
                    "A) Immediately cut your prices in half and engage in a margin race to the bottom",
                    "B) Double down on your ecosystem moats: proprietary integrations, enterprise reliability, network effects, and customer switching costs that a point-solution clone cannot replicate",
                    "C) File baseless copyright lawsuits against the startup",
                    "D) Delete the feature from your platform"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Enterprise and platform products win on ecosystem integration, trust, security, and switching costs rather than matching commodity feature prices.",
                "company_context": f"{company_name}'s competitive durability is anchored in deep ecosystem integrations and platform network effects."
            },
            {
                "turn_number": 18,
                "stage_title": "Round 2: Strategic Product Sense & Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Pricing & Packaging: Freemium vs Reverse-Trial",
                "question": f"When transitioning a self-serve SaaS product at {company_name} from a pure Freemium model to a 14-day Reverse-Trial (full enterprise features unlocked initially, degrading to free tier if unconverted), what is the primary behavioral advantage?",
                "options": [
                    "A) Users immediately experience peak product value (endowment effect), increasing paid conversion by exposing advanced features before restricting them",
                    "B) It eliminates the need to maintain free servers",
                    "C) It hides product pricing from competitors",
                    "D) It forces users to enter a credit card on Day 1"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Reverse trials leverage loss aversion and the endowment effect: once users build workflows relying on advanced features, they are far more likely to upgrade.",
                "company_context": f"Self-serve growth optimization at {company_name} tests modern PLG onboarding psychology."
            },
            {
                "turn_number": 19,
                "stage_title": "Round 2: Strategic Product Sense & Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Feature Deprecation & Sunsetting Strategy",
                "question": f"A legacy feature at {company_name} is used by only 2% of total users but generates 25% of backend maintenance overhead. How do you properly deprecate it?",
                "options": [
                    "A) Delete the feature silently overnight without telling anyone",
                    "B) Provide 90-day advance notice, provide clear migration pathways or alternatives, support high-value customers with transition guides, and monitor telemetry during scheduled deprecation windows",
                    "C) Double the price of the feature to force users to leave",
                    "D) Keep the feature forever to avoid upsetting any customer"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Responsible deprecation respects user trust by communicating timelines, offering alternatives, and coordinating migrations well in advance.",
                "company_context": f"Platform hygiene and deprecation protocols at {company_name} protect brand equity while maintaining engineering agility."
            },
            {
                "turn_number": 20,
                "stage_title": "Round 2: Strategic Product Sense & Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Product Post-Mortem & Cultural Accountability",
                "question": f"Following a feature launch at {company_name} that failed to hit target adoption goals, what is the key output of a blameless product retrospective?",
                "options": [
                    "A) Assigning blame to the marketing team for poor messaging",
                    "B) Documenting false hypothesis assumptions, identifying gaps in customer validation, and updating discovery frameworks for future product bets",
                    "C) Deleting all documentation related to the project",
                    "D) Forbidding the team from launching experimental features again"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "High-performing product organizations embrace blameless post-mortems to turn failed hypotheses into institutional learning.",
                "company_context": f"A culture of intellectual honesty and rigorous learning underpins continuous product innovation at {company_name}."
            }
        ]

    elif track == "data":
        # =========================================================================
        # DATA SCIENCE & MACHINE LEARNING TRACK: 10 Stats/Probability + 10 ML Arch
        # =========================================================================
        return [
            # 10 Quantitative Probability, Stats & Matrix Aptitude Questions
            {
                "turn_number": 1,
                "stage_title": "Round 1: Statistical Inference & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Bayes' Theorem & Precision in Rare Event Detection",
                "question": f"At {company_name}, an automated fraud model flags suspicious transactions. Fraud occurs in 0.1% of transactions (Prior = 0.001). The model has a 99% True Positive Rate (Sensitivity) and a 1% False Positive Rate. Given that a transaction is flagged as fraud, what is the approximate posterior probability that it is truly fraudulent?",
                "options": [
                    "A) Approximately 9.0%",
                    "B) Approximately 99.0%",
                    "C) Approximately 50.0%",
                    "D) Approximately 0.1%"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "P(Fraud|Positive) = (0.99 * 0.001) / [(0.99 * 0.001) + (0.01 * 0.999)] = 0.00099 / (0.00099 + 0.00999) = 0.00099 / 0.01098 ~ 9.01%.",
                "company_context": f"Understanding false positives in base-rate fallacy scenarios is vital for fraud telemetry at {company_name}."
            },
            {
                "turn_number": 2,
                "stage_title": "Round 1: Statistical Inference & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Confusion Matrix: Precision vs Recall F1-Score Math",
                "question": f"An evaluation of an ML classifier at {company_name} shows: True Positives (TP) = 80, False Positives (FP) = 20, False Negatives (FN) = 20. What is the F1-Score of this model?",
                "options": [
                    "A) 0.80",
                    "B) 0.75",
                    "C) 0.85",
                    "D) 0.90"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Precision = TP / (TP + FP) = 80/100 = 0.80. Recall = TP / (TP + FN) = 80/100 = 0.80. F1 = 2 * (P * R) / (P + R) = 2 * 0.64 / 1.6 = 0.80.",
                "company_context": f"Balanced classification evaluation metrics guide model deployments at {company_name}."
            },
            {
                "turn_number": 3,
                "stage_title": "Round 1: Statistical Inference & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "ROC-AUC vs PR-AUC under Severe Class Imbalance",
                "question": f"When evaluating a model at {company_name} predicting an extreme minority class (positive class is 0.05% of dataset), why is Precision-Recall AUC (PR-AUC) more informative than ROC-AUC?",
                "options": [
                    "A) ROC-AUC can be deceptively high (e.g. 0.98) because the massive true negative volume keeps the False Positive Rate (FP / (FP + TN)) artificially near zero",
                    "B) ROC-AUC is only valid for multi-class classification",
                    "C) PR-AUC requires less computational memory",
                    "D) ROC-AUC is sensitive only to linear relationships"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "When TN is massive, FPR remains tiny even with thousands of false positives. PR-AUC focuses directly on precision and recall without being diluted by true negatives.",
                "company_context": f"Anomaly detection and fraud modeling at {company_name} rely on PR-AUC benchmarks."
            },
            {
                "turn_number": 4,
                "stage_title": "Round 1: Statistical Inference & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Matrix Multiplication Dimensions in Multi-Head Attention",
                "question": f"In a transformer model at {company_name}, query matrix Q and key matrix K each have dimensions (batch_size, num_heads, seq_len, head_dim). What are the exact dimensions of the attention score matrix resulting from `matmul(Q, K.transpose(-2, -1))`?",
                "options": [
                    "A) (batch_size, num_heads, seq_len, seq_len)",
                    "B) (batch_size, num_heads, head_dim, head_dim)",
                    "C) (batch_size, seq_len, num_heads, head_dim)",
                    "D) (batch_size, seq_len, seq_len)"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Multiplying (seq_len, head_dim) by (head_dim, seq_len) yields an attention affinity matrix of dimension (seq_len, seq_len) per head and batch.",
                "company_context": f"Architecting transformer components at {company_name} requires mastery of tensor operations."
            },
            {
                "turn_number": 5,
                "stage_title": "Round 1: Statistical Inference & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Gradient Descent Learning Rate Divergence",
                "question": f"When training a neural network using Stochastic Gradient Descent (SGD) at {company_name}, the training loss suddenly explodes to `NaN`. What is the most probable mathematical cause?",
                "options": [
                    "A) The learning rate is excessively large, causing parameter updates to oscillate outward and overshoot the loss landscape into numerical overflow",
                    "B) The batch size is larger than the GPU memory",
                    "C) The dataset has too many training epochs",
                    "D) The activation function has zero bias"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Excessive learning rates cause gradient updates to diverge exponentially, creating floating-point overflow resulting in NaN.",
                "company_context": f"Hyperparameter tuning and gradient stability monitoring are foundational in {company_name}'s ML training runs."
            },
            {
                "turn_number": 6,
                "stage_title": "Round 1: Statistical Inference & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Bonferroni Correction in Multiple Hypothesis Testing",
                "question": f"A data scientist at {company_name} runs 20 simultaneous A/B feature hypothesis tests at an individual significance level of alpha = 0.05. According to the Bonferroni correction, what adjusted alpha threshold must each individual test satisfy to control Family-Wise Error Rate (FWER) at 0.05?",
                "options": [
                    "A) alpha = 0.0025 (0.05 / 20)",
                    "B) alpha = 0.05",
                    "C) alpha = 0.01",
                    "D) alpha = 0.001"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Bonferroni divides the overall significance alpha by the number of simultaneous tests: 0.05 / 20 = 0.0025 to prevent spurious false discoveries.",
                "company_context": f"Multi-armed bandit and A/B test governance at {company_name} uses error rate controls."
            },
            {
                "turn_number": 7,
                "stage_title": "Round 1: Statistical Inference & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Multicollinearity & Variance Inflation Factor (VIF)",
                "question": f"In a linear regression model at {company_name}, an engineer computes a Variance Inflation Factor (VIF) of 18.5 for a marketing channel feature. What does this indicate?",
                "options": [
                    "A) Severe multicollinearity exists; the feature is highly correlated with other independent variables, inflating coefficient standard errors",
                    "B) The model has 18.5% training accuracy",
                    "C) The feature has zero predictive value and must be transformed into text",
                    "D) The dataset has 18.5% missing values"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "VIF values above 5-10 indicate significant multicollinearity, meaning the variable's variance is largely explained by other predictors, destabilizing coefficient estimates.",
                "company_context": f"Feature pruning and collinearity checks ensure model explainability at {company_name}."
            },
            {
                "turn_number": 8,
                "stage_title": "Round 1: Statistical Inference & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "L1 (Lasso) vs L2 (Ridge) Regularization Sparsity",
                "question": f"Why does L1 regularization (Lasso) drive feature weights to exact zero (yielding sparse feature selection), whereas L2 regularization (Ridge) only shrinks weights toward zero without setting them to exact zero?",
                "options": [
                    "A) The L1 penalty contour is diamond-shaped with sharp corners on the coordinate axes where the loss contour is likely to intersect first",
                    "B) L1 regularization uses matrix inversion while L2 does not",
                    "C) L2 regularization is only used for unsupervised clustering",
                    "D) L1 regularization doubles the learning rate"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "L1's non-differentiable sharp corners at w_i = 0 cause constrained optimization points to land directly on axes, driving non-essential coefficients to exact zero.",
                "company_context": f"High-dimensional feature selection at {company_name} utilizes L1 penalties for compact models."
            },
            {
                "turn_number": 9,
                "stage_title": "Round 1: Statistical Inference & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Cosine Similarity Vector Math",
                "question": f"Given two embedding vectors A = [3, 4] and B = [4, 3], what is their exact Cosine Similarity?",
                "options": [
                    "A) 24 / 25 = 0.96",
                    "B) 1.00",
                    "C) 0.50",
                    "D) 7 / 25 = 0.28"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Dot product = (3*4) + (4*3) = 12 + 12 = 24. Norm A = sqrt(9 + 16) = 5. Norm B = sqrt(16 + 9) = 5. Cosine Similarity = 24 / (5 * 5) = 24 / 25 = 0.96.",
                "company_context": f"Semantic vector search and embedding retrieval at {company_name} rely on cosine similarity."
            },
            {
                "turn_number": 10,
                "stage_title": "Round 1: Statistical Inference & Quantitative Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "K-Fold Cross-Validation Data Split Arithmetic",
                "question": f"In a 5-fold cross-validation scheme on a dataset of 500,000 samples at {company_name}, how many samples are used for training and how many for validation in each fold iteration?",
                "options": [
                    "A) 400,000 for training, 100,000 for validation (80% / 20%)",
                    "B) 250,000 for training, 250,000 for validation",
                    "C) 450,000 for training, 50,000 for validation",
                    "D) 100,000 for training, 400,000 for validation"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "In K-fold cross-validation, 1 fold (1/5 = 20% = 100,000) serves as validation while the remaining K-1 folds (4/5 = 80% = 400,000) serve as training.",
                "company_context": f"Unbiased model validation at {company_name} uses cross-validation to prevent overfitting."
            },

            # 10 Applied Machine Learning & AI Engineering Questions
            {
                "turn_number": 11,
                "stage_title": "Round 2: Applied Machine Learning & Systems Architecture",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Data Leakage Prevention in Pipeline Design",
                "question": f"When building an ML preprocessing pipeline at {company_name}, an engineer computes mean normalization and target encoding across the entire dataset before splitting into train and test sets. What is the fundamental issue?",
                "options": [
                    "A) Data leakage: test set distribution statistics leak into the training phase, creating overly optimistic validation metrics that fail in production",
                    "B) It causes a memory leak in the Spark cluster",
                    "C) Normalization must only be done on categorical variables",
                    "D) It converts the problem from regression into classification"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Fitting scalers or encoders on the entire dataset incorporates test-time knowledge into training data, generating invalid validation scores.",
                "company_context": f"Strict pipeline isolation prevents data leakage across {company_name}'s production models."
            },
            {
                "turn_number": 12,
                "stage_title": "Round 2: Applied Machine Learning & Systems Architecture",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Handling Severe Class Imbalance (SMOTE vs Focal Loss)",
                "question": f"In a deep learning model classifying rare platform security intrusions at {company_name}, which loss function dynamically scales the loss assigned to hard, easily misclassified examples while downweighting easy negative examples?",
                "options": [
                    "A) Focal Loss",
                    "B) Standard Binary Cross Entropy",
                    "C) Mean Squared Error",
                    "D) Hinge Loss"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Focal Loss adds a modulating factor (1 - p_t)^gamma to cross-entropy loss, downweighting easy negatives and focusing model training on hard minority examples.",
                "company_context": f"Intrusion detection models at {company_name} rely on focal loss for high precision on rare events."
            },
            {
                "turn_number": 13,
                "stage_title": "Round 2: Applied Machine Learning & Systems Architecture",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Model Monitoring: Concept Drift vs Covariate Shift",
                "question": f"In production monitoring at {company_name}, what is the difference between Covariate Shift and Concept Drift?",
                "options": [
                    "A) Covariate Shift means input feature distribution P(X) changes while P(Y|X) remains constant; Concept Drift means the relationship between features and labels P(Y|X) itself changes",
                    "B) Covariate Shift affects only unsupervised models; Concept Drift affects only neural networks",
                    "C) Concept Drift is a hardware GPU failure",
                    "D) There is no mathematical distinction"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Covariate shift: inputs change (e.g. demographic shift). Concept drift: the actual meaning or outcome changes (e.g. macro-economic shift altering consumer purchase propensity for the same income).",
                "company_context": f"Production model observabilty at {company_name} monitors both covariate shift and concept drift."
            },
            {
                "turn_number": 14,
                "stage_title": "Round 2: Applied Machine Learning & Systems Architecture",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Vector Database Indexing: HNSW vs Flat Index",
                "question": f"When scaling an embedding retrieval engine to 50,000,000 vectors at {company_name}, why is Hierarchical Navigable Small World (HNSW) indexing preferred over an exact Flat L2 index?",
                "options": [
                    "A) HNSW provides Approximate Nearest Neighbor (ANN) search with logarithmic O(log N) time complexity, whereas Flat index requires linear O(N) exhaustive brute-force distance calculations",
                    "B) HNSW requires zero RAM",
                    "C) Flat indexes only work with 2D vectors",
                    "D) HNSW guarantees 100% exact retrieval recall under all conditions"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Exhaustive flat scan over 50M high-dimensional vectors causes hundreds of milliseconds of latency. HNSW navigates multi-layer graph structures to return top-k matches in single-digit milliseconds.",
                "company_context": f"Real-time semantic search and RAG retrieval at {company_name} rely on HNSW vector graphs."
            },
            {
                "turn_number": 15,
                "stage_title": "Round 2: Applied Machine Learning & Systems Architecture",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Inference Optimization: Quantization (INT8 vs FP16)",
                "question": f"To reduce LLM inference latency and memory footprint at {company_name}, an engineer applies Post-Training Quantization (PTQ) from FP16 to INT8. What is the direct operational impact?",
                "options": [
                    "A) Model weight memory footprint is reduced by approximately 50%, with higher cache locality and throughput, at the cost of minimal precision degradation",
                    "B) Model parameters are deleted permanently",
                    "C) Inference latency increases by 400%",
                    "D) The model cannot process text embeddings anymore"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "INT8 uses 8 bits per weight compared to FP16's 16 bits, halving memory bandwidth demands and unlocking integer tensor core acceleration with negligible quality loss.",
                "company_context": f"Edge and cloud LLM serving at {company_name} uses quantization to minimize serving costs."
            },
            {
                "turn_number": 16,
                "stage_title": "Round 2: Applied Machine Learning & Systems Architecture",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Cold-Start Problem in Recommendation Systems",
                "question": f"When deploying a collaborative filtering recommendation engine at {company_name}, how is the 'cold-start problem' for brand-new users with zero interaction history resolved?",
                "options": [
                    "A) Hybrid recommendation: fall back to content-based filtering (metadata, categories, popular trending items, and contextual onboarding signals) until interaction history accumulates",
                    "B) Throw an HTTP 500 server error until the user makes 10 purchases",
                    "C) Delete new user profiles from the database",
                    "D) Recommend items completely at random forever"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Collaborative filtering fails without interaction history. Hybrid systems bridge the cold-start gap using content attributes, trending popularity, and onboarding questions.",
                "company_context": f"Personalization pipelines at {company_name} use hybrid architectures to deliver instant new-user value."
            },
            {
                "turn_number": 17,
                "stage_title": "Round 2: Applied Machine Learning & Systems Architecture",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Overfitting Mitigation in Tree-Based Models",
                "question": f"An XGBoost model at {company_name} achieves 99.5% accuracy on training data but drops to 78.0% on test data. Which hyperparameter adjustments best mitigate this variance?",
                "options": [
                    "A) Decrease `max_depth`, increase `min_child_weight`, and add row/column subsampling (`subsample` and `colsample_bytree`)",
                    "B) Increase `max_depth` to 25 and set learning rate to 1.0",
                    "C) Remove all regularization parameters",
                    "D) Increase the number of trees from 100 to 10,000"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Limiting tree depth, requiring more samples per leaf, and adding feature/data subsampling constrains tree complexity, directly curbing overfitting.",
                "company_context": f"Robust hyperparameter constraints ensure generalization on production tabular data at {company_name}."
            },
            {
                "turn_number": 18,
                "stage_title": "Round 2: Applied Machine Learning & Systems Architecture",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Feature Store Architecture: Offline vs Online Synchronization",
                "question": f"What is the core architectural purpose of a centralized Feature Store (e.g., Feast or Hopsworks) in production ML systems at {company_name}?",
                "options": [
                    "A) Serving low-latency feature lookups (via Redis/DynamoDB) for online inference while providing point-in-time correct historical features (via Parquet/Snowflake) for model training to prevent training-serving skew",
                    "B) Storing git commits of Jupyter notebooks",
                    "C) Replaces all cloud databases with CSV files",
                    "D) Replaces deep learning frameworks entirely"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Feature stores provide a single source of truth for features, synchronizing low-latency online caches with point-in-time historical offline stores.",
                "company_context": f"Enterprise ML engineering at {company_name} avoids feature drift using centralized feature stores."
            },
            {
                "turn_number": 19,
                "stage_title": "Round 2: Applied Machine Learning & Systems Architecture",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Model Interpretability: SHAP vs Feature Importance",
                "question": f"Why are SHAP (SHapley Additive exPlanations) values preferred over traditional Gini impurity feature importance for compliance-sensitive models at {company_name}?",
                "options": [
                    "A) SHAP provides local and global feature attribution grounded in cooperative game theory, ensuring additive consistency and showing both magnitude and direction of feature effect per individual prediction",
                    "B) SHAP runs 1,000x faster than Gini importance",
                    "C) Gini importance works only on unsupervised clustering",
                    "D) SHAP removes all model bias automatically"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Gini importance is biased toward high-cardinality features and lacks directional clarity per prediction. SHAP guarantees consistent, additive, individual explanations.",
                "company_context": f"Model governance and compliance at {company_name} utilize SHAP for model explainability."
            },
            {
                "turn_number": 20,
                "stage_title": "Round 2: Applied Machine Learning & Systems Architecture",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Online vs Offline Metric Misalignment",
                "question": f"A search ranking model at {company_name} shows a 6% improvement in offline NDCG@10, but the production A/B experiment reveals no lift in click-through rate or user purchase conversions. What is the most plausible explanation?",
                "options": [
                    "A) Offline historical logs suffer from position bias, or the offline test set failed to reflect real-world user intent and diversity present in production traffic",
                    "B) Online A/B tests cannot evaluate machine learning models",
                    "C) NDCG only works for binary classification",
                    "D) The model must be converted from Python to C"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Offline logs are biased toward historical top-ranked items. Offline ranking metrics can diverge from real online behavior if exploration, presentation bias, and novelty effects are unaddressed.",
                "company_context": f"Search and discovery at {company_name} conducts counterfactual evaluation to align offline and online metrics."
            }
        ]

    elif track == "finance":
        # =========================================================================
        # FINANCE & CONSULTING TRACK: 10 Financial Aptitude + 10 Valuation/Strategy
        # =========================================================================
        return [
            # 10 Quantitative Financial Modeling Aptitude Questions
            {
                "turn_number": 1,
                "stage_title": "Round 1: Corporate Finance & Financial Modeling Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Weighted Average Cost of Capital (WACC) Calculation",
                "question": f"At {company_name}, you are computing WACC for an enterprise acquisition. Equity value is $600M with a Cost of Equity of 12%. Debt value is $400M with a pre-tax Cost of Debt of 6%. The corporate tax rate is 25%. What is the firm's WACC?",
                "options": [
                    "A) 9.0%",
                    "B) 9.6%",
                    "C) 8.4%",
                    "D) 10.2%"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Total Capital = $1,000M. Equity weight = 60%, Debt weight = 40%. After-tax Cost of Debt = 6% * (1 - 0.25) = 4.5%. WACC = (0.60 * 12%) + (0.40 * 4.5%) = 7.2% + 1.8% = 9.0%.",
                "company_context": f"Accurate discount rate calculations underpin corporate valuation and capital budgeting at {company_name}."
            },
            {
                "turn_number": 2,
                "stage_title": "Round 1: Corporate Finance & Financial Modeling Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "DCF Terminal Value (Gordon Growth Method)",
                "question": f"A target company being evaluated by {company_name} generates a projected final year Free Cash Flow of $50,000,000. Assuming a long-term perpetual growth rate g = 2.5% and a discount rate WACC = 8.5%, what is the Terminal Value of the firm at the end of the projection period?",
                "options": [
                    "A) Approximately $854,166,667",
                    "B) Approximately $625,000,000",
                    "C) Approximately $588,235,294",
                    "D) Approximately $1,000,000,000"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Terminal Value = FCF * (1 + g) / (WACC - g) = $50M * 1.025 / (0.085 - 0.025) = $51.25M / 0.06 = $854,166,667.",
                "company_context": f"Terminal value represents 60-80% of total enterprise value in discounted cash flow modeling at {company_name}."
            },
            {
                "turn_number": 3,
                "stage_title": "Round 1: Corporate Finance & Financial Modeling Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Enterprise Value to Equity Value Bridge",
                "question": f"An enterprise software firm evaluated by {company_name} has an Enterprise Value (EV) of $1,500,000,000. It carries $300,000,000 in total funded debt, $80,000,000 in unrestricted cash and cash equivalents, and $20,000,000 in non-controlling minority interest. What is the company's Implied Equity Value?",
                "options": [
                    "A) $1,260,000,000",
                    "B) $1,880,000,000",
                    "C) $1,420,000,000",
                    "D) $1,100,000,000"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Equity Value = Enterprise Value - Total Debt + Cash - Minority Interest = $1,500M - $300M + $80M - $20M = $1,260,000,000.",
                "company_context": f"M&A transaction structuring at {company_name} requires mastery of capital structure bridges."
            },
            {
                "turn_number": 4,
                "stage_title": "Round 1: Corporate Finance & Financial Modeling Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "EBITDA Margin & Operating Leverage",
                "question": f"A portfolio company at {company_name} generates $200,000,000 in revenue with an EBITDA margin of 25%. If revenue grows by 15% next year and operating costs increase by only 5% due to fixed cost operating leverage, what is the new EBITDA?",
                "options": [
                    "A) $72,500,000 (EBITDA margin expands to 31.5%)",
                    "B) $57,500,000",
                    "C) $50,000,000",
                    "D) $65,000,000"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Original EBITDA = $50M, original costs = $150M. New revenue = $200M * 1.15 = $230M. New costs = $150M * 1.05 = $157.5M. New EBITDA = $230M - $157.5M = $72.5M.",
                "company_context": f"Operating leverage sensitivity modeling evaluates private equity returns at {company_name}."
            },
            {
                "turn_number": 5,
                "stage_title": "Round 1: Corporate Finance & Financial Modeling Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Compound Annual Growth Rate (CAGR) Math",
                "question": f"A target company's ARR grew from $25,000,000 in Year 0 to $100,000,000 in Year 4. What is the 4-year Compound Annual Growth Rate (CAGR)?",
                "options": [
                    "A) Approximately 41.4%",
                    "B) Approximately 75.0%",
                    "C) Approximately 25.0%",
                    "D) Approximately 50.0%"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "CAGR = (Ending / Beginning)^(1 / N) - 1 = (100 / 25)^(1/4) - 1 = (4.0)^0.25 - 1 = 1.4142 - 1 = 41.42%.",
                "company_context": f"Historical growth benchmarking drives valuation multiples in advisory mandates at {company_name}."
            },
            {
                "turn_number": 6,
                "stage_title": "Round 1: Corporate Finance & Financial Modeling Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Net Working Capital (NWC) Cash Flow Impact",
                "question": f"In a financial statement model at {company_name}, if Accounts Receivable increases by $15M, Inventory decreases by $5M, and Accounts Payable increases by $10M over the fiscal year, what is the net impact on Free Cash Flow from Working Capital?",
                "options": [
                    "A) Zero net cash flow impact ($0)",
                    "B) Cash outflow of $10M",
                    "C) Cash inflow of $20M",
                    "D) Cash outflow of $15M"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Change in NWC = Delta(AR) + Delta(Inv) - Delta(AP) = +$15M - $5M - $10M = $0. Cash flow impact from NWC change is -$0 = $0.",
                "company_context": f"Three-statement modeling at {company_name} requires precise balance sheet cash flow links."
            },
            {
                "turn_number": 7,
                "stage_title": "Round 1: Corporate Finance & Financial Modeling Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Debt Service Coverage Ratio (DSCR) & LBO Risk",
                "question": f"In a Leveraged Buyout (LBO) debt structuring at {company_name}, the borrower generates $45,000,000 in annual Net Operating Income (NOI). The annual debt service consists of $20,000,000 in principal repayment and $10,000,000 in interest expense. What is the Debt Service Coverage Ratio (DSCR)?",
                "options": [
                    "A) 1.50x",
                    "B) 2.25x",
                    "C) 1.20x",
                    "D) 0.67x"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "DSCR = Net Operating Income / Total Debt Service = $45M / ($20M + $10M) = $45M / $30M = 1.50x.",
                "company_context": f"Credit covenants and private credit transactions at {company_name} require DSCR >= 1.25x - 1.50x."
            },
            {
                "turn_number": 8,
                "stage_title": "Round 1: Corporate Finance & Financial Modeling Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Breakeven Analysis under Operating Leverage",
                "question": f"A corporate division at {company_name} sells software appliance units at $500 per unit. Variable cost per unit is $200. Total annual fixed overhead is $6,000,000. How many units must be sold to reach operating breakeven (EBIT = $0)?",
                "options": [
                    "A) 20,000 units",
                    "B) 12,000 units",
                    "C) 30,000 units",
                    "D) 15,000 units"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Contribution Margin per unit = $500 - $200 = $300. Breakeven Volume = Fixed Costs / Unit Contribution Margin = $6,000,000 / $300 = 20,000 units.",
                "company_context": f"Unit breakeven modeling is essential when evaluating cost structures at {company_name}."
            },
            {
                "turn_number": 9,
                "stage_title": "Round 1: Corporate Finance & Financial Modeling Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Return on Invested Capital (ROIC) vs WACC",
                "question": f"A target company earns $80,000,000 in Net Operating Profit After Taxes (NOPAT) on $500,000,000 of Invested Capital. If its WACC is 10%, what is its Economic Value Added (EVA)?",
                "options": [
                    "A) +$30,000,000 (ROIC = 16%, generating positive economic value spread of 6%)",
                    "B) +$10,000,000",
                    "C) -$20,000,000",
                    "D) +$50,000,000"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "ROIC = NOPAT / Invested Capital = $80M / $500M = 16%. Capital Charge = $500M * 10% = $50M. EVA = NOPAT - Capital Charge = $80M - $50M = +$30,000,000.",
                "company_context": f"Shareholder value creation analysis at {company_name} tracks ROIC spreads over WACC."
            },
            {
                "turn_number": 10,
                "stage_title": "Round 1: Corporate Finance & Financial Modeling Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Diluted Shares & Treasury Stock Method",
                "question": f"A public tech firm being advised by {company_name} has 10,000,000 basic shares outstanding at a current share price of $50. There are 1,000,000 in-the-money options outstanding with an average exercise price of $30. Under the Treasury Stock Method, what is the diluted share count?",
                "options": [
                    "A) 10,400,000 shares",
                    "B) 11,000,000 shares",
                    "C) 10,600,000 shares",
                    "D) 10,200,000 shares"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Proceeds from options = 1M * $30 = $30M. Shares repurchased with proceeds = $30M / $50 = 600,000 shares. Net new shares = 1,000,000 - 600,000 = 400,000. Diluted shares = 10M + 400k = 10,400,000.",
                "company_context": f"Per-share accretion and valuation models at {company_name} use the Treasury Stock Method."
            },

            # 10 Corporate Finance & Strategic Advisory Questions
            {
                "turn_number": 11,
                "stage_title": "Round 2: Strategic M&A Advisory & Corporate Finance",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "M&A Accretion / Dilution Dynamics",
                "question": f"Company A (P/E of 25x) proposes to acquire Company B (P/E of 15x) using 100% stock financing with zero transaction synergies. Assuming equal tax rates, will the transaction be immediately accretive or dilutive to Company A's Earnings Per Share (EPS)?",
                "options": [
                    "A) Accretive: acquiring a target with a lower P/E ratio using higher-valued stock yields immediate EPS accretion",
                    "B) Dilutive: acquiring any company without synergies reduces EPS",
                    "C) Breakeven: P/E ratios have no mathematical relationship to EPS accretion",
                    "D) Impossible to determine without revenue figures"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "In an all-stock transaction, when the acquirer's P/E is higher than the target's P/E (or acquirer cost of equity is lower than target earnings yield), the transaction is mathematically accretive to EPS.",
                "company_context": f"M&A merger consequence analysis at {company_name} relies on fundamental cost of capital rules."
            },
            {
                "turn_number": 12,
                "stage_title": "Round 2: Strategic M&A Advisory & Corporate Finance",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Comparable Company Analysis vs Precedent Transactions",
                "question": f"When evaluating a target company in an M&A advisory engagement at {company_name}, why do Precedent Transactions multiples typically trade at a premium compared to Public Comparable Company multiples?",
                "options": [
                    "A) Precedent transactions reflect a control premium paid by the acquirer to gain board control and realize operational synergies",
                    "B) Public comparable companies are smaller in size",
                    "C) Accounting standards differ between private and public companies",
                    "D) Precedent transactions exclude debt from enterprise value"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Acquirers pay a control premium (often 20-35% above unaffected market price) to gain unilateral voting control and unlock cost/revenue synergies.",
                "company_context": f"Valuation football field charts compiled at {company_name} benchmark control premiums explicitly."
            },
            {
                "turn_number": 13,
                "stage_title": "Round 2: Strategic M&A Advisory & Corporate Finance",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Capital Structure & Modigliani-Miller with Taxes",
                "question": f"According to corporate finance theory (Modigliani-Miller Theorem with corporate taxes), why does introducing debt into a company's capital structure initially increase firm value?",
                "options": [
                    "A) The interest tax shield: interest payments on debt are tax-deductible, reducing corporate tax liability and increasing after-tax cash flows to investors",
                    "B) Debt has zero default risk",
                    "C) Equity holders are guaranteed dividend returns",
                    "D) Debt eliminates depreciation expenses"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "The interest tax shield creates additional corporate value equal to the present value of tax savings (Tax Rate * Debt), up to the point where financial distress costs outweigh the tax benefit.",
                "company_context": f"Capital structure advisory at {company_name} optimizes leverage while preserving investment grade credit ratings."
            },
            {
                "turn_number": 14,
                "stage_title": "Round 2: Strategic M&A Advisory & Corporate Finance",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Strategic Synergies: Revenue vs Cost Synergies Credibility",
                "question": f"During M&A due diligence at {company_name}, why do institutional investors and investment committee members heavily discount projected revenue synergies compared to cost synergies?",
                "options": [
                    "A) Cost synergies (redundant headcount, duplicate vendor software, facility consolidation) are within management's direct operational control, while revenue synergies depend on unverified external customer cross-selling",
                    "B) Cost synergies cannot be modeled in Excel",
                    "C) Revenue synergies are subject to double taxation",
                    "D) Cost synergies are illegal in cross-border deals"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Cost cuts are execution-driven and highly predictable. Revenue cross-selling requires customer behavior changes that often take years or fail to materialize.",
                "company_context": f"Financial sponsors and corporate clients at {company_name} underwrite acquisitions primarily on tangible cost synergies."
            },
            {
                "turn_number": 15,
                "stage_title": "Round 2: Strategic M&A Advisory & Corporate Finance",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "LBO Value Creation Drivers",
                "question": f"In a Private Equity Leveraged Buyout (LBO) advisory engagement at {company_name}, what are the three primary drivers of internal rate of return (IRR) value creation across the holding period?",
                "options": [
                    "A) EBITDA growth, debt paydown (deleveraging), and multiple expansion (exit multiple > entry multiple)",
                    "B) Stock dividends, marketing campaigns, and hiring consultants",
                    "C) Inflation, currency hedging, and share dilution",
                    "D) Asset sales, IPO underpricing, and patent filings"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "LBO returns are mathematically driven by operational earnings growth (EBITDA), using free cash flows to retire acquisition debt, and market valuation multiple expansion.",
                "company_context": f"Private equity advisory teams at {company_name} conduct detailed IRR attribution bridges."
            },
            {
                "turn_number": 16,
                "stage_title": "Round 2: Strategic M&A Advisory & Corporate Finance",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Market Entry Strategy: Greenfield vs Acquisition",
                "question": f"A multinational enterprise client advised by {company_name} is evaluating entering a highly regulated foreign healthcare market. Which strategic framework justifies an acquisition over organic greenfield entry?",
                "options": [
                    "A) An acquisition bypasses multi-year regulatory licensing barriers, secures established distribution relationships, and eliminates cold-start customer acquisition friction",
                    "B) Greenfield entry is always illegal in healthcare",
                    "C) Acquisitions guarantee zero operational risk",
                    "D) Greenfield entry requires higher dividend payouts"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "In heavily regulated or entrenched markets, the speed-to-market, regulatory permits, and existing enterprise relationships justify an M&A premium over slow greenfield execution.",
                "company_context": f"Corporate strategy engagements at {company_name} evaluate build-versus-buy trade-offs."
            },
            {
                "turn_number": 17,
                "stage_title": "Round 2: Strategic M&A Advisory & Corporate Finance",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Working Capital Optimization: Cash Conversion Cycle",
                "question": f"A corporate client at {company_name} seeks to unlock liquidity without taking on external debt. Days Sales Outstanding (DSO) is 65 days, Days Inventory Outstanding (DIO) is 45 days, and Days Payable Outstanding (DPO) is 30 days. How can the Cash Conversion Cycle (CCC) be shortened to generate free cash flow?",
                "options": [
                    "A) Accelerate customer collections (lower DSO), improve inventory turnover (lower DIO), and negotiate extended supplier payment terms (higher DPO)",
                    "B) Increase DSO to 90 days and pay suppliers in cash upfront",
                    "C) Triple inventory stock in warehouses",
                    "D) Increase corporate debt covenants"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Cash Conversion Cycle = DSO + DIO - DPO = 65 + 45 - 30 = 80 days. Shortening DSO and DIO while extending DPO frees trapped working capital onto the balance sheet.",
                "company_context": f"Operational restructuring teams at {company_name} optimize cash conversion cycles to bolster corporate liquidity."
            },
            {
                "turn_number": 18,
                "stage_title": "Round 2: Strategic M&A Advisory & Corporate Finance",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Spin-off vs Carve-Out Divestiture Structuring",
                "question": f"In corporate portfolio restructuring at {company_name}, what is the primary structural difference between an equity carve-out and a corporate spin-off?",
                "options": [
                    "A) An equity carve-out is an IPO of a minority stake in a subsidiary that raises cash for the parent; a spin-off distributes shares of the new company tax-free to existing parent shareholders with no cash raised",
                    "B) A spin-off requires selling the entire company to a private equity firm",
                    "C) An equity carve-out is only permitted for distressed assets",
                    "D) A spin-off permanently dissolves both parent and subsidiary"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Carve-outs sell minority shares to the public market to raise external growth capital. Spin-offs distribute pro-rata shares to existing owners, unlocking conglomerate discount value tax-free.",
                "company_context": f"Divestiture advisory at {company_name} evaluates carve-out vs spin-off tax and capital implications."
            },
            {
                "turn_number": 19,
                "stage_title": "Round 2: Strategic M&A Advisory & Corporate Finance",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Defensive M&A Tactics (Poison Pill / Shareholder Rights Plan)",
                "question": f"When advising a public company board at {company_name} facing an unsolicited hostile takeover bid, what is the strategic objective of enacting a Shareholder Rights Plan ('Poison Pill')?",
                "options": [
                    "A) Diluting the hostile acquirer's ownership stake by allowing existing shareholders to buy discounted shares once a ownership threshold (e.g. 15%) is crossed, forcing the hostile bidder to negotiate with the board",
                    "B) Immediately declaring bankruptcy to prevent the takeover",
                    "C) Forbidding shareholders from voting in proxy contests",
                    "D) Transferring all company assets to private offshore accounts"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Poison pills make hostile takeovers prohibitively dilutive and expensive, compelling bidders to negotiate directly with the board to maximize purchase price for shareholders.",
                "company_context": f"Hostile takeover defense advisory at {company_name} protects shareholder value."
            },
            {
                "turn_number": 20,
                "stage_title": "Round 2: Strategic M&A Advisory & Corporate Finance",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Fairness Opinion & Fiduciary Board Responsibility",
                "question": f"What is the formal role of an investment bank rendering a Fairness Opinion to a corporate board of directors at {company_name} prior to signing a merger agreement?",
                "options": [
                    "A) Providing a professional financial assessment from an investment bank stating whether the proposed transaction consideration is fair, from a financial point of view, to shareholders",
                    "B) Guaranteeing that the target company's share price will double after closing",
                    "C) Providing legal indemnity against all future shareholder lawsuits",
                    "D) Approving executive severance packages"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "A Fairness Opinion is a financial analysis by an independent financial advisor supporting the board's fiduciary duty of care that the price offered is financially fair.",
                "company_context": f"Fairness opinions delivered by {company_name} represent core M&A governance deliverables."
            }
        ]

    elif track == "sales":
        return []

    else:
        return []
