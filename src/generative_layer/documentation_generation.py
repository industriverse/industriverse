"""
Documentation Generation for Industriverse Generative Layer

This module implements the documentation generation system with protocol-native architecture
and MCP/A2A integration.
"""

import json
import logging
import os
import time
import uuid
from typing import Dict, Any, List, Optional, Union, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentationGeneration:
    """
    Implements the documentation generation system for the Generative Layer.
    Generates documentation for artifacts with protocol-native architecture.
    """
    
    def __init__(self, agent_core=None):
        """
        Initialize the documentation generation system.
        
        Args:
            agent_core: The agent core instance (optional)
        """
        self.agent_core = agent_core
        self.doc_templates = {}
        self.doc_history = {}
        
        # Initialize storage paths
        self.storage_path = os.path.join(os.getcwd(), "documentation_storage")
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Register default documentation templates
        self._register_default_templates()
        
        logger.info("Documentation Generation System initialized")
    
    def _register_default_templates(self):
        """Register default documentation templates."""
        # API documentation template
        self.register_doc_template(
            template_id="api_documentation",
            name="API Documentation",
            description="Template for generating API documentation",
            target_types=["api", "service", "function"],
            sections=[
                {
                    "id": "overview",
                    "title": "Overview",
                    "description": "General overview of the API",
                    "required": True
                },
                {
                    "id": "authentication",
                    "title": "Authentication",
                    "description": "Authentication methods and requirements",
                    "required": True
                },
                {
                    "id": "endpoints",
                    "title": "Endpoints",
                    "description": "API endpoints and their details",
                    "required": True,
                    "subsections": [
                        {
                            "id": "endpoint_url",
                            "title": "URL",
                            "required": True
                        },
                        {
                            "id": "endpoint_method",
                            "title": "Method",
                            "required": True
                        },
                        {
                            "id": "endpoint_params",
                            "title": "Parameters",
                            "required": True
                        },
                        {
                            "id": "endpoint_response",
                            "title": "Response",
                            "required": True
                        },
                        {
                            "id": "endpoint_examples",
                            "title": "Examples",
                            "required": False
                        }
                    ]
                },
                {
                    "id": "error_handling",
                    "title": "Error Handling",
                    "description": "Error codes and their meanings",
                    "required": True
                },
                {
                    "id": "rate_limiting",
                    "title": "Rate Limiting",
                    "description": "Rate limiting policies",
                    "required": False
                },
                {
                    "id": "examples",
                    "title": "Examples",
                    "description": "Usage examples",
                    "required": False
                }
            ],
            formats=["markdown", "html", "pdf"],
            metadata={
                "version": "1.0",
                "author": "Industriverse Generative Layer"
            }
        )
        
        # Component documentation template
        self.register_doc_template(
            template_id="component_documentation",
            name="Component Documentation",
            description="Template for generating component documentation",
            target_types=["component", "module", "class"],
            sections=[
                {
                    "id": "overview",
                    "title": "Overview",
                    "description": "General overview of the component",
                    "required": True
                },
                {
                    "id": "installation",
                    "title": "Installation",
                    "description": "Installation instructions",
                    "required": False
                },
                {
                    "id": "usage",
                    "title": "Usage",
                    "description": "Usage instructions and examples",
                    "required": True
                },
                {
                    "id": "api",
                    "title": "API Reference",
                    "description": "API reference documentation",
                    "required": True,
                    "subsections": [
                        {
                            "id": "methods",
                            "title": "Methods",
                            "required": True
                        },
                        {
                            "id": "properties",
                            "title": "Properties",
                            "required": True
                        },
                        {
                            "id": "events",
                            "title": "Events",
                            "required": False
                        }
                    ]
                },
                {
                    "id": "examples",
                    "title": "Examples",
                    "description": "Usage examples",
                    "required": True
                },
                {
                    "id": "troubleshooting",
                    "title": "Troubleshooting",
                    "description": "Common issues and solutions",
                    "required": False
                }
            ],
            formats=["markdown", "html", "pdf"],
            metadata={
                "version": "1.0",
                "author": "Industriverse Generative Layer"
            }
        )
        
        # User guide template
        self.register_doc_template(
            template_id="user_guide",
            name="User Guide",
            description="Template for generating user guides",
            target_types=["application", "system", "product"],
            sections=[
                {
                    "id": "introduction",
                    "title": "Introduction",
                    "description": "Introduction to the product",
                    "required": True
                },
                {
                    "id": "getting_started",
                    "title": "Getting Started",
                    "description": "Getting started guide",
                    "required": True,
                    "subsections": [
                        {
                            "id": "prerequisites",
                            "title": "Prerequisites",
                            "required": True
                        },
                        {
                            "id": "installation",
                            "title": "Installation",
                            "required": True
                        },
                        {
                            "id": "first_steps",
                            "title": "First Steps",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "features",
                    "title": "Features",
                    "description": "Product features",
                    "required": True
                },
                {
                    "id": "tutorials",
                    "title": "Tutorials",
                    "description": "Step-by-step tutorials",
                    "required": True
                },
                {
                    "id": "faq",
                    "title": "FAQ",
                    "description": "Frequently asked questions",
                    "required": False
                },
                {
                    "id": "troubleshooting",
                    "title": "Troubleshooting",
                    "description": "Common issues and solutions",
                    "required": False
                },
                {
                    "id": "glossary",
                    "title": "Glossary",
                    "description": "Glossary of terms",
                    "required": False
                }
            ],
            formats=["markdown", "html", "pdf"],
            metadata={
                "version": "1.0",
                "author": "Industriverse Generative Layer"
            }
        )
        
        # Industrial protocol documentation template
        self.register_doc_template(
            template_id="industrial_protocol",
            name="Industrial Protocol Documentation",
            description="Template for generating industrial protocol documentation",
            target_types=["protocol", "standard", "specification"],
            sections=[
                {
                    "id": "overview",
                    "title": "Overview",
                    "description": "General overview of the protocol",
                    "required": True
                },
                {
                    "id": "architecture",
                    "title": "Architecture",
                    "description": "Protocol architecture",
                    "required": True
                },
                {
                    "id": "message_format",
                    "title": "Message Format",
                    "description": "Protocol message format",
                    "required": True,
                    "subsections": [
                        {
                            "id": "header",
                            "title": "Header",
                            "required": True
                        },
                        {
                            "id": "payload",
                            "title": "Payload",
                            "required": True
                        },
                        {
                            "id": "footer",
                            "title": "Footer",
                            "required": False
                        }
                    ]
                },
                {
                    "id": "commands",
                    "title": "Commands",
                    "description": "Protocol commands",
                    "required": True
                },
                {
                    "id": "responses",
                    "title": "Responses",
                    "description": "Protocol responses",
                    "required": True
                },
                {
                    "id": "error_handling",
                    "title": "Error Handling",
                    "description": "Error handling procedures",
                    "required": True
                },
                {
                    "id": "security",
                    "title": "Security",
                    "description": "Security considerations",
                    "required": True
                },
                {
                    "id": "compliance",
                    "title": "Compliance",
                    "description": "Compliance requirements",
                    "required": True
                },
                {
                    "id": "examples",
                    "title": "Examples",
                    "description": "Usage examples",
                    "required": True
                }
            ],
            formats=["markdown", "html", "pdf"],
            metadata={
                "version": "1.0",
                "author": "Industriverse Generative Layer"
            }
        )
        
        # Low ticket offer documentation template
        self.register_doc_template(
            template_id="low_ticket_offer",
            name="Low Ticket Offer Documentation",
            description="Template for generating documentation for low ticket offers",
            target_types=["offer", "product", "service"],
            sections=[
                {
                    "id": "overview",
                    "title": "Overview",
                    "description": "General overview of the offer",
                    "required": True
                },
                {
                    "id": "value_proposition",
                    "title": "Value Proposition",
                    "description": "Value proposition of the offer",
                    "required": True
                },
                {
                    "id": "features",
                    "title": "Features",
                    "description": "Offer features",
                    "required": True
                },
                {
                    "id": "pricing",
                    "title": "Pricing",
                    "description": "Pricing information",
                    "required": True
                },
                {
                    "id": "implementation",
                    "title": "Implementation",
                    "description": "Implementation details",
                    "required": True,
                    "subsections": [
                        {
                            "id": "requirements",
                            "title": "Requirements",
                            "required": True
                        },
                        {
                            "id": "setup",
                            "title": "Setup",
                            "required": True
                        },
                        {
                            "id": "configuration",
                            "title": "Configuration",
                            "required": True
                        }
                    ]
                },
                {
                    "id": "use_cases",
                    "title": "Use Cases",
                    "description": "Example use cases",
                    "required": True
                },
                {
                    "id": "faq",
                    "title": "FAQ",
                    "description": "Frequently asked questions",
                    "required": False
                },
                {
                    "id": "support",
                    "title": "Support",
                    "description": "Support information",
                    "required": True
                }
            ],
            formats=["markdown", "html", "pdf"],
            metadata={
                "version": "1.0",
                "author": "Industriverse Generative Layer"
            }
        )
    
    def register_doc_template(self, 
                            template_id: str, 
                            name: str,
                            description: str,
                            target_types: List[str],
                            sections: List[Dict[str, Any]],
                            formats: List[str],
                            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a new documentation template.
        
        Args:
            template_id: Unique identifier for the template
            name: Name of the template
            description: Description of the template
            target_types: List of target types this template can document
            sections: List of sections in the template
            formats: List of supported output formats
            metadata: Additional metadata (optional)
            
        Returns:
            True if registration was successful, False otherwise
        """
        if template_id in self.doc_templates:
            logger.warning(f"Documentation template {template_id} already registered")
            return False
        
        timestamp = time.time()
        
        # Create template record
        template = {
            "id": template_id,
            "name": name,
            "description": description,
            "target_types": target_types,
            "sections": sections,
            "formats": formats,
            "metadata": metadata or {},
            "timestamp": timestamp
        }
        
        # Store template
        self.doc_templates[template_id] = template
        
        # Store template file
        template_path = os.path.join(self.storage_path, f"{template_id}_template.json")
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        logger.info(f"Registered documentation template {template_id}: {name}")
        
        # Emit MCP event for template registration
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/documentation/template_registered",
                {
                    "template_id": template_id,
                    "name": name,
                    "target_types": target_types
                }
            )
        
        return True
    
    def generate_documentation(self, 
                             artifact_id: str, 
                             artifact_type: str,
                             content: Any,
                             metadata: Dict[str, Any],
                             template_id: Optional[str] = None,
                             output_format: str = "markdown",
                             doc_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate documentation for an artifact.
        
        Args:
            artifact_id: ID of the artifact to document
            artifact_type: Type of the artifact
            content: Content of the artifact
            metadata: Metadata about the artifact
            template_id: ID of the documentation template to use (optional)
            output_format: Output format (default: markdown)
            doc_id: Optional ID for the documentation (generated if not provided)
            
        Returns:
            Documentation result if successful, None otherwise
        """
        # Select appropriate template if not specified
        if template_id is None:
            template_id = self._select_template_for_type(artifact_type)
            
        if template_id is None:
            logger.warning(f"No suitable documentation template found for type: {artifact_type}")
            return None
            
        if template_id not in self.doc_templates:
            logger.warning(f"Documentation template {template_id} not found")
            return None
        
        template = self.doc_templates[template_id]
        
        # Check if template supports this artifact type
        if artifact_type not in template["target_types"]:
            logger.warning(f"Template {template_id} does not support artifact type: {artifact_type}")
            return None
        
        # Check if template supports the requested output format
        if output_format not in template["formats"]:
            logger.warning(f"Template {template_id} does not support output format: {output_format}")
            return None
        
        # Generate documentation ID if not provided
        if doc_id is None:
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        
        timestamp = time.time()
        
        try:
            # Generate documentation content
            doc_content = self._generate_doc_content(template, content, metadata, output_format)
            
            # Create documentation result
            result = {
                "id": doc_id,
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "template_id": template_id,
                "output_format": output_format,
                "timestamp": timestamp,
                "status": "success",
                "content": doc_content
            }
            
            # Store documentation history
            self.doc_history[doc_id] = result
            
            # Store documentation result file (without content)
            result_for_storage = result.copy()
            result_for_storage.pop("content", None)
            
            result_path = os.path.join(self.storage_path, f"{doc_id}_result.json")
            with open(result_path, 'w') as f:
                json.dump(result_for_storage, f, indent=2)
            
            # Store documentation content separately
            content_path = os.path.join(self.storage_path, f"{doc_id}_content.{self._get_extension(output_format)}")
            with open(content_path, 'w') as f:
                f.write(doc_content)
            
            logger.info(f"Generated documentation {doc_id} for artifact {artifact_id} using template {template_id}")
            
            # Emit MCP event for documentation generation
            if self.agent_core:
                self.agent_core.send_mcp_event(
                    "generative_layer/documentation/artifact_documented",
                    {
                        "doc_id": doc_id,
                        "artifact_id": artifact_id,
                        "template_id": template_id,
                        "output_format": output_format
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating documentation for artifact {artifact_id}: {str(e)}")
            
            # Create failure result
            result = {
                "id": doc_id,
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "template_id": template_id,
                "output_format": output_format,
                "timestamp": timestamp,
                "status": "failed",
                "reason": f"Documentation generation error: {str(e)}"
            }
            
            # Store documentation history
            self.doc_history[doc_id] = result
            
            return result
    
    def get_documentation(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get documentation by ID.
        
        Args:
            doc_id: ID of the documentation to retrieve
            
        Returns:
            Documentation if found, None otherwise
        """
        if doc_id not in self.doc_history:
            logger.warning(f"Documentation {doc_id} not found")
            return None
        
        return self.doc_history[doc_id]
    
    def get_doc_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a documentation template by ID.
        
        Args:
            template_id: ID of the template to retrieve
            
        Returns:
            Documentation template if found, None otherwise
        """
        if template_id not in self.doc_templates:
            logger.warning(f"Documentation template {template_id} not found")
            return None
        
        return self.doc_templates[template_id]
    
    def _select_template_for_type(self, artifact_type: str) -> Optional[str]:
        """
        Select an appropriate documentation template for an artifact type.
        
        Args:
            artifact_type: Type of artifact
            
        Returns:
            Template ID if found, None otherwise
        """
        # Find templates that support this artifact type
        suitable_templates = []
        
        for template_id, template in self.doc_templates.items():
            if artifact_type in template["target_types"]:
                suitable_templates.append(template_id)
        
        if not suitable_templates:
            return None
        
        # For now, just return the first suitable template
        # In the future, this could be more sophisticated
        return suitable_templates[0]
    
    def _generate_doc_content(self, template: Dict[str, Any], content: Any, metadata: Dict[str, Any], output_format: str) -> str:
        """
        Generate documentation content based on template.
        
        Args:
            template: Documentation template
            content: Artifact content
            metadata: Artifact metadata
            output_format: Output format
            
        Returns:
            Generated documentation content
        """
        # Extract information from content and metadata
        doc_data = self._extract_doc_data(content, metadata)
        
        # Generate documentation based on template sections
        doc_content = ""
        
        # Add title
        doc_content += self._format_title(metadata.get("name", "Untitled"), output_format)
        
        # Add metadata section
        doc_content += self._format_metadata(metadata, output_format)
        
        # Add sections
        for section in template["sections"]:
            section_id = section["id"]
            section_title = section["title"]
            section_required = section.get("required", False)
            
            # Check if we have data for this section
            section_data = doc_data.get(section_id)
            
            if section_data is None and section_required:
                # Generate placeholder for required section
                section_data = f"[TODO: Add {section_title}]"
            
            if section_data is not None:
                # Add section title
                doc_content += self._format_section_title(section_title, output_format)
                
                # Add section content
                doc_content += self._format_section_content(section_data, output_format)
                
                # Add subsections if any
                if "subsections" in section:
                    for subsection in section["subsections"]:
                        subsection_id = subsection["id"]
                        subsection_title = subsection["title"]
                        subsection_required = subsection.get("required", False)
                        
                        # Check if we have data for this subsection
                        subsection_data = None
                        if isinstance(section_data, dict):
                            subsection_data = section_data.get(subsection_id)
                        
                        if subsection_data is None and subsection_required:
                            # Generate placeholder for required subsection
                            subsection_data = f"[TODO: Add {subsection_title}]"
                        
                        if subsection_data is not None:
                            # Add subsection title
                            doc_content += self._format_subsection_title(subsection_title, output_format)
                            
                            # Add subsection content
                            doc_content += self._format_section_content(subsection_data, output_format)
        
        # Add footer
        doc_content += self._format_footer(metadata, output_format)
        
        return doc_content
    
    def _extract_doc_data(self, content: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract documentation data from content and metadata.
        
        Args:
            content: Artifact content
            metadata: Artifact metadata
            
        Returns:
            Extracted documentation data
        """
        doc_data = {}
        
        # Extract overview from metadata
        if "description" in metadata:
            doc_data["overview"] = metadata["description"]
        
        # Extract other sections based on content type
        if isinstance(content, dict):
            # For API-like content
            if "endpoints" in content:
                doc_data["endpoints"] = content["endpoints"]
            
            if "authentication" in content:
                doc_data["authentication"] = content["authentication"]
            
            if "error_handling" in content:
                doc_data["error_handling"] = content["error_handling"]
            
            if "examples" in content:
                doc_data["examples"] = content["examples"]
            
            # For component-like content
            if "methods" in content:
                doc_data["api"] = {
                    "methods": content["methods"],
                    "properties": content.get("properties", {})
                }
            
            if "usage" in content:
                doc_data["usage"] = content["usage"]
            
            # For protocol-like content
            if "message_format" in content:
                doc_data["message_format"] = content["message_format"]
            
            if "commands" in content:
                doc_data["commands"] = content["commands"]
            
            if "responses" in content:
                doc_data["responses"] = content["responses"]
            
            # For offer-like content
            if "value_proposition" in content:
                doc_data["value_proposition"] = content["value_proposition"]
            
            if "features" in content:
                doc_data["features"] = content["features"]
            
            if "pricing" in content:
                doc_data["pricing"] = content["pricing"]
            
            if "implementation" in content:
                doc_data["implementation"] = content["implementation"]
            
            if "use_cases" in content:
                doc_data["use_cases"] = content["use_cases"]
        
        # Extract from metadata
        if "version" in metadata:
            doc_data["version"] = metadata["version"]
        
        if "author" in metadata:
            doc_data["author"] = metadata["author"]
        
        if "license" in metadata:
            doc_data["license"] = metadata["license"]
        
        return doc_data
    
    def _format_title(self, title: str, output_format: str) -> str:
        """
        Format title based on output format.
        
        Args:
            title: Title text
            output_format: Output format
            
        Returns:
            Formatted title
        """
        if output_format == "markdown":
            return f"# {title}\n\n"
        elif output_format == "html":
            return f"<h1>{title}</h1>\n\n"
        else:
            return f"{title}\n\n"
    
    def _format_section_title(self, title: str, output_format: str) -> str:
        """
        Format section title based on output format.
        
        Args:
            title: Section title
            output_format: Output format
            
        Returns:
            Formatted section title
        """
        if output_format == "markdown":
            return f"## {title}\n\n"
        elif output_format == "html":
            return f"<h2>{title}</h2>\n\n"
        else:
            return f"{title}\n\n"
    
    def _format_subsection_title(self, title: str, output_format: str) -> str:
        """
        Format subsection title based on output format.
        
        Args:
            title: Subsection title
            output_format: Output format
            
        Returns:
            Formatted subsection title
        """
        if output_format == "markdown":
            return f"### {title}\n\n"
        elif output_format == "html":
            return f"<h3>{title}</h3>\n\n"
        else:
            return f"{title}\n\n"
    
    def _format_section_content(self, content: Any, output_format: str) -> str:
        """
        Format section content based on output format.
        
        Args:
            content: Section content
            output_format: Output format
            
        Returns:
            Formatted section content
        """
        if content is None:
            return ""
        
        if isinstance(content, str):
            return f"{content}\n\n"
        elif isinstance(content, list):
            if output_format == "markdown":
                return "".join([f"- {item}\n" for item in content]) + "\n"
            elif output_format == "html":
                return "<ul>\n" + "".join([f"<li>{item}</li>\n" for item in content]) + "</ul>\n\n"
            else:
                return "".join([f"- {item}\n" for item in content]) + "\n"
        elif isinstance(content, dict):
            result = ""
            for key, value in content.items():
                if output_format == "markdown":
                    result += f"**{key}**: {value}\n\n"
                elif output_format == "html":
                    result += f"<p><strong>{key}</strong>: {value}</p>\n\n"
                else:
                    result += f"{key}: {value}\n\n"
            return result
        else:
            return f"{content}\n\n"
    
    def _format_metadata(self, metadata: Dict[str, Any], output_format: str) -> str:
        """
        Format metadata based on output format.
        
        Args:
            metadata: Metadata
            output_format: Output format
            
        Returns:
            Formatted metadata
        """
        result = ""
        
        # Extract relevant metadata
        version = metadata.get("version", "")
        author = metadata.get("author", "")
        date = metadata.get("date", "")
        
        if version or author or date:
            if output_format == "markdown":
                result += "*"
                if version:
                    result += f"Version: {version}"
                if author:
                    result += f" | Author: {author}"
                if date:
                    result += f" | Date: {date}"
                result += "*\n\n"
            elif output_format == "html":
                result += "<p><em>"
                if version:
                    result += f"Version: {version}"
                if author:
                    result += f" | Author: {author}"
                if date:
                    result += f" | Date: {date}"
                result += "</em></p>\n\n"
            else:
                if version:
                    result += f"Version: {version}\n"
                if author:
                    result += f"Author: {author}\n"
                if date:
                    result += f"Date: {date}\n"
                result += "\n"
        
        return result
    
    def _format_footer(self, metadata: Dict[str, Any], output_format: str) -> str:
        """
        Format footer based on output format.
        
        Args:
            metadata: Metadata
            output_format: Output format
            
        Returns:
            Formatted footer
        """
        result = ""
        
        # Extract relevant metadata
        copyright_info = metadata.get("copyright", "")
        license_info = metadata.get("license", "")
        
        if copyright_info or license_info:
            if output_format == "markdown":
                result += "---\n\n"
                if copyright_info:
                    result += f"*{copyright_info}*\n\n"
                if license_info:
                    result += f"*Licensed under {license_info}*\n\n"
            elif output_format == "html":
                result += "<hr>\n\n"
                if copyright_info:
                    result += f"<p><em>{copyright_info}</em></p>\n\n"
                if license_info:
                    result += f"<p><em>Licensed under {license_info}</em></p>\n\n"
            else:
                result += "\n"
                if copyright_info:
                    result += f"{copyright_info}\n"
                if license_info:
                    result += f"Licensed under {license_info}\n"
        
        return result
    
    def _get_extension(self, output_format: str) -> str:
        """
        Get file extension for output format.
        
        Args:
            output_format: Output format
            
        Returns:
            File extension
        """
        extensions = {
            "markdown": "md",
            "html": "html",
            "pdf": "pdf",
            "text": "txt"
        }
        
        return extensions.get(output_format, "txt")
    
    def export_doc_data(self) -> Dict[str, Any]:
        """
        Export documentation data for persistence.
        
        Returns:
            Documentation data
        """
        return {
            "doc_templates": self.doc_templates
        }
    
    def import_doc_data(self, doc_data: Dict[str, Any]) -> None:
        """
        Import documentation data from persistence.
        
        Args:
            doc_data: Documentation data to import
        """
        if "doc_templates" in doc_data:
            self.doc_templates = doc_data["doc_templates"]
        
        logger.info("Imported documentation data")
