class JurisCoreException(Exception):
    """Base exception for JurisCore application."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class DocumentParsingException(JurisCoreException):
    def __init__(self, message: str):
        super().__init__(message, code="DOCUMENT_PARSING_FAILED")

class RuleEvaluationException(JurisCoreException):
    def __init__(self, message: str):
        super().__init__(message, code="RULE_EVALUATION_FAILED")

class WorkflowException(JurisCoreException):
    def __init__(self, message: str):
        super().__init__(message, code="WORKFLOW_EXECUTION_FAILED")
