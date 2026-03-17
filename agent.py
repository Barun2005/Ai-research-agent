from typing import Generator
import google.generativeai as genai
import google.generativeai.protos as protos
from duckduckgo_search import DDGS
import json
import os
from dotenv import load_dotenv

load_dotenv()

def build_tools():
    return [
        protos.Tool(function_declarations=[
            protos.FunctionDeclaration(
                name="think",
                description="Think through a problem step by step. Plan your research approach.",
                parameters=protos.Schema(
                    type=protos.Type.OBJECT,
                    properties={
                        "thought": protos.Schema(
                            type=protos.Type.STRING,
                            description="Your detailed reasoning or research plan"
                        )
                    },
                    required=["thought"]
                )
            ),
            protos.FunctionDeclaration(
                name="search_topic",
                description="Search for information on a specific topic or subtopic.",
                parameters=protos.Schema(
                    type=protos.Type.OBJECT,
                    properties={
                        "topic": protos.Schema(
                            type=protos.Type.STRING,
                            description="The specific topic to research"
                        ),
                        "focus": protos.Schema(
                            type=protos.Type.STRING,
                            description="Aspect to focus on: overview, technical, examples, history, applications, pros_cons"
                        )
                    },
                    required=["topic", "focus"]
                )
            ),
            protos.FunctionDeclaration(
                name="analyze",
                description="Analyze gathered information, find patterns and insights.",
                parameters=protos.Schema(
                    type=protos.Type.OBJECT,
                    properties={
                        "subject": protos.Schema(
                            type=protos.Type.STRING,
                            description="What to analyze"
                        ),
                        "analysis_type": protos.Schema(
                            type=protos.Type.STRING,
                            description="Type: compare, evaluate, summarize, critique, synthesize"
                        )
                    },
                    required=["subject", "analysis_type"]
                )
            ),
            protos.FunctionDeclaration(
                name="write_section",
                description="Write a specific section of the final report.",
                parameters=protos.Schema(
                    type=protos.Type.OBJECT,
                    properties={
                        "section_title": protos.Schema(
                            type=protos.Type.STRING,
                            description="Title of this section"
                        ),
                        "content_brief": protos.Schema(
                            type=protos.Type.STRING,
                            description="What this section should cover"
                        )
                    },
                    required=["section_title", "content_brief"]
                )
            ),
            protos.FunctionDeclaration(
                name="finalize_report",
                description="Compile all gathered information into the final report. Always call this LAST.",
                parameters=protos.Schema(
                    type=protos.Type.OBJECT,
                    properties={
                        "format": protos.Schema(
                            type=protos.Type.STRING,
                            description="Format: detailed_report, executive_summary, bullet_points, qa_format"
                        ),
                        "include_sections": protos.Schema(
                            type=protos.Type.ARRAY,
                            items=protos.Schema(type=protos.Type.STRING),
                            description="List of section titles for the report"
                        )
                    },
                    required=["format", "include_sections"]
                )
            ),
        ])
    ]


    return "Tool executed."


