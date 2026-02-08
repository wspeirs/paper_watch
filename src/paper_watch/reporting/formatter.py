from typing import List, Dict, Any
from datetime import datetime
from ..models import Paper
from ..intelligence import DeepAnalysisResult

class ReportFormatter:
    @staticmethod
    def format_markdown(
        relevant_papers: List[tuple[Paper, DeepAnalysisResult]], 
        discarded_papers: List[Paper]
    ) -> str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        report = f"# Paper Watch Daily Digest - {date_str}\n\n"
        
        report += "## Executive Summaries of Relevant Papers\n\n"
        if not relevant_papers:
            report += "No highly relevant papers found today.\n\n"
        else:
            for paper, analysis in relevant_papers:
                report += f"### {paper.title}\n"
                report += f"**Source:** {paper.source.upper()} ({paper.source_id})  \n"
                report += f"**Authors:** {', '.join(paper.authors)}  \n"
                report += f"**PDF:** [{paper.pdf_url}]({paper.pdf_url})\n\n"
                
                report += "#### Summary\n"
                report += f"{analysis.summary}\n\n"
                
                report += "#### Methodology\n"
                report += f"{analysis.methodology}\n\n"
                
                report += "#### Data\n"
                report += f"{analysis.data}\n\n"
                
                report += "#### Results\n"
                report += f"{analysis.results}\n\n"
                
                report += "---\n\n"

        report += "## Discarded Titles (Manual Review Recommended)\n\n"
        if not discarded_papers:
            report += "No papers were discarded today.\n\n"
        else:
            for paper in discarded_papers:
                report += f"- {paper.title} ({paper.source.upper()}: {paper.source_id})\n"
        
        return report

    @staticmethod
    def format_html(
        relevant_papers: List[tuple[Paper, DeepAnalysisResult]], 
        discarded_papers: List[Paper]
    ) -> str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        html = f"<html><body><h1>Paper Watch Daily Digest - {date_str}</h1>"
        
        html += "<h2>Executive Summaries of Relevant Papers</h2>"
        if not relevant_papers:
            html += "<p>No highly relevant papers found today.</p>"
        else:
            for paper, analysis in relevant_papers:
                html += f"<h3>{paper.title}</h3>"
                html += f"<p><b>Source:</b> {paper.source.upper()} ({paper.source_id})<br>"
                html += f"<b>Authors:</b> {', '.join(paper.authors)}<br>"
                html += f"<b>PDF:</b> <a href='{paper.pdf_url}'>{paper.pdf_url}</a></p>"
                
                html += "<h4>Summary</h4>"
                html += f"<p>{analysis.summary}</p>"
                
                html += "<h4>Methodology</h4>"
                html += f"<p>{analysis.methodology}</p>"
                
                html += "<h4>Data</h4>"
                html += f"<p>{analysis.data}</p>"
                
                html += "<h4>Results</h4>"
                html += f"<p>{analysis.results}</p>"
                html += "<hr>"

        html += "<h2>Discarded Titles (Manual Review Recommended)</h2><ul>"
        if not discarded_papers:
            html += "<li>No papers were discarded today.</li>"
        else:
            for paper in discarded_papers:
                html += f"<li>{paper.title} ({paper.source.upper()}: {paper.source_id})</li>"
        html += "</ul></body></html>"
        
        return html