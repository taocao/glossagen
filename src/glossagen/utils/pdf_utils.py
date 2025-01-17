"""Base classes for document extraction."""

import os
import re
from typing import Dict, Optional

import dspy
import fitz  # PyMuPDF
from pydantic import BaseModel

from glossagen.utils import init_dspy


class MetadataSignature(dspy.Signature):
    """Extracts metadata from the publication text."""

    publication_text: str = dspy.InputField()
    title: str = dspy.OutputField(desc="Title of the publication.")
    doi: str = dspy.OutputField(desc="Digital Object Identifier (DOI) of the publication.")


class ResearchDoc(BaseModel):
    """A research paper."""

    doc_src: str
    fitz_paper: Optional[fitz.Document] = None
    paper: str = ""
    metadata_dict: Dict[str, str] = {}

    class Config:
        """Pydantic configuration for the ResearchDoc class."""

        arbitrary_types_allowed = True

    @classmethod
    def from_text(cls, text: str, doc_src: str) -> "ResearchDoc":
        """
        Create a ResearchDoc instance from text.

        Args:
            text (str): The text of the research paper.
            doc_src (str): The source of the document.

        Returns
        -------
            ResearchDoc: The created ResearchDoc instance.
        """
        research_doc = cls(doc_src="Latex", fitz_paper=None, paper=text)
        return research_doc

    @classmethod
    def from_dir(cls, paper_dir: str) -> "ResearchDoc":
        """
        Create a ResearchDoc instance from dir containing a research paper.

        Args:
            paper_dir (str): The dir path containing the research paper.

        Returns
        -------
            ResearchDoc: The created ResearchDoc instance.
        """
        paper_path = os.path.join(paper_dir, "paper.pdf")
        doc = fitz.open(paper_path)
        text = "".join(page.get_text() for page in doc)
        research_doc = cls(doc_src=paper_dir, fitz_paper=doc, paper=text)
        research_doc.extract_metadata()
        print("--------------------------------------------------")
        print(f"Lenght of paper: {len(research_doc.paper)}")
        # print(research_doc.paper[:3000])
        print("--------------------------------------------------")
        research_doc.trim_at_references()
        print(f"Lenght of paper: {len(research_doc.paper)}")
        # print(research_doc.paper[:3000])
        print("--------------------------------------------------")
        return research_doc

    def extract_metadata(self) -> None:
        """
        Extract metadata from the research paper.

        This method uses a metadata extractor to extract the title and
        DOI from the paper. The extracted metadata is stored in the
        `metadata_dict` attribute of the ResearchDoc instance.
        """
        # metadata_extractor = dspy.Predict(MetadataSignature)
        # metadata = metadata_extractor(publication_text=self.paper[:3000])
        # self.metadata_dict = {
        #     "title": metadata.title.lstrip("Title: "),
        #     "doi": metadata.doi,
        # }
        title = "foo"
        doi = "bar"
        self.metadata_dict = {"title": title, "doi": doi}

    def trim_at_references(self) -> None:
        """Trim the document text at the start of the references section."""
        # Regex to detect 'REFERENCES' and ensure it's followed by typical reference entries
        pattern = re.compile(
            r"\bREFERENCES\b\s*" r"(?=\s*(?:\(\d+\)|\d+\.)\s+[A-Z][a-z]+.*?\d{4})",
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(self.paper)
        if match:
            # If 'REFERENCES' is found, cut the text
            self.paper = self.paper[: match.start()]


class ResearchDocLoader:
    """A class for loading research documents from a directory."""

    def __init__(self, directory: str):
        """
        Initialize a ResearchDocLoader object.

        Args:
            directory (str): The directory path where the research
            documents are located.

        Raises
        ------
            FileNotFoundError: If the specified directory does not exist.
        """
        self.directory = directory
        if not os.path.exists(directory):
            raise FileNotFoundError(f"The specified directory {directory} does not exist.")

    def load(self) -> ResearchDoc:
        """
        Load the research document from the specified directory.

        Returns
        -------
            ResearchDoc: The loaded research document.

        Raises
        ------
            FileNotFoundError: If the required file 'paper.pdf' is not
            found in the directory.
        """
        file_path = os.path.join(self.directory, "paper.pdf")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Required file 'paper.pdf' not found in {self.directory}.")
        return ResearchDoc.from_dir(self.directory)


def main() -> None:
    """Demonstrate the usage of the ResearchDoc class."""
    # document_directory = (
    #     "/Users/magdalenalederbauer/projects/glossagen/papers/Chem. Rev. 2018, 118, 2718-2768"
    # )
    # document_directory = (
    #     "/Users/magdalenalederbauer/projects/glossagen/papers/Chem. Rev. 2022, 122, 12207-12243"
    # )
    document_directory = "./papers/Chem. Rev. 2024, 124, 2352-2418"

    init_dspy()
    loader = ResearchDocLoader(document_directory)
    research_doc = loader.load()
    research_doc.extract_metadata()

    print("--------------------------------------------------")
    print("Extracted Metadata:")
    for key, value in research_doc.metadata_dict.items():
        print(f"{key}: {value}")
    print("--------------------------------------------------")
    print("Paper Text:", research_doc.paper[:1000])


if __name__ == "__main__":
    main()
