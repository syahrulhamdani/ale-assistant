"""Tools to generate resume and download it in a PDF format."""
import logging

from langchain_core.tools import tool
from requests.exceptions import HTTPError, RequestException

from ale.core.config import config as c
from ale.models.resume import ResumeData
from ale.tools import BasicServices

_LOGGER = logging.getLogger(__name__)
service = BasicServices(c.RESUME_GENERATOR_URL)


@tool
def tool_generate_resume(data: ResumeData) -> dict[str, str]:
    """Tool to generate resume and download it in a PDF format.

    Args:
        data (ResumeData): Content of the resume.
    """
    url = f"{service.url}/sylab/api/v1/resume/generate"

    try:
        response = service.session.post(
            url, json=data.model_dump(),
            stream=True,
        )

        try:
            response.raise_for_status()
        except HTTPError as http_error:
            raise HTTPError(
                f"Failed to generate resume ({response.status_code}): "
                f"{http_error}"
            ) from http_error
    except RequestException as exc:
        _LOGGER.error("Error generating resume: %s", exc)
        raise RuntimeError(
            f"Error making request to resume generator: {exc}"
        ) from exc

    try:
        content_disposition = response.headers.get("Content-Disposition")
        filename = content_disposition.split("filename=")[1] + ".pdf"
        with open(filename, "wb") as file:
            file.write(response.content)
    except Exception as exc:
        _LOGGER.error("Unexpected error while saving resume: %s", exc)
        raise RuntimeError(
            f"Unexpected error while saving resume: {exc}"
        ) from exc

    return {"resume": filename}
