#!/usr/bin/env python3
"""Command-line interface for JD To Resume Customiser."""
import click
import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from agent import ResumeTailorAgent
from pdf_parser import ResumeParser
from pdf_generator import PDFGenerator
from config import settings

console = Console()


@click.group()
def cli():
    """JD To Resume Customiser - Customize your resume for each job description."""
    pass


@cli.command()
@click.option('--resume', '-r', required=True, type=click.Path(exists=True), help='Path to resume PDF')
@click.option('--job-description', '-j', required=True, type=click.Path(exists=True), help='Path to job description PDF or text file')
@click.option('--output-dir', '-o', default='output', help='Output directory for generated files')
def tailor(resume, job_description, output_dir):
    """Tailor your resume for a specific job description."""
    # Validate OpenAI API key
    if not settings.validate_api_keys():
        console.print("[bold red]Error:[/bold red] API key not configured!")
        console.print("Please set OPENAI_API_KEY in .env file")
        return

    console.print(Panel.fit(
        f"[bold cyan]JD To Resume Customiser[/bold cyan]\n"
        f"Provider: OpenAI | Model: {settings.model_name}",
        border_style="cyan"
    ))

    try:
        # Parse inputs
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Parsing resume...", total=None)
            resume_text = ResumeParser.extract_text_from_pdf(resume)

            progress.update(task, description="[cyan]Parsing job description...")
            jd_text = ResumeParser.extract_text_from_pdf(job_description)

            progress.update(task, description="[cyan]Initializing AI agent...")
            agent = ResumeTailorAgent()

            progress.update(task, description="[cyan]Generating tailored resume...")
            tailored_resume = agent.tailor_resume(resume_text, jd_text)

            progress.update(task, description="[cyan]Generating cover letter...")
            cover_letter = agent.generate_cover_letter(resume_text, jd_text)

            progress.update(task, description="[cyan]Analyzing skill gaps...")
            skill_gap_analysis = agent.analyze_skill_gaps(resume_text, jd_text)

            progress.update(task, description="[cyan]Generating PDF files...")
            pdf_gen = PDFGenerator()
            output_files = pdf_gen.generate_complete_package(
                tailored_resume,
                cover_letter,
                skill_gap_analysis,
                output_dir
            )

            progress.update(task, description="[green]Complete!")

        # Display results
        console.print("\n[bold green]Success![/bold green] Generated files:")
        for file_type, path in output_files.items():
            console.print(f"  • {file_type.replace('_', ' ').title()}: [cyan]{path}[/cyan]")

        # Show skill gap analysis preview
        console.print("\n[bold]Skill Gap Analysis Preview:[/bold]")
        console.print(Panel(skill_gap_analysis[:500] + "...", border_style="blue"))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise


@cli.command()
@click.option('--resume', '-r', required=True, type=click.Path(exists=True), help='Path to resume PDF')
@click.option('--job-description', '-j', required=True, type=click.Path(exists=True), help='Path to job description PDF')
def analyze(resume, job_description):
    """Analyze skill gaps between your resume and job requirements."""
    # Validate OpenAI API key
    if not settings.validate_api_keys():
        console.print("[bold red]Error:[/bold red] API key not configured!")
        console.print("Please set OPENAI_API_KEY in .env file")
        return

    console.print(Panel.fit(
        "[bold cyan]Skill Gap Analysis[/bold cyan]",
        border_style="cyan"
    ))

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Analyzing...", total=None)

            resume_text = ResumeParser.extract_text_from_pdf(resume)
            jd_text = ResumeParser.extract_text_from_pdf(job_description)

            agent = ResumeTailorAgent()
            analysis = agent.analyze_skill_gaps(resume_text, jd_text)

            progress.update(task, description="[green]Complete!")

        # Display analysis
        console.print("\n")
        md = Markdown(analysis)
        console.print(Panel(md, title="[bold]Skill Gap Analysis[/bold]", border_style="blue"))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise


@cli.command()
def config():
    """Show current configuration."""
    console.print(Panel.fit(
        f"[bold]Current Configuration[/bold]\n\n"
        f"Provider: [cyan]OpenAI[/cyan]\n"
        f"Model: [cyan]{settings.model_name}[/cyan]\n"
        f"API Key Configured: [{'green]Yes' if settings.validate_api_keys() else 'red]No'}[/]\n",
        border_style="blue"
    ))


if __name__ == '__main__':
    cli()
