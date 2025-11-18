"""
AWS Provider Integration

This module provides integration with AWS cloud services for the Deployment Operations Layer.
It handles AWS-specific deployment operations, resource management, and service interactions.

Classes:
    AWSProviderAdapter: Adapter for AWS cloud services integration
    AWSResourceManager: Manages AWS resources for deployments
    AWSDeploymentHandler: Handles deployment operations on AWS
"""

import boto3
import json
import logging
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError

from ..agent.agent_utils import AgentResponse
from ..protocol.mcp_integration.mcp_context_schema import MCPContext

logger = logging.getLogger(__name__)

class AWSProviderAdapter:
    """
    Adapter for AWS cloud services integration.
    
    This class provides a standardized interface for interacting with AWS services
    within the Deployment Operations Layer.
    """
    
    def __init__(self, region: str = "us-east-1", profile: Optional[str] = None):
        """
        Initialize the AWS Provider Adapter.
        
        Args:
            region: AWS region to use for operations
            profile: AWS profile to use for credentials (optional)
        """
        self.region = region
        self.profile = profile
        self.session = self._create_session()
        self.resource_manager = AWSResourceManager(self.session)
        self.deployment_handler = AWSDeploymentHandler(self.session)
        
    def _create_session(self) -> boto3.Session:
        """
        Create an AWS session using the specified profile and region.
        
        Returns:
            boto3.Session: Configured AWS session
        """
        if self.profile:
            return boto3.Session(profile_name=self.profile, region_name=self.region)
        return boto3.Session(region_name=self.region)
    
    def validate_credentials(self) -> bool:
        """
        Validate AWS credentials.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            sts = self.session.client('sts')
            sts.get_caller_identity()
            return True
        except ClientError as e:
            logger.error(f"AWS credentials validation failed: {str(e)}")
            return False
    
    def get_available_services(self) -> List[str]:
        """
        Get list of available AWS services in the current region.
        
        Returns:
            List[str]: List of available service names
        """
        return self.session.get_available_services()
    
    def create_deployment_context(self, mission_id: str) -> Dict[str, Any]:
        """
        Create AWS-specific deployment context for a mission.
        
        Args:
            mission_id: Unique identifier for the mission
            
        Returns:
            Dict[str, Any]: AWS deployment context
        """
        return {
            "provider": "aws",
            "region": self.region,
            "mission_id": mission_id,
            "services": self.get_available_services(),
            "account_id": self._get_account_id()
        }
    
    def _get_account_id(self) -> str:
        """
        Get the current AWS account ID.
        
        Returns:
            str: AWS account ID
        """
        sts = self.session.client('sts')
        return sts.get_caller_identity()["Account"]
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert AWS provider information to MCP context.
        
        Returns:
            MCPContext: MCP context with AWS provider information
        """
        return MCPContext(
            context_type="cloud_provider",
            provider="aws",
            region=self.region,
            account_id=self._get_account_id(),
            services=self.get_available_services()
        )


