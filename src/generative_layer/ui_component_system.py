"""
UI Component System for Industriverse Generative Layer

This module implements the UI component system for generating reusable UI components
with protocol-native architecture and MCP/A2A integration.
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

class UIComponentSystem:
    """
    Implements the UI component system for the Generative Layer.
    Generates reusable UI components with protocol-native architecture.
    """
    
    def __init__(self, agent_core=None):
        """
        Initialize the UI component system.
        
        Args:
            agent_core: The agent core instance (optional)
        """
        self.agent_core = agent_core
        self.components = {}
        self.component_categories = {}
        self.renderers = {}
        self.render_history = {}
        
        # Initialize storage paths
        self.storage_path = os.path.join(os.getcwd(), "ui_component_storage")
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Register default renderers
        self._register_default_renderers()
        
        logger.info("UI Component System initialized")
    
    def _register_default_renderers(self):
        """Register default UI component renderers."""
        self.register_renderer("react", self._render_react_component)
        self.register_renderer("vue", self._render_vue_component)
        self.register_renderer("angular", self._render_angular_component)
        self.register_renderer("html", self._render_html_component)
        self.register_renderer("svelte", self._render_svelte_component)
    
    def register_component(self, 
                          component_id: str, 
                          name: str,
                          description: str,
                          component_type: str,
                          content: Dict[str, Any],
                          props: List[Dict[str, Any]],
                          category: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a new UI component.
        
        Args:
            component_id: Unique identifier for the component
            name: Name of the component
            description: Description of the component
            component_type: Type of component (react, vue, angular, html, svelte)
            content: Component content (structure depends on component_type)
            props: List of props/parameters for the component
            category: Category of the component (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            True if registration was successful, False otherwise
        """
        if component_id in self.components:
            logger.warning(f"Component {component_id} already registered")
            return False
        
        if component_type not in self.renderers:
            logger.warning(f"Unknown component type: {component_type}")
            return False
        
        timestamp = time.time()
        
        # Create component record
        component = {
            "id": component_id,
            "name": name,
            "description": description,
            "type": component_type,
            "content": content,
            "props": props,
            "category": category,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "version": 1
        }
        
        # Store component
        self.components[component_id] = component
        
        # Add to category
        if category:
            if category not in self.component_categories:
                self.component_categories[category] = []
            
            self.component_categories[category].append(component_id)
        
        # Store component file
        component_path = os.path.join(self.storage_path, f"{component_id}_component.json")
        with open(component_path, 'w') as f:
            json.dump(component, f, indent=2)
        
        logger.info(f"Registered component {component_id}: {name}")
        
        # Emit MCP event for component registration
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/ui_component/registered",
                {
                    "component_id": component_id,
                    "name": name,
                    "type": component_type
                }
            )
        
        return True
    
    def update_component(self, 
                        component_id: str, 
                        content: Optional[Dict[str, Any]] = None,
                        props: Optional[List[Dict[str, Any]]] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing UI component.
        
        Args:
            component_id: ID of the component to update
            content: New component content (optional)
            props: New list of props (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if update was successful, False otherwise
        """
        if component_id not in self.components:
            logger.warning(f"Component {component_id} not found")
            return False
        
        component = self.components[component_id]
        timestamp = time.time()
        
        # Update component
        if content is not None:
            component["content"] = content
        
        if props is not None:
            component["props"] = props
        
        if metadata is not None:
            component["metadata"].update(metadata)
        
        component["timestamp"] = timestamp
        component["version"] += 1
        
        # Store updated component
        self.components[component_id] = component
        
        # Store component file
        component_path = os.path.join(self.storage_path, f"{component_id}_component.json")
        with open(component_path, 'w') as f:
            json.dump(component, f, indent=2)
        
        logger.info(f"Updated component {component_id} to version {component['version']}")
        
        # Emit MCP event for component update
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/ui_component/updated",
                {
                    "component_id": component_id,
                    "name": component["name"],
                    "version": component["version"]
                }
            )
        
        return True
    
    def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a component by ID.
        
        Args:
            component_id: ID of the component to retrieve
            
        Returns:
            Component data if found, None otherwise
        """
        if component_id not in self.components:
            logger.warning(f"Component {component_id} not found")
            return None
        
        return self.components[component_id]
    
    def get_components_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all components in a category.
        
        Args:
            category: Category to retrieve components for
            
        Returns:
            List of components in the category
        """
        if category not in self.component_categories:
            logger.warning(f"Category {category} not found")
            return []
        
        component_ids = self.component_categories[category]
        components = [self.components[cid] for cid in component_ids if cid in self.components]
        
        return components
    
    def register_renderer(self, component_type: str, renderer: Callable) -> bool:
        """
        Register a component renderer.
        
        Args:
            component_type: Type of component to register renderer for
            renderer: Renderer function
            
        Returns:
            True if registration was successful, False otherwise
        """
        if component_type in self.renderers:
            logger.warning(f"Renderer for {component_type} already registered")
            return False
        
        self.renderers[component_type] = renderer
        logger.info(f"Registered renderer for {component_type}")
        
        return True
    
    def render_component(self, 
                        component_id: str, 
                        props: Dict[str, Any],
                        render_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Render a UI component with the provided props.
        
        Args:
            component_id: ID of the component to render
            props: Props to use in rendering
            render_id: Optional ID for the render (generated if not provided)
            
        Returns:
            Render result if successful, None otherwise
        """
        if component_id not in self.components:
            logger.warning(f"Component {component_id} not found")
            return None
        
        component = self.components[component_id]
        component_type = component["type"]
        
        if component_type not in self.renderers:
            logger.warning(f"No renderer found for component type: {component_type}")
            return None
        
        # Generate render ID if not provided
        if render_id is None:
            render_id = f"render_{uuid.uuid4().hex[:8]}"
        
        timestamp = time.time()
        
        # Validate props
        required_props = {prop["name"] for prop in component["props"] if prop.get("required", False)}
        provided_props = set(props.keys())
        
        missing_props = required_props - provided_props
        if missing_props:
            logger.warning(f"Missing required props: {missing_props}")
            
            # Create failure result
            result = {
                "id": render_id,
                "component_id": component_id,
                "timestamp": timestamp,
                "status": "failed",
                "reason": f"Missing required props: {missing_props}",
                "props": props
            }
            
            self.render_history[render_id] = result
            return result
        
        # Render component
        try:
            renderer = self.renderers[component_type]
            rendered_content = renderer(component["content"], props)
            
            # Create success result
            result = {
                "id": render_id,
                "component_id": component_id,
                "timestamp": timestamp,
                "status": "success",
                "content": rendered_content,
                "props": props,
                "component_name": component["name"],
                "component_type": component_type
            }
            
            self.render_history[render_id] = result
            
            # Store render result
            result_path = os.path.join(self.storage_path, f"{render_id}_result.json")
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            # Store rendered content
            content_path = os.path.join(self.storage_path, f"{render_id}_content.{self._get_extension(component_type)}")
            with open(content_path, 'w') as f:
                f.write(rendered_content)
            
            logger.info(f"Rendered component {component_id} as {render_id}")
            
            # Emit MCP event for component rendering
            if self.agent_core:
                self.agent_core.send_mcp_event(
                    "generative_layer/ui_component/rendered",
                    {
                        "render_id": render_id,
                        "component_id": component_id,
                        "component_name": component["name"]
                    }
                )
            
            return result
        
        except Exception as e:
            logger.error(f"Error rendering component {component_id}: {str(e)}")
            
            # Create failure result
            result = {
                "id": render_id,
                "component_id": component_id,
                "timestamp": timestamp,
                "status": "failed",
                "reason": f"Rendering error: {str(e)}",
                "props": props
            }
            
            self.render_history[render_id] = result
            return result
    
    def get_render_result(self, render_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a render result by ID.
        
        Args:
            render_id: ID of the render result to retrieve
            
        Returns:
            Render result if found, None otherwise
        """
        if render_id not in self.render_history:
            logger.warning(f"Render result {render_id} not found")
            return None
        
        return self.render_history[render_id]
    
    def _render_react_component(self, content: Dict[str, Any], props: Dict[str, Any]) -> str:
        """
        Render a React component.
        
        Args:
            content: Component content
            props: Props to use in rendering
            
        Returns:
            Rendered content
        """
        # Extract component parts
        imports = content.get("imports", "")
        component_name = content.get("componentName", "Component")
        jsx = content.get("jsx", "")
        styles = content.get("styles", "")
        exports = content.get("exports", "")
        
        # Replace prop placeholders in JSX
        for prop_name, prop_value in props.items():
            # Convert prop value to string representation
            if isinstance(prop_value, str):
                value_str = f'"{prop_value}"'
            elif isinstance(prop_value, (bool, int, float)):
                value_str = str(prop_value).lower() if isinstance(prop_value, bool) else str(prop_value)
            elif prop_value is None:
                value_str = "null"
            else:
                # For objects and arrays, use JSON representation
                value_str = json.dumps(prop_value)
            
            # Replace in JSX
            jsx = jsx.replace(f"{{{{{prop_name}}}}}", value_str)
        
        # Assemble component
        component = f"""{imports}

const {component_name} = ({', '.join(props.keys()) if props else ''}) => {{{jsx}
}};

{styles}

{exports}
"""
        
        return component
    
    def _render_vue_component(self, content: Dict[str, Any], props: Dict[str, Any]) -> str:
        """
        Render a Vue component.
        
        Args:
            content: Component content
            props: Props to use in rendering
            
        Returns:
            Rendered content
        """
        # Extract component parts
        template = content.get("template", "")
        script = content.get("script", "")
        style = content.get("style", "")
        
        # Replace prop placeholders in template
        for prop_name, prop_value in props.items():
            # For Vue, we use different syntax based on the type
            if isinstance(prop_value, str):
                template = template.replace(f":{prop_name}", f'{prop_name}="{prop_value}"')
                template = template.replace(f"{{{{ {prop_name} }}}}", prop_value)
            else:
                # For non-string values, keep the binding
                value_str = json.dumps(prop_value)
                template = template.replace(f":{prop_name}=\"{{{{{prop_name}}}}}\"", f":{prop_name}='{value_str}'")
                template = template.replace(f"{{{{ {prop_name} }}}}", value_str)
        
        # Assemble component
        component = f"""<template>
{template}
</template>

<script>
{script}
</script>

<style>
{style}
</style>
"""
        
        return component
    
    def _render_angular_component(self, content: Dict[str, Any], props: Dict[str, Any]) -> str:
        """
        Render an Angular component.
        
        Args:
            content: Component content
            props: Props to use in rendering
            
        Returns:
            Rendered content
        """
        # Extract component parts
        template = content.get("template", "")
        component_class = content.get("componentClass", "")
        styles = content.get("styles", "")
        
        # Replace prop placeholders in template
        for prop_name, prop_value in props.items():
            # For Angular, we use different syntax based on the type
            if isinstance(prop_value, str):
                template = template.replace(f"[{prop_name}]", f'{prop_name}="{prop_value}"')
                template = template.replace(f"{{{{ {prop_name} }}}}", prop_value)
            else:
                # For non-string values, keep the binding
                value_str = json.dumps(prop_value)
                template = template.replace(f"[{prop_name}]=\"{prop_name}\"", f"[{prop_name}]='{value_str}'")
                template = template.replace(f"{{{{ {prop_name} }}}}", value_str)
        
        # Assemble component files
        component_files = {
            "component.ts": component_class,
            "component.html": template,
            "component.css": styles
        }
        
        # Return as JSON string for multiple files
        return json.dumps(component_files, indent=2)
    
    def _render_html_component(self, content: Dict[str, Any], props: Dict[str, Any]) -> str:
        """
        Render an HTML component.
        
        Args:
            content: Component content
            props: Props to use in rendering
            
        Returns:
            Rendered content
        """
        # Extract component parts
        html = content.get("html", "")
        css = content.get("css", "")
        js = content.get("js", "")
        
        # Replace prop placeholders in HTML
        for prop_name, prop_value in props.items():
            if isinstance(prop_value, str):
                html = html.replace(f"{{{{{prop_name}}}}}", prop_value)
            else:
                # For non-string values, use JSON representation
                value_str = json.dumps(prop_value)
                html = html.replace(f"{{{{{prop_name}}}}}", value_str)
        
        # Assemble component
        component = f"""<!DOCTYPE html>
<html>
<head>
    <style>
{css}
    </style>
</head>
<body>
{html}
    <script>
{js}
    </script>
</body>
</html>
"""
        
        return component
    
    def _render_svelte_component(self, content: Dict[str, Any], props: Dict[str, Any]) -> str:
        """
        Render a Svelte component.
        
        Args:
            content: Component content
            props: Props to use in rendering
            
        Returns:
            Rendered content
        """
        # Extract component parts
        script = content.get("script", "")
        template = content.get("template", "")
        style = content.get("style", "")
        
        # Replace prop placeholders in template
        for prop_name, prop_value in props.items():
            if isinstance(prop_value, str):
                template = template.replace(f"{{{{{prop_name}}}}}", prop_value)
            else:
                # For non-string values, use JSON representation
                value_str = json.dumps(prop_value)
                template = template.replace(f"{{{{{prop_name}}}}}", value_str)
        
        # Assemble component
        component = f"""<script>
{script}
</script>

{template}

<style>
{style}
</style>
"""
        
        return component
    
    def _get_extension(self, component_type: str) -> str:
        """
        Get the file extension for a component type.
        
        Args:
            component_type: Component type
            
        Returns:
            File extension
        """
        extensions = {
            "react": "jsx",
            "vue": "vue",
            "angular": "json",  # Multiple files as JSON
            "html": "html",
            "svelte": "svelte"
        }
        
        return extensions.get(component_type, "txt")
    
    def create_component_for_offer(self, 
                                 offer_type: str,
                                 offer_name: str,
                                 offer_description: str) -> Optional[str]:
        """
        Create a UI component for a specific low-ticket offer.
        
        Args:
            offer_type: Type of offer
            offer_name: Name of the offer
            offer_description: Description of the offer
            
        Returns:
            Component ID if successful, None otherwise
        """
        # Generate a unique component ID
        component_id = f"offer_{offer_type}_{uuid.uuid4().hex[:8]}"
        
        # Determine component type and content based on offer type
        component_type = "react"  # Default to React
        props = []
        content = {}
        
        if offer_type == "dashboard":
            component_type = "react"
            content = {
                "imports": "import React, { useState, useEffect } from 'react';\nimport { Card, Chart, Table, Button } from 'your-ui-library';",
                "componentName": "Dashboard",
                "jsx": """
  const [data, setData] = useState({{initialData}});
  
  useEffect(() => {
    // Fetch data or use provided data
    if ({{dataUrl}}) {
      fetch({{dataUrl}})
        .then(response => response.json())
        .then(result => setData(result))
        .catch(error => console.error('Error fetching data:', error));
    }
  }, [{{dataUrl}}]);
  
  return (
    <div className="dashboard">
      <h1>{{title}}</h1>
      <div className="dashboard-description">{{description}}</div>
      
      <div className="dashboard-metrics">
        {data.metrics && data.metrics.map((metric, index) => (
          <Card key={index} title={metric.name} value={metric.value} trend={metric.trend} />
        ))}
      </div>
      
      <div className="dashboard-charts">
        {data.charts && data.charts.map((chart, index) => (
          <Chart 
            key={index}
            type={chart.type}
            data={chart.data}
            options={chart.options}
            title={chart.title}
          />
        ))}
      </div>
      
      {data.tableData && (
        <Table 
          columns={data.tableColumns}
          data={data.tableData}
          pagination={{pageSize: {{pageSize}}}}
          sortable={true}
        />
      )}
      
      <div className="dashboard-actions">
        <Button onClick={{{onRefresh}}}>Refresh Data</Button>
        <Button onClick={{{onExport}}}>Export</Button>
      </div>
    </div>
""",
                "styles": """
.dashboard {
  padding: 20px;
  font-family: {{fontFamily}};
}

.dashboard-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.dashboard-charts {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 30px;
  margin-bottom: 30px;
}

.dashboard-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
""",
                "exports": "export default Dashboard;"
            }
            props = [
                {"name": "title", "type": "string", "description": "Dashboard title", "required": True},
                {"name": "description", "type": "string", "description": "Dashboard description", "required": False},
                {"name": "initialData", "type": "object", "description": "Initial dashboard data", "required": True},
                {"name": "dataUrl", "type": "string", "description": "URL to fetch dashboard data", "required": False},
                {"name": "pageSize", "type": "number", "description": "Table page size", "required": False, "default": 10},
                {"name": "fontFamily", "type": "string", "description": "Font family", "required": False, "default": "Arial, sans-serif"},
                {"name": "onRefresh", "type": "function", "description": "Refresh callback", "required": False},
                {"name": "onExport", "type": "function", "description": "Export callback", "required": False}
            ]
        
        elif offer_type == "form":
            component_type = "react"
            content = {
                "imports": "import React, { useState } from 'react';\nimport { Form, Input, Select, Button, DatePicker } from 'your-ui-library';",
                "componentName": "DynamicForm",
                "jsx": """
  const [formData, setFormData] = useState({{initialValues}} || {});
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when field is edited
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Validate form
    const validationErrors = {};
    {{fields}}.forEach(field => {
      if (field.required && !formData[field.name]) {
        validationErrors[field.name] = `${field.label} is required`;
      }
    });
    
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      setIsSubmitting(false);
      return;
    }
    
    try {
      // Submit form data
      if ({{onSubmit}}) {
        await {{onSubmit}}(formData);
      }
      
      // Reset form if specified
      if ({{resetOnSubmit}}) {
        setFormData({{initialValues}} || {});
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setErrors({ form: 'An error occurred during submission' });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="dynamic-form">
      <h2>{{title}}</h2>
      {{{subtitle}} && <p className="form-subtitle">{{subtitle}}</p>}
      
      {errors.form && <div className="form-error">{errors.form}</div>}
      
      <Form onSubmit={handleSubmit} layout={{layout}}>
        {{{fields}}.map((field) => (
          <Form.Item 
            key={field.name}
            label={field.label}
            error={errors[field.name]}
            required={field.required}
          >
            {field.type === 'text' && (
              <Input
                name={field.name}
                value={formData[field.name] || ''}
                onChange={handleChange}
                placeholder={field.placeholder}
                disabled={field.disabled}
              />
            )}
            
            {field.type === 'select' && (
              <Select
                name={field.name}
                value={formData[field.name] || ''}
                onChange={(value) => setFormData(prev => ({ ...prev, [field.name]: value }))}
                options={field.options}
                placeholder={field.placeholder}
                disabled={field.disabled}
              />
            )}
            
            {field.type === 'date' && (
              <DatePicker
                name={field.name}
                value={formData[field.name] || null}
                onChange={(date) => setFormData(prev => ({ ...prev, [field.name]: date }))}
                placeholder={field.placeholder}
                disabled={field.disabled}
              />
            )}
          </Form.Item>
        ))}
        
        <Form.Item>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={isSubmitting}
            disabled={isSubmitting}
          >
            {{submitButtonText}}
          </Button>
          
          {{{showCancelButton}} && (
            <Button 
              onClick={{{onCancel}}}
              style={{ marginLeft: '10px' }}
            >
              {{cancelButtonText}}
            </Button>
          )}
        </Form.Item>
      </Form>
    </div>
""",
                "styles": """
.dynamic-form {
  max-width: {{maxWidth}}px;
  margin: 0 auto;
  padding: 20px;
}

.form-subtitle {
  margin-bottom: 20px;
  color: #666;
}

.form-error {
  color: #ff4d4f;
  margin-bottom: 16px;
  padding: 8px;
  background-color: #fff1f0;
  border: 1px solid #ffccc7;
  border-radius: 2px;
}
""",
                "exports": "export default DynamicForm;"
            }
            props = [
                {"name": "title", "type": "string", "description": "Form title", "required": True},
                {"name": "subtitle", "type": "string", "description": "Form subtitle", "required": False},
                {"name": "fields", "type": "array", "description": "Form fields configuration", "required": True},
                {"name": "initialValues", "type": "object", "description": "Initial form values", "required": False},
                {"name": "onSubmit", "type": "function", "description": "Form submission handler", "required": True},
                {"name": "resetOnSubmit", "type": "boolean", "description": "Whether to reset form after submission", "required": False, "default": False},
                {"name": "layout", "type": "string", "description": "Form layout (vertical, horizontal)", "required": False, "default": "vertical"},
                {"name": "submitButtonText", "type": "string", "description": "Submit button text", "required": False, "default": "Submit"},
                {"name": "showCancelButton", "type": "boolean", "description": "Whether to show cancel button", "required": False, "default": False},
                {"name": "cancelButtonText", "type": "string", "description": "Cancel button text", "required": False, "default": "Cancel"},
                {"name": "onCancel", "type": "function", "description": "Cancel button handler", "required": False},
                {"name": "maxWidth", "type": "number", "description": "Maximum form width", "required": False, "default": 600}
            ]
        
        elif offer_type == "data_visualization":
            component_type = "react"
            content = {
                "imports": "import React, { useState, useEffect, useRef } from 'react';\nimport { Select, Button, Tooltip } from 'your-ui-library';",
                "componentName": "DataVisualization",
                "jsx": """
  const chartRef = useRef(null);
  const [chartInstance, setChartInstance] = useState(null);
  const [selectedView, setSelectedView] = useState({{defaultView}} || 'chart');
  
  useEffect(() => {
    // Initialize chart library
    if (!chartRef.current) return;
    
    // Clean up previous chart instance
    if (chartInstance) {
      chartInstance.destroy();
    }
    
    // Create new chart based on type
    const ctx = chartRef.current.getContext('2d');
    const newChart = new {{chartLibrary}}.{{chartType}}(ctx, {
      data: {{data}},
      options: {{options}}
    });
    
    setChartInstance(newChart);
    
    return () => {
      if (newChart) {
        newChart.destroy();
      }
    };
  }, [chartRef, {{data}}, {{chartType}}]);
  
  const handleViewChange = (view) => {
    setSelectedView(view);
  };
  
  const handleExport = (format) => {
    if ({{onExport}}) {
      {{onExport}}(format, selectedView);
    }
  };
  
  return (
    <div className="data-visualization">
      <div className="visualization-header">
        <h2>{{title}}</h2>
        
        <div className="visualization-controls">
          <Select
            value={selectedView}
            onChange={handleViewChange}
            options={[
              { value: 'chart', label: 'Chart' },
              { value: 'table', label: 'Table' },
              { value: 'summary', label: 'Summary' }
            ]}
          />
          
          <div className="export-buttons">
            <Tooltip title="Export as PNG">
              <Button icon="download" onClick={() => handleExport('png')} />
            </Tooltip>
            <Tooltip title="Export as CSV">
              <Button icon="file-excel" onClick={() => handleExport('csv')} />
            </Tooltip>
            <Tooltip title="Export as PDF">
              <Button icon="file-pdf" onClick={() => handleExport('pdf')} />
            </Tooltip>
          </div>
        </div>
      </div>
      
      <div className="visualization-content">
        {selectedView === 'chart' && (
          <div className="chart-container" style={{ height: {{height}}px }}>
            <canvas ref={chartRef}></canvas>
          </div>
        )}
        
        {selectedView === 'table' && (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  {{{tableColumns}}.map((column) => (
                    <th key={column.key}>{column.title}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {{{tableData}}.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {{{tableColumns}}.map((column) => (
                      <td key={`${rowIndex}-${column.key}`}>{row[column.key]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {selectedView === 'summary' && (
          <div className="summary-container">
            <div className="summary-stats">
              {{{summaryStats}}.map((stat, index) => (
                <div key={index} className="stat-card">
                  <div className="stat-title">{stat.title}</div>
                  <div className="stat-value">{stat.value}</div>
                  {stat.change && (
                    <div className={`stat-change ${stat.change > 0 ? 'positive' : 'negative'}`}>
                      {stat.change > 0 ? '+' : ''}{stat.change}%
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            <div className="summary-description">
              {{summaryDescription}}
            </div>
          </div>
        )}
      </div>
    </div>
""",
                "styles": """
.data-visualization {
  font-family: {{fontFamily}};
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.visualization-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.visualization-controls {
  display: flex;
  gap: 10px;
}

.export-buttons {
  display: flex;
  gap: 5px;
}

.chart-container {
  position: relative;
  width: 100%;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #e8e8e8;
  text-align: left;
}

.data-table th {
  background-color: #fafafa;
  font-weight: 500;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 5px;
}

.stat-change {
  font-size: 14px;
}

.stat-change.positive {
  color: #52c41a;
}

.stat-change.negative {
  color: #f5222d;
}

.summary-description {
  line-height: 1.6;
}
""",
                "exports": "export default DataVisualization;"
            }
            props = [
                {"name": "title", "type": "string", "description": "Visualization title", "required": True},
                {"name": "data", "type": "object", "description": "Chart data", "required": True},
                {"name": "chartType", "type": "string", "description": "Chart type (e.g., 'Bar', 'Line', 'Pie')", "required": True},
                {"name": "chartLibrary", "type": "string", "description": "Chart library to use", "required": False, "default": "Chart"},
                {"name": "options", "type": "object", "description": "Chart options", "required": False},
                {"name": "height", "type": "number", "description": "Chart height", "required": False, "default": 400},
                {"name": "defaultView", "type": "string", "description": "Default view (chart, table, summary)", "required": False, "default": "chart"},
                {"name": "tableColumns", "type": "array", "description": "Table columns configuration", "required": False},
                {"name": "tableData", "type": "array", "description": "Table data", "required": False},
                {"name": "summaryStats", "type": "array", "description": "Summary statistics", "required": False},
                {"name": "summaryDescription", "type": "string", "description": "Summary description", "required": False},
                {"name": "onExport", "type": "function", "description": "Export handler", "required": False},
                {"name": "fontFamily", "type": "string", "description": "Font family", "required": False, "default": "Arial, sans-serif"}
            ]
        
        else:
            # Generic component
            component_type = "react"
            content = {
                "imports": "import React from 'react';",
                "componentName": "GenericComponent",
                "jsx": """
  return (
    <div className="generic-component">
      <h2>{{title}}</h2>
      <div className="content">
        {{content}}
      </div>
      {{{showButton}} && (
        <button 
          className="action-button"
          onClick={{{onButtonClick}}}
        >
          {{buttonText}}
        </button>
      )}
    </div>
""",
                "styles": """
.generic-component {
  padding: 20px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  background-color: #fff;
}

.content {
  margin: 20px 0;
}

.action-button {
  padding: 8px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.action-button:hover {
  background-color: #40a9ff;
}
""",
                "exports": "export default GenericComponent;"
            }
            props = [
                {"name": "title", "type": "string", "description": "Component title", "required": True},
                {"name": "content", "type": "string", "description": "Component content", "required": True},
                {"name": "showButton", "type": "boolean", "description": "Whether to show action button", "required": False, "default": False},
                {"name": "buttonText", "type": "string", "description": "Button text", "required": False, "default": "Click Me"},
                {"name": "onButtonClick", "type": "function", "description": "Button click handler", "required": False}
            ]
        
        # Register component
        success = self.register_component(
            component_id=component_id,
            name=offer_name,
            description=offer_description,
            component_type=component_type,
            content=content,
            props=props,
            category=offer_type,
            metadata={
                "offer_type": offer_type,
                "generated": True,
                "timestamp": time.time()
            }
        )
        
        if success:
            return component_id
        else:
            return None
    
    def export_component_data(self) -> Dict[str, Any]:
        """
        Export component data for persistence.
        
        Returns:
            Component data
        """
        return {
            "components": self.components,
            "component_categories": self.component_categories
        }
    
    def import_component_data(self, component_data: Dict[str, Any]) -> None:
        """
        Import component data from persistence.
        
        Args:
            component_data: Component data to import
        """
        if "components" in component_data:
            self.components = component_data["components"]
        
        if "component_categories" in component_data:
            self.component_categories = component_data["component_categories"]
        
        logger.info("Imported component data")
