import google.generativeai as genai
import os

def agent_research_summarizer(text):
    """
    Agent 1: Research Analyst.
    Reads the raw PDF text and creates a structured summary/brief for the writer.
    """
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    prompt = f"""
    You are an expert Research Analyst. Your goal is to analyze the provided text and produce a detailed content brief for a blog writer.
    
    1. Read the text thoroughly.
    2. Extract the core message, key technical details, and interesting facts.
    3. Structure the output as a "Content Brief" that a writer can easily turn into a blog post.
    
    Raw Text:
    {text}
    
    Content Brief:
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error during research: {e}"

def agent_blog_writer(summary):
    """
    Agent 2: Professional Blog Writer.
    Takes the brief from the Research Analyst and writes the final post.
    """
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    prompt = f"""
    You are a Senior Tech Blog Writer. You have just received a Content Brief from your Research Analyst.
    Your task is to write a high-quality, engaging blog post based *only* on this brief.
    
    Guidelines:
    - Tone: Professional, enthusiastic, and expert.
    - Structure: Catchy Title -> Hook -> Body Paragraphs (with headers) -> Conclusion.
    - Formatting: Use Markdown.
    
    Research Brief:
    {summary}
    
    Final Blog Post:
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error during blogging: {e}"

def run_blog_pipeline(text):
    """
    Orchestrates the full Agent 1 -> Agent 2 pipeline.
    Returns a dictionary with the results.
    """
    # Step 1: Research
    brief = agent_research_summarizer(text)
    if "Error" in brief:
        return {"error": brief}
        
    # Step 2: Write (using the brief from Step 1)
    blog = agent_blog_writer(brief)
    if "Error" in blog:
        return {"error": blog}
        
    return {
        "brief": brief,
        "blog_post": blog
    }
