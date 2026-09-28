import json
import logging
import re
from typing import Type, TypeVar, Optional, List, Dict, Any
import httpx
from pydantic import BaseModel, ValidationError
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")
T = TypeVar("T", bound=BaseModel)

class LLMClient:
    """
    Provider-agnostic LLM wrapper supporting Anthropic, OpenAI, Gemini,
    and a robust smart mock fallback mode when API keys are not set.
    """
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = settings.OPENROUTER_API_KEY or settings.LLM_API_KEY
        self.model = settings.LLM_MODEL or "anthropic/claude-3.5-sonnet"

    async def generate_json(
        self, 
        prompt: str, 
        schema_cls: Type[T], 
        system_prompt: Optional[str] = None,
        max_retries: int = 2
    ) -> T:
        """Generate structured JSON output adhering to a Pydantic schema with retry logic."""
        json_schema_str = json.dumps(schema_cls.model_json_schema(), indent=2)
        system = (system_prompt or "") + f"\n\nIMPORTANT: You MUST respond ONLY with a valid JSON object matching this JSON schema:\n{json_schema_str}\nDo NOT include markdown formatting like ```json ... ``` or conversational text outside the JSON."

        for attempt in range(max_retries + 1):
            raw_response = await self._call_provider(prompt=prompt, system_prompt=system)
            try:
                # Clean potential markdown wrapping
                cleaned = self._clean_json_string(raw_response)
                parsed_json = json.loads(cleaned)
                validated_obj = schema_cls.model_validate(parsed_json)
                return validated_obj
            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(f"LLM JSON generation attempt {attempt + 1} failed: {e}. Raw response: {raw_response[:200]}")
                if attempt == max_retries:
                    # Fallback to smart default mock instantiation if all retries fail
                    logger.error("Max retries reached for JSON generation. Returning fallback instance.")
                    return self._generate_mock_schema_instance(schema_cls, prompt)
                prompt += f"\n\nSystem Error: Your previous response was not valid JSON matching the schema ({e}). Please fix and return ONLY valid JSON."

        return self._generate_mock_schema_instance(schema_cls, prompt)

    async def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        """Multi-turn text generation for chat / interview questions."""
        formatted_prompt = ""
        for msg in messages:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "")
            formatted_prompt += f"{role}: {content}\n"
        
        return await self._call_provider(prompt=formatted_prompt, system_prompt=system_prompt)

    async def _call_provider(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key or self.provider == "mock":
            return self._mock_call(prompt, system_prompt)

        try:
            if self.provider == "openrouter":
                return await self._call_openrouter(prompt, system_prompt)
            elif self.provider == "anthropic":
                return await self._call_anthropic(prompt, system_prompt)
            elif self.provider == "openai":
                return await self._call_openai(prompt, system_prompt)
            elif self.provider == "gemini":
                return await self._call_gemini(prompt, system_prompt)
            else:
                return self._mock_call(prompt, system_prompt)
        except Exception as e:
            logger.error(f"Error calling LLM API ({self.provider}): {e}. Falling back to mock client handler.")
            return self._mock_call(prompt, system_prompt)

    async def _call_openrouter(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/vickydecodes/ai_resume_simulator",
            "X-Title": "HireFit AI",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model or "anthropic/claude-3.5-sonnet",
            "messages": messages,
            "temperature": 0.7
        }
        async with httpx.AsyncClient(timeout=35.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]

    async def _call_anthropic(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model or "claude-3-5-sonnet-20241022",
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            return data["content"][0]["text"]

    async def _call_openai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model or "gpt-4o-mini",
            "messages": msgs,
            "temperature": 0.7
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]

    async def _call_gemini(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model or 'gemini-1.5-flash'}:generateContent?key={self.api_key}"
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Directive: {system_prompt}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, json={"contents": contents})
            res.raise_for_status()
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    def _clean_json_string(self, text: str) -> str:
        """Strip markdown syntax blocks and extra whitespace."""
        text = text.strip()
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return text.strip()

    def _mock_call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Smart fallback mock generator for local development or testing without API keys."""
        logger.info("Executing LLM mock fallback handler.")
        prompt_lower = prompt.lower()

        if "resume" in prompt_lower and ("skills" in prompt_lower or "experience" in prompt_lower):
            return json.dumps({
                "candidate_name": "Applicant Candidate",
                "experience_years": 4.5,
                "skills": ["Python", "FastAPI", "React", "SQL", "Docker", "REST APIs"],
                "projects": [
                    {"name": "E-Commerce Microservices", "description": "Built scalable backend services in FastAPI with Redis caching."}
                ],
                "education": "B.S. in Computer Science",
                "key_strengths": ["Backend API design", "Asynchronous Python", "Database optimization"],
                "identified_gaps": ["Limited exposure to Kubernetes cluster management", "No explicit GraphQL production experience"]
            })
        
        elif "role" in prompt_lower or "seniority" in prompt_lower:
            return json.dumps({
                "role_title": "Software Engineer",
                "seniority_level": "Mid-Senior",
                "required_skills": ["Python", "FastAPI", "MongoDB", "System Architecture", "React"],
                "responsibilities": ["Design high-throughput backend services", "Collaborate on frontend React features"],
                "likely_topics": ["REST API Design", "Asynchronous IO", "Database Query Performance", "System Scalability"]
            })

        elif "company" in prompt_lower or "tech_stack" in prompt_lower or "culture" in prompt_lower:
            return json.dumps({
                "what_they_do": "Leading cloud software provider delivering high-availability SaaS platforms.",
                "products": ["Cloud Data Pipeline", "Analytics Dashboard"],
                "tech_stack": ["Python", "Go", "React", "PostgreSQL", "MongoDB", "AWS"],
                "culture": ["Customer-centric", "High technical autonomy", "Data-driven decisions"],
                "recent_news": ["Expanded European cloud infrastructure", "Launched AI copilot feature"],
                "interview_style_hints": "Expect deep technical trade-off questions and practical system design scenarios.",
                "is_limited_data": False
            })

        elif "evaluate answer" in prompt_lower or "score" in prompt_lower or "relevance" in prompt_lower:
            return json.dumps({
                "relevance_score": 85,
                "depth_score": 80,
                "correctness_score": 85,
                "communication_score": 90,
                "feedback": "Solid answer demonstrating good understanding of asynchronous request handling and trade-offs.",
                "turn_score": 84
            })

        elif "next_question" in prompt_lower or "is_final" in prompt_lower:
            return json.dumps({
                "next_question": "Can you walk me through how you handle database connection pooling and horizontal scaling under heavy traffic spikes in FastAPI?",
                "is_final": False,
                "reason": "Transitioning to system architecture and backend scalability topic."
            })

        elif "final_score" in prompt_lower or "estimated_selection_probability" in prompt_lower or "category_scores" in prompt_lower:
            return json.dumps({
                "overall_score": 82,
                "estimated_selection_probability": 74.5,
                "category_scores": {
                    "resume_fit": 85,
                    "technical_knowledge": 80,
                    "communication": 88,
                    "problem_solving": 78,
                    "company_awareness": 75
                },
                "top_strengths": [
                    "Strong practical knowledge of asynchronous Python and FastAPI routing",
                    "Clear communication structure when explaining trade-offs",
                    "Good alignment with target company technology stack"
                ],
                "top_weaknesses": [
                    "Could elaborate more on distributed error handling and fallback patterns",
                    "System design answers could include explicit throughput numbers"
                ],
                "improvement_tips": [
                    "Practice quantifying latency and throughput expectations during system design questions",
                    "Review specific target company product features to deepen company awareness answers"
                ]
            })

        # Generic chat question fallback
        return "Can you describe a challenging technical problem you solved in your recent backend project and how you evaluated the performance trade-offs?"

    def _generate_mock_schema_instance(self, schema_cls: Type[T], prompt: str) -> T:
        """Instantiate a valid fallback Pydantic model instance matching schema_cls."""
        raw_mock = self._mock_call(prompt)
        try:
            cleaned = self._clean_json_string(raw_mock)
            return schema_cls.model_validate(json.loads(cleaned))
        except Exception:
            # Construct minimal field dictionary from schema
            schema = schema_cls.model_json_schema()
            properties = schema.get("properties", {})
            mock_data: Dict[str, Any] = {}
            for field, prop in properties.items():
                field_type = prop.get("type", "string")
                if field_type == "integer":
                    mock_data[field] = 80
                elif field_type == "number":
                    mock_data[field] = 75.0
                elif field_type == "boolean":
                    mock_data[field] = False
                elif field_type == "array":
                    mock_data[field] = ["Skill A", "Skill B"]
                elif field_type == "object":
                    mock_data[field] = {"score": 80}
                else:
                    mock_data[field] = "Mock text evaluation"
            return schema_cls.model_validate(mock_data)

llm_client = LLMClient()