class AWSResourceManager:
    """
    Manages AWS resources for deployments.
    
    This class handles resource provisioning, monitoring, and cleanup for
    AWS-based deployments.
    """
    
    def __init__(self, session: boto3.Session):
        """
        Initialize the AWS Resource Manager.
        
        Args:
            session: Configured AWS session
        """
        self.session = session
        
    def provision_resources(self, resource_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision AWS resources based on specifications.
        
        Args:
            resource_specs: Resource specifications
            
        Returns:
            Dict[str, Any]: Provisioned resource details
        """
        resources = {}
        
        # Process each resource type
        for resource_type, specs in resource_specs.items():
            if resource_type == "ec2":
                resources["ec2"] = self._provision_ec2(specs)
            elif resource_type == "s3":
                resources["s3"] = self._provision_s3(specs)
            elif resource_type == "lambda":
                resources["lambda"] = self._provision_lambda(specs)
            elif resource_type == "ecs":
                resources["ecs"] = self._provision_ecs(specs)
            elif resource_type == "eks":
                resources["eks"] = self._provision_eks(specs)
                
        return resources
    
    def _provision_ec2(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision EC2 instances.
        
        Args:
            specs: EC2 specifications
            
        Returns:
            Dict[str, Any]: EC2 resource details
        """
        ec2 = self.session.resource('ec2')
        instances = []
        
        try:
            for instance_spec in specs.get("instances", []):
                instance = ec2.create_instances(
                    ImageId=instance_spec.get("image_id"),
                    InstanceType=instance_spec.get("instance_type", "t2.micro"),
                    MinCount=instance_spec.get("min_count", 1),
                    MaxCount=instance_spec.get("max_count", 1),
                    KeyName=instance_spec.get("key_name"),
                    SecurityGroupIds=instance_spec.get("security_group_ids", []),
                    SubnetId=instance_spec.get("subnet_id"),
                    UserData=instance_spec.get("user_data"),
                    TagSpecifications=instance_spec.get("tag_specifications", [])
                )
                
                instances.extend([{
                    "id": i.id,
                    "type": i.instance_type,
                    "state": i.state["Name"],
                    "private_ip": i.private_ip_address,
                    "public_ip": i.public_ip_address
                } for i in instance])
                
            return {"instances": instances}
        
        except ClientError as e:
            logger.error(f"Failed to provision EC2 instances: {str(e)}")
            return {"error": str(e)}
    
    def _provision_s3(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision S3 buckets.
        
        Args:
            specs: S3 specifications
            
        Returns:
            Dict[str, Any]: S3 resource details
        """
        s3 = self.session.resource('s3')
        buckets = []
        
        try:
            for bucket_spec in specs.get("buckets", []):
                bucket = s3.create_bucket(
                    Bucket=bucket_spec.get("name"),
                    CreateBucketConfiguration={
                        'LocationConstraint': bucket_spec.get("region", self.session.region_name)
                    }
                )
                
                buckets.append({
                    "name": bucket.name,
                    "creation_date": bucket.creation_date,
                    "url": f"s3://{bucket.name}"
                })
                
            return {"buckets": buckets}
        
        except ClientError as e:
            logger.error(f"Failed to provision S3 buckets: {str(e)}")
            return {"error": str(e)}
    
    def _provision_lambda(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision Lambda functions.
        
        Args:
            specs: Lambda specifications
            
        Returns:
            Dict[str, Any]: Lambda resource details
        """
        lambda_client = self.session.client('lambda')
        functions = []
        
        try:
            for function_spec in specs.get("functions", []):
                response = lambda_client.create_function(
                    FunctionName=function_spec.get("name"),
                    Runtime=function_spec.get("runtime", "python3.9"),
                    Role=function_spec.get("role"),
                    Handler=function_spec.get("handler"),
                    Code=function_spec.get("code"),
                    Description=function_spec.get("description", ""),
                    Timeout=function_spec.get("timeout", 3),
                    MemorySize=function_spec.get("memory_size", 128),
                    Environment=function_spec.get("environment", {})
                )
                
                functions.append({
                    "name": response["FunctionName"],
                    "arn": response["FunctionArn"],
                    "runtime": response["Runtime"],
                    "handler": response["Handler"]
                })
                
            return {"functions": functions}
        
        except ClientError as e:
            logger.error(f"Failed to provision Lambda functions: {str(e)}")
            return {"error": str(e)}
    
    def _provision_ecs(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision ECS clusters and services.
        
        Args:
            specs: ECS specifications
            
        Returns:
            Dict[str, Any]: ECS resource details
        """
        ecs = self.session.client('ecs')
        clusters = []
        
        try:
            for cluster_spec in specs.get("clusters", []):
                cluster_response = ecs.create_cluster(
                    clusterName=cluster_spec.get("name"),
                    tags=cluster_spec.get("tags", [])
                )
                
                cluster = {
                    "name": cluster_response["cluster"]["clusterName"],
                    "arn": cluster_response["cluster"]["clusterArn"],
                    "services": []
                }
                
                # Create services in the cluster
                for service_spec in cluster_spec.get("services", []):
                    service_response = ecs.create_service(
                        cluster=cluster["name"],
                        serviceName=service_spec.get("name"),
                        taskDefinition=service_spec.get("task_definition"),
                        desiredCount=service_spec.get("desired_count", 1),
                        launchType=service_spec.get("launch_type", "FARGATE"),
                        networkConfiguration=service_spec.get("network_configuration", {})
                    )
                    
                    cluster["services"].append({
                        "name": service_response["service"]["serviceName"],
                        "arn": service_response["service"]["serviceArn"]
                    })
                
                clusters.append(cluster)
                
            return {"clusters": clusters}
        
        except ClientError as e:
            logger.error(f"Failed to provision ECS resources: {str(e)}")
            return {"error": str(e)}
    
    def _provision_eks(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision EKS clusters.
        
        Args:
            specs: EKS specifications
            
        Returns:
            Dict[str, Any]: EKS resource details
        """
        eks = self.session.client('eks')
        clusters = []
        
        try:
            for cluster_spec in specs.get("clusters", []):
                response = eks.create_cluster(
                    name=cluster_spec.get("name"),
                    roleArn=cluster_spec.get("role_arn"),
                    resourcesVpcConfig=cluster_spec.get("vpc_config"),
                    version=cluster_spec.get("version", "1.21")
                )
                
                clusters.append({
                    "name": response["cluster"]["name"],
                    "arn": response["cluster"]["arn"],
                    "status": response["cluster"]["status"],
                    "endpoint": response["cluster"].get("endpoint"),
                    "version": response["cluster"]["version"]
                })
                
            return {"clusters": clusters}
        
        except ClientError as e:
            logger.error(f"Failed to provision EKS clusters: {str(e)}")
            return {"error": str(e)}
    
    def cleanup_resources(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up provisioned AWS resources.
        
        Args:
            resources: Resource details to clean up
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        results = {}
        
        # Clean up EC2 instances
        if "ec2" in resources:
            results["ec2"] = self._cleanup_ec2(resources["ec2"])
            
        # Clean up S3 buckets
        if "s3" in resources:
            results["s3"] = self._cleanup_s3(resources["s3"])
            
        # Clean up Lambda functions
        if "lambda" in resources:
            results["lambda"] = self._cleanup_lambda(resources["lambda"])
            
        # Clean up ECS resources
        if "ecs" in resources:
            results["ecs"] = self._cleanup_ecs(resources["ecs"])
            
        # Clean up EKS clusters
        if "eks" in resources:
            results["eks"] = self._cleanup_eks(resources["eks"])
            
        return results
    
    def _cleanup_ec2(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up EC2 resources.
        
        Args:
            resources: EC2 resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        ec2 = self.session.resource('ec2')
        results = {"success": [], "failed": []}
        
        try:
            for instance in resources.get("instances", []):
                instance_id = instance["id"]
                ec2_instance = ec2.Instance(instance_id)
                ec2_instance.terminate()
                results["success"].append(instance_id)
                
            return results
        
        except ClientError as e:
            logger.error(f"Failed to clean up EC2 instances: {str(e)}")
            results["failed"].append({"id": instance_id, "error": str(e)})
            return results
    
    def _cleanup_s3(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up S3 resources.
        
        Args:
            resources: S3 resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        s3 = self.session.resource('s3')
        results = {"success": [], "failed": []}
        
        try:
            for bucket in resources.get("buckets", []):
                bucket_name = bucket["name"]
                s3_bucket = s3.Bucket(bucket_name)
                
                # Delete all objects in the bucket first
                s3_bucket.objects.all().delete()
                
                # Then delete the bucket
                s3_bucket.delete()
                results["success"].append(bucket_name)
                
            return results
        
        except ClientError as e:
            logger.error(f"Failed to clean up S3 buckets: {str(e)}")
            results["failed"].append({"name": bucket_name, "error": str(e)})
            return results
    
    def _cleanup_lambda(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up Lambda resources.
        
        Args:
            resources: Lambda resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        lambda_client = self.session.client('lambda')
        results = {"success": [], "failed": []}
        
        try:
            for function in resources.get("functions", []):
                function_name = function["name"]
                lambda_client.delete_function(FunctionName=function_name)
                results["success"].append(function_name)
                
            return results
        
        except ClientError as e:
            logger.error(f"Failed to clean up Lambda functions: {str(e)}")
            results["failed"].append({"name": function_name, "error": str(e)})
            return results
    
    def _cleanup_ecs(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up ECS resources.
        
        Args:
            resources: ECS resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        ecs = self.session.client('ecs')
        results = {"success": [], "failed": []}
        
        try:
            for cluster in resources.get("clusters", []):
                cluster_name = cluster["name"]
                
                # Delete all services in the cluster first
                for service in cluster.get("services", []):
                    service_name = service["name"]
                    ecs.update_service(
                        cluster=cluster_name,
                        service=service_name,
                        desiredCount=0
                    )
                    ecs.delete_service(
                        cluster=cluster_name,
                        service=service_name,
                        force=True
                    )
                
                # Then delete the cluster
                ecs.delete_cluster(cluster=cluster_name)
                results["success"].append(cluster_name)
                
            return results
        
        except ClientError as e:
            logger.error(f"Failed to clean up ECS resources: {str(e)}")
            results["failed"].append({"name": cluster_name, "error": str(e)})
            return results
    
    def _cleanup_eks(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up EKS resources.
        
        Args:
            resources: EKS resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        eks = self.session.client('eks')
        results = {"success": [], "failed": []}
        
        try:
            for cluster in resources.get("clusters", []):
                cluster_name = cluster["name"]
                eks.delete_cluster(name=cluster_name)
                results["success"].append(cluster_name)
                
            return results
        
        except ClientError as e:
            logger.error(f"Failed to clean up EKS clusters: {str(e)}")
            results["failed"].append({"name": cluster_name, "error": str(e)})
            return results


class AWSDeploymentHandler:
    """
    Handles deployment operations on AWS.
    
    This class manages the deployment of applications and services to AWS.
    """
    
    def __init__(self, session: boto3.Session):
        """
        Initialize the AWS Deployment Handler.
        
        Args:
            session: Configured AWS session
        """
        self.session = session
        
    def deploy_application(self, deployment_spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy an application to AWS.
        
        Args:
            deployment_spec: Deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        deployment_type = deployment_spec.get("type", "")
        
        if deployment_type == "lambda":
            return self._deploy_lambda_application(deployment_spec)
        elif deployment_type == "ecs":
            return self._deploy_ecs_application(deployment_spec)
        elif deployment_type == "eks":
            return self._deploy_eks_application(deployment_spec)
        elif deployment_type == "ec2":
            return self._deploy_ec2_application(deployment_spec)
        elif deployment_type == "cloudformation":
            return self._deploy_cloudformation_stack(deployment_spec)
        else:
            return AgentResponse(
                success=False,
                message=f"Unsupported deployment type: {deployment_type}",
                data={}
            )
    
    def _deploy_lambda_application(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy a Lambda application.
        
        Args:
            spec: Lambda deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        lambda_client = self.session.client('lambda')
        
        try:
            # Create or update the Lambda function
            function_name = spec.get("function_name")
            
            # Check if function exists
            try:
                lambda_client.get_function(FunctionName=function_name)
                # Update existing function
                response = lambda_client.update_function_code(
                    FunctionName=function_name,
                    S3Bucket=spec.get("code", {}).get("s3_bucket"),
                    S3Key=spec.get("code", {}).get("s3_key"),
                    Publish=True
                )
            except ClientError:
                # Create new function
                response = lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime=spec.get("runtime", "python3.9"),
                    Role=spec.get("role"),
                    Handler=spec.get("handler"),
                    Code={
                        'S3Bucket': spec.get("code", {}).get("s3_bucket"),
                        'S3Key': spec.get("code", {}).get("s3_key")
                    },
                    Description=spec.get("description", ""),
                    Timeout=spec.get("timeout", 3),
                    MemorySize=spec.get("memory_size", 128),
                    Environment={
                        'Variables': spec.get("environment", {})
                    }
                )
            
            # Configure function concurrency if specified
            if "concurrency" in spec:
                lambda_client.put_function_concurrency(
                    FunctionName=function_name,
                    ReservedConcurrentExecutions=spec["concurrency"]
                )
            
            # Add event source mappings if specified
            if "event_sources" in spec:
                for event_source in spec["event_sources"]:
                    lambda_client.create_event_source_mapping(
                        FunctionName=function_name,
                        EventSourceArn=event_source.get("arn"),
                        Enabled=event_source.get("enabled", True),
                        BatchSize=event_source.get("batch_size", 10)
                    )
            
            return AgentResponse(
                success=True,
                message=f"Successfully deployed Lambda function: {function_name}",
                data={
                    "function_name": response["FunctionName"],
                    "function_arn": response["FunctionArn"],
                    "runtime": response["Runtime"],
                    "handler": response["Handler"],
                    "last_modified": response["LastModified"]
                }
            )
        
        except ClientError as e:
            logger.error(f"Failed to deploy Lambda application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Lambda application: {str(e)}",
                data={}
            )
    
    def _deploy_ecs_application(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy an ECS application.
        
        Args:
            spec: ECS deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        ecs = self.session.client('ecs')
        
        try:
            cluster_name = spec.get("cluster")
            service_name = spec.get("service_name")
            task_definition = spec.get("task_definition")
            
            # Register task definition
            task_def_response = ecs.register_task_definition(
                family=task_definition.get("family"),
                executionRoleArn=task_definition.get("execution_role_arn"),
                taskRoleArn=task_definition.get("task_role_arn"),
                networkMode=task_definition.get("network_mode", "awsvpc"),
                containerDefinitions=task_definition.get("container_definitions"),
                volumes=task_definition.get("volumes", []),
                placementConstraints=task_definition.get("placement_constraints", []),
                requiresCompatibilities=task_definition.get("requires_compatibilities", ["FARGATE"]),
                cpu=task_definition.get("cpu"),
                memory=task_definition.get("memory")
            )
            
            task_def_arn = task_def_response["taskDefinition"]["taskDefinitionArn"]
            
            # Check if service exists
            try:
                ecs.describe_services(
                    cluster=cluster_name,
                    services=[service_name]
                )
                
                # Update existing service
                service_response = ecs.update_service(
                    cluster=cluster_name,
                    service=service_name,
                    taskDefinition=task_def_arn,
                    desiredCount=spec.get("desired_count", 1),
                    forceNewDeployment=spec.get("force_new_deployment", True)
                )
            except self.ecs_client.exceptions.ServiceNotFoundException:
                # ServiceNotFoundException: service doesn't exist, create new one
                # Create new service
                service_response = ecs.create_service(
                    cluster=cluster_name,
                    serviceName=service_name,
                    taskDefinition=task_def_arn,
                    desiredCount=spec.get("desired_count", 1),
                    launchType=spec.get("launch_type", "FARGATE"),
                    networkConfiguration=spec.get("network_configuration"),
                    loadBalancers=spec.get("load_balancers", [])
                )
            
            return AgentResponse(
                success=True,
                message=f"Successfully deployed ECS service: {service_name} to cluster: {cluster_name}",
                data={
                    "cluster": cluster_name,
                    "service_name": service_response["service"]["serviceName"],
                    "service_arn": service_response["service"]["serviceArn"],
                    "task_definition": task_def_arn,
                    "desired_count": service_response["service"]["desiredCount"],
                    "running_count": service_response["service"]["runningCount"]
                }
            )
        
        except ClientError as e:
            logger.error(f"Failed to deploy ECS application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy ECS application: {str(e)}",
                data={}
            )
    
    def _deploy_eks_application(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy an application to EKS.
        
        Args:
            spec: EKS deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        # For EKS deployments, we use kubectl commands through subprocess
        # This is a simplified implementation
        import subprocess
        import tempfile
        import os
        
        try:
            cluster_name = spec.get("cluster")
            namespace = spec.get("namespace", "default")
            manifests = spec.get("manifests", [])
            
            # Update kubeconfig for the cluster
            eks = self.session.client('eks')
            cluster_info = eks.describe_cluster(name=cluster_name)
            
            # Create a temporary directory for manifests
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write manifests to files
                manifest_files = []
                for i, manifest in enumerate(manifests):
                    file_path = os.path.join(temp_dir, f"manifest_{i}.yaml")
                    with open(file_path, "w") as f:
                        f.write(manifest)
                    manifest_files.append(file_path)
                
                # Update kubeconfig
                update_cmd = [
                    "aws", "eks", "update-kubeconfig",
                    "--name", cluster_name,
                    "--region", self.session.region_name
                ]
                
                subprocess.run(update_cmd, check=True)
                
                # Apply manifests
                results = []
                for file_path in manifest_files:
                    apply_cmd = [
                        "kubectl", "apply",
                        "-f", file_path,
                        "-n", namespace
                    ]
                    
                    result = subprocess.run(
                        apply_cmd,
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    
                    results.append({
                        "file": os.path.basename(file_path),
                        "output": result.stdout
                    })
            
            return AgentResponse(
                success=True,
                message=f"Successfully deployed application to EKS cluster: {cluster_name}, namespace: {namespace}",
                data={
                    "cluster": cluster_name,
                    "namespace": namespace,
                    "results": results
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy EKS application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy EKS application: {str(e)}",
                data={}
            )
    
    def _deploy_ec2_application(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy an application to EC2 instances.
        
        Args:
            spec: EC2 deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        ssm = self.session.client('ssm')
        
        try:
            instance_ids = spec.get("instance_ids", [])
            deployment_type = spec.get("deployment_method", "ssm")
            
            if deployment_type == "ssm":
                # Use SSM Run Command for deployment
                document_name = spec.get("document_name", "AWS-RunShellScript")
                commands = spec.get("commands", [])
                
                response = ssm.send_command(
                    InstanceIds=instance_ids,
                    DocumentName=document_name,
                    Parameters={
                        'commands': commands
                    },
                    Comment=spec.get("comment", "Deployment by Deployment Ops Layer")
                )
                
                command_id = response["Command"]["CommandId"]
                
                # Wait for command completion
                import time
                completed = False
                max_retries = 30
                retries = 0
                
                while not completed and retries < max_retries:
                    time.sleep(5)
                    result = ssm.list_command_invocations(
                        CommandId=command_id,
                        Details=True
                    )
                    
                    invocations = result["CommandInvocations"]
                    all_completed = all(inv["Status"] in ["Success", "Failed", "Cancelled", "TimedOut"] for inv in invocations)
                    
                    if all_completed:
                        completed = True
                    
                    retries += 1
                
                # Get final status
                final_result = ssm.list_command_invocations(
                    CommandId=command_id,
                    Details=True
                )
                
                return AgentResponse(
                    success=True,
                    message=f"Deployment to EC2 instances completed",
                    data={
                        "command_id": command_id,
                        "instances": [
                            {
                                "instance_id": inv["InstanceId"],
                                "status": inv["Status"],
                                "output": inv.get("CommandPlugins", [{}])[0].get("Output", "")
                            }
                            for inv in final_result["CommandInvocations"]
                        ]
                    }
                )
            else:
                return AgentResponse(
                    success=False,
                    message=f"Unsupported EC2 deployment method: {deployment_type}",
                    data={}
                )
        
        except ClientError as e:
            logger.error(f"Failed to deploy EC2 application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy EC2 application: {str(e)}",
                data={}
            )
    
    def _deploy_cloudformation_stack(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy a CloudFormation stack.
        
        Args:
            spec: CloudFormation deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        cfn = self.session.client('cloudformation')
        
        try:
            stack_name = spec.get("stack_name")
            template_body = spec.get("template_body")
            template_url = spec.get("template_url")
            parameters = spec.get("parameters", [])
            capabilities = spec.get("capabilities", [])
            
            # Check if stack exists
            try:
                cfn.describe_stacks(StackName=stack_name)
                
                # Update existing stack
                if template_body:
                    response = cfn.update_stack(
                        StackName=stack_name,
                        TemplateBody=template_body,
                        Parameters=parameters,
                        Capabilities=capabilities
                    )
                else:
                    response = cfn.update_stack(
                        StackName=stack_name,
                        TemplateURL=template_url,
                        Parameters=parameters,
                        Capabilities=capabilities
                    )
                
                operation = "update"
            except self.cf_client.exceptions.ClientError as e:
                # ClientError: stack doesn't exist or can't be updated
                if 'does not exist' in str(e):
                    # Create new stack
                if template_body:
                    response = cfn.create_stack(
                        StackName=stack_name,
                        TemplateBody=template_body,
                        Parameters=parameters,
                        Capabilities=capabilities,
                        OnFailure=spec.get("on_failure", "ROLLBACK")
                    )
                else:
                    response = cfn.create_stack(
                        StackName=stack_name,
                        TemplateURL=template_url,
                        Parameters=parameters,
                        Capabilities=capabilities,
                        OnFailure=spec.get("on_failure", "ROLLBACK")
                    )
                
                operation = "create"
            
            stack_id = response["StackId"]
            
            # Wait for stack operation to complete
            waiter = cfn.get_waiter(f'stack_{operation}_complete')
            waiter.wait(StackName=stack_id)
            
            # Get stack outputs
            stack_info = cfn.describe_stacks(StackName=stack_id)
            outputs = stack_info["Stacks"][0].get("Outputs", [])
            
            return AgentResponse(
                success=True,
                message=f"Successfully deployed CloudFormation stack: {stack_name}",
                data={
                    "stack_name": stack_name,
                    "stack_id": stack_id,
                    "operation": operation,
                    "outputs": {
                        output["OutputKey"]: output["OutputValue"]
                        for output in outputs
                    }
                }
            )
        
        except ClientError as e:
            logger.error(f"Failed to deploy CloudFormation stack: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy CloudFormation stack: {str(e)}",
                data={}
            )
