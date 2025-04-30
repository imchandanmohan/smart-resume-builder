import json
import re
import subprocess
import os
from jinja2 import Environment, FileSystemLoader
from src.logger import get_logger
from src.custom_exception import CustomException

logger = get_logger(__name__)

class ResumePDFGenerator:
    def __init__(self, json_path: str, template_folder: str = 'resume', output_folder: str = 'resume'):
        """
        Initialize paths and Jinja2 environment.
        """
        self.json_path = json_path
        self.template_folder = template_folder
        self.output_folder = output_folder
        self.template_filename = 'resume_template.tex.j2'
        self.tex_filename = 'resume.tex'
        self.env = Environment(
            loader=FileSystemLoader(self.template_folder),
            autoescape=False,
            comment_start_string='((*',
            comment_end_string='*))'
        )
        self.env.filters['strip_diff'] = self.strip_diff

    @staticmethod
    def strip_diff(text):
        """
        Remove leading +/- signs in diff outputs if necessary.
        """
        return re.sub(r'^[+-]\s*', '', text, flags=re.MULTILINE)

    def generate_pdf(self):
        """
        Main execution method: loads JSON, renders LaTeX, compiles PDF.
        """
        try:
            logger.info("Starting PDF generation process...")

            # Step 1: Load JSON data
            data = self._load_json()

            # Step 2: Render LaTeX template
            output_tex = self._render_template(data)

            # Step 3: Save .tex file
            tex_path = os.path.join(self.output_folder, self.tex_filename)
            self._save_tex(output_tex, tex_path)

            # Step 4: Compile .tex to .pdf
            self._compile_pdf()

            logger.info("PDF generation completed successfully.")
        except Exception as e:
            logger.exception("PDF generation failed.")
            raise CustomException("Error during resume PDF generation.", e)

    def _load_json(self):
        """
        Load data from JSON file.
        """
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                logger.info(f"Loaded JSON file: {self.json_path}")
                return json.load(f)
        except Exception as e:
            logger.error("Failed to load JSON file.")
            raise CustomException("Failed to load JSON data.", e)

    def _render_template(self, data: dict) -> str:
        """
        Render the Jinja2 LaTeX template using provided data.
        """
        try:
            template = self.env.get_template(self.template_filename)
            logger.info(f"Rendering LaTeX template: {self.template_filename}")
            return template.render(data)
        except Exception as e:
            logger.error("Failed to render LaTeX template.")
            raise CustomException("Template rendering failed.", e)

    def _save_tex(self, content: str, tex_path: str):
        """
        Save the rendered LaTeX content to .tex file.
        """
        try:
            os.makedirs(self.output_folder, exist_ok=True)
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Wrote LaTeX file: {tex_path}")
        except Exception as e:
            logger.error("Failed to write LaTeX file.")
            raise CustomException("Saving .tex file failed.", e)

    def _compile_pdf(self):
        """
        Compile LaTeX to PDF using pdflatex.
        """
        try:
            logger.info("Compiling LaTeX to PDF...")
            cmd = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', self.tex_filename]
            # Run twice for references
            for i in range(2):
                subprocess.run(cmd, cwd=self.output_folder, check=True, stdout=subprocess.DEVNULL)
                logger.info(f"LaTeX compilation pass {i+1} complete.")
            logger.info("PDF successfully generated at resume/resume.pdf")
        except subprocess.CalledProcessError as e:
            logger.error("LaTeX compilation failed.")
            raise CustomException("LaTeX compilation error.", e)


if __name__ == "__main__":
    try:
        generator = ResumePDFGenerator(
            json_path='user_resume.json',
            template_folder='resume',
            output_folder='resume'
        )
        generator.generate_pdf()
    except Exception as e:
        print("❗ Resume PDF generation failed:", e)