class ResearchAgent:
    def __init__(self, api_key: str | None = None, max_steps: int = 5, output_format: str = "Detailed Report"):
        actual_key = api_key or os.getenv("GEMINI_API_KEY")
        if not actual_key:
            raise ValueError("API Key not found. Set GEMINI_API_KEY in .env file.")
        
        genai.configure(api_key=actual_key)
        tools = build_tools()
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-lite-preview-0205",
            tools=tools,
        )
        self.sub_model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite-preview-0205")
        self.max_steps = max_steps
        self.output_format = output_format
        self.context: list[str] = []
        self.final_result: str | None = None
        self.fallback_models = [
            "gemini-2.0-flash-lite-preview-0205",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-2.0-flash",
        ]

    def _generate_with_fallback(self, prompt: str, is_sub_model: bool = True) -> str:
        """Helper to generate content with automatic model fallback on 429 errors."""
        last_error = ""
        # Try primary model first, then fallbacks
        models_to_try = self.fallback_models if is_sub_model else [self.model.model_name] + self.fallback_models
        
        for model_name in dict.fromkeys(models_to_try): # Unique preserving order
            try:
                m = genai.GenerativeModel(model_name)
                response = m.generate_content(prompt)
                return response.text
            except Exception as e:
                last_error = str(e)
                if "429" in last_error:
                    continue # Try next model
                raise e # Real error, don't fallback
        
        raise Exception(f"All models exhausted. Last error: {last_error}")

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        if tool_name == "think":
            return f"Plan recorded: {tool_input.get('thought', '')}"

        elif tool_name == "search_topic":
            topic = tool_input.get("topic", "")
            focus = tool_input.get("focus", "overview")
            try:
                with DDGS() as ddgs:
                    # Get a small number of results for the topic
                    results = list(ddgs.text(f"{topic} {focus}", max_results=5))
                    if not results:
                        return f"No real-world search results found for '{topic}'."
                    
                    # Format the results into a readable chunk
                    formatted = []
                    for i, r in enumerate(results, 1):
                        title = str(r.get('title', 'N/A'))
                        body = str(r.get('body', 'N/A'))
                        href = str(r.get('href', 'N/A'))
                        formatted.append(f"Result {i}: {title}\nSource: {href}\nSnippet: {body}\n")
                    
                    search_data = "\n".join(formatted)
                    
                    prompt = f"""Synthesize the following search results for the topic '{topic}' (Focus: {focus}).
                    
Search Results:
{search_data}

Provide a detailed summary (3-5 paragraphs) with facts, key concepts, and insights from these results. Be accurate and educational."""
                    
                    return self._generate_with_fallback(prompt, is_sub_model=True)
            except Exception as e:
                return f"Search error (DDG): {str(e)}"

        elif tool_name == "analyze":
            subject = tool_input.get("subject", "")
            ctx = "\n".join([f"- {c[:200]}" for c in self.context[-3:]])
            prompt = f"Analyze {subject} given this research context:\n{ctx}"
            return self._generate_with_fallback(prompt)

        elif tool_name == "write_section":
            title = tool_input.get("section_title", "")
            brief = tool_input.get("content_brief", "")
            ctx = "\n".join(self.context[-3:])
            prompt = f"Write the '{title}' section for a report. Cover: {brief}\nContext:\n{ctx}"
            return self._generate_with_fallback(prompt)

        elif tool_name == "finalize_report":
            return "Finalize triggered."

        return "Tool executed."

    def _format_key(self) -> str:
        return {
            "Detailed Report":   "detailed_report",
            "Executive Summary": "executive_summary",
            "Bullet Points":     "bullet_points",
            "Q&A Format":        "qa_format",
        }.get(self.output_format, "detailed_report")

    def _step_type(self, tool_name: str) -> str:
        return {
            "think":           "thinking",
            "search_topic":    "searching",
            "analyze":         "analyzing",
            "write_section":   "writing",
            "finalize_report": "done",
        }.get(tool_name, "thinking")

    def _step_label(self, tool_name: str, inp: dict) -> str:
        if tool_name == "think":           return "Planning approach"
        if tool_name == "search_topic":    return f"Searching: {inp.get('topic','')[:45]}"
        if tool_name == "analyze":         return f"Analyzing: {inp.get('subject','')[:45]}"
        if tool_name == "write_section":   return f"Writing: {inp.get('section_title','')[:45]}"
        if tool_name == "finalize_report": return "Compiling final report"
        return "Processing"

    def _step_text(self, tool_name: str, inp: dict) -> str:
        if tool_name == "think":           return inp.get("thought", "")[:180]
        if tool_name == "search_topic":    return f"Focus: {inp.get('focus','overview')} | Topic: {inp.get('topic','')}"
        if tool_name == "analyze":         return f"Running {inp.get('analysis_type','analysis')} analysis..."
        if tool_name == "write_section":   return inp.get("content_brief", "")[:180]
        if tool_name == "finalize_report": return f"Format: {self.output_format} | Sections: {len(inp.get('include_sections', []))}"
        return ""

    def run(self, query: str) -> Generator[dict, None, None]:
        fmt = self._format_key()
        system_msg = f"""You are an autonomous AI research agent. Research the given topic thoroughly.

Follow this exact sequence:
1. 'think' — plan your research strategy
2. 'search_topic' — search 2-3 different subtopics/aspects
3. 'analyze' — synthesize all findings
4. 'write_section' — draft key sections (optional)
5. 'finalize_report' — compile the final report (ALWAYS do this last, use format='{fmt}')

Rules:
- Be autonomous, do NOT ask questions
- Always end with finalize_report
- Max steps allowed: {self.max_steps}

Query: {query}"""

        chat = self.model.start_chat(enable_automatic_function_calling=False)
        step_num = 0

        try:
            response = chat.send_message(system_msg)
        except Exception as e:
            yield {"step_num": 1, "type": "error", "label": "API Error", "text": str(e)}
            self.final_result = f"Error: {str(e)}"
            return

        while step_num < self.max_steps:
            step_num += 1
            has_tool = False

            try:
                candidates = response.candidates
                if not candidates:
                    break

                parts = candidates[0].content.parts or []
                tool_responses = []

                for part in parts:
                    fn = getattr(part, "function_call", None)
                    if fn and fn.name:
                        has_tool = True
                        name = fn.name
                        inp = dict(fn.args)

                        yield {
                            "step_num": step_num,
                            "type":     self._step_type(name),
                            "label":    self._step_label(name, inp),
                            "text":     self._step_text(name, inp),
                        }

                        result = self._execute_tool(name, inp)
                        self.context.append(f"[{name}] {result[:250]}")

                        if name == "finalize_report":
                            self.final_result = self._build_report(query, inp)
                            return

                        tool_responses.append(
                            protos.Part(
                                function_response=protos.FunctionResponse(
                                    name=name,
                                    response={"result": result[:400]}
                                )
                            )
                        )

                if tool_responses:
                    response = chat.send_message(tool_responses)
                elif not has_tool:
                    text_found = False
                    for part in parts:
                        if getattr(part, "text", None) and part.text.strip():
                            text_found = True
                            # If it's pure text, show it as thinking/planning and nudge if needed
                            yield {
                                "step_num": step_num,
                                "type": "thinking",
                                "label": "Observation",
                                "text": part.text[:180],
                            }
                            # Check if the model is ending or just talking
                            # If it's a long text and looks like a result, we might take it.
                            # But usually we want it to call finalize_report.
                            if step_num >= self.max_steps:
                                self.final_result = part.text
                                return
                            
                            # Nudge the model to follow the tools if it's just chatting
                            response = chat.send_message("Please proceed with the appropriate tool for your next step, or finalize the report if you are finished.")
                            break # Go to next iteration of while loop
                    
                    if not text_found:
                        break

            except Exception as e:
                yield {"step_num": step_num, "type": "error", "label": "Error", "text": str(e)}
                break

        if not self.final_result:
            self.final_result = self._build_report(query, {"format": fmt, "include_sections": []})

    def _build_report(self, query: str, tool_input: dict) -> str:
        ctx = "\n\n".join(self.context) if self.context else "No context gathered."
        fmt = tool_input.get("format", "detailed_report")
        sections = tool_input.get("include_sections", [])

        instructions = {
            "detailed_report":   "Write a comprehensive report with ## headings. Include: Executive Summary, main sections, Key Findings, and Conclusion.",
            "executive_summary": "Write a concise 3-4 paragraph executive summary covering key points and recommendations.",
            "bullet_points":     "Present findings as organized bullet points with bold category headers.",
            "qa_format":         "Present as Q&A. Format: **Q: question?** then **A:** detailed answer.",
        }

        prompt = f"""Create a final research report.

Query: {query}

Research gathered:
{ctx}

{instructions.get(fmt, instructions['detailed_report'])}

{f'Cover these sections: {", ".join(sections)}' if sections else ''}

Use clear markdown formatting."""

        try:
            response = self.sub_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"## Research Report\n\n**Query:** {query}\n\n**Error:** {str(e)}\n\n{ctx}"