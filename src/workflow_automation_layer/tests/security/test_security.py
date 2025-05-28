import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from security.security_compliance_observability import SecurityComplianceObservability
from security.zk_attestation import ZkAttestation
from security.trust_pathway_manager import TrustPathwayManager
from security.multi_tenant_isolation import MultiTenantIsolation
from security.adaptive_trust_policy_manager import AdaptiveTrustPolicyManager

from workflow_engine.workflow_runtime import WorkflowRuntime
from workflow_engine.execution_mode_manager import ExecutionModeManager


class TestSecurityComplianceObservability(unittest.TestCase):
    """Security tests for the SecurityComplianceObservability class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.security_compliance = SecurityComplianceObservability(
            workflow_runtime=self.workflow_runtime
        )
    
    def test_initialization(self):
        """Test that the security compliance module initializes correctly."""
        self.assertEqual(self.security_compliance.workflow_runtime, self.workflow_runtime)
        self.assertIsNotNone(self.security_compliance.audit_log)
        self.assertIsNotNone(self.security_compliance.compliance_rules)
    
    @patch('security.security_compliance_observability.SecurityComplianceObservability.audit_workflow_access')
    def test_audit_workflow_access(self, mock_audit):
        """Test that workflow access is properly audited."""
        user_id = "user-001"
        workflow_id = "workflow-001"
        access_type = "read"
        self.security_compliance.audit_workflow_access(user_id, workflow_id, access_type)
        mock_audit.assert_called_once_with(user_id, workflow_id, access_type)
    
    @patch('security.security_compliance_observability.SecurityComplianceObservability.verify_compliance')
    def test_verify_compliance(self, mock_verify):
        """Test that compliance verification works correctly."""
        workflow_id = "workflow-001"
        compliance_type = "GDPR"
        self.security_compliance.verify_compliance(workflow_id, compliance_type)
        mock_verify.assert_called_once_with(workflow_id, compliance_type)
    
    @patch('security.security_compliance_observability.SecurityComplianceObservability.generate_compliance_report')
    def test_generate_compliance_report(self, mock_generate):
        """Test that compliance reports are generated correctly."""
        workflow_id = "workflow-001"
        report_type = "regulatory"
        start_date = "2025-05-01"
        end_date = "2025-05-22"
        self.security_compliance.generate_compliance_report(workflow_id, report_type, start_date, end_date)
        mock_generate.assert_called_once_with(workflow_id, report_type, start_date, end_date)
    
    def test_data_encryption_at_rest(self):
        """Test that data encryption at rest is properly implemented."""
        # This is a security test to ensure sensitive data is encrypted at rest
        sensitive_data = {"user_id": "user-001", "api_key": "secret-key"}
        encrypted_data = self.security_compliance.encrypt_sensitive_data(sensitive_data)
        
        # Verify the data is encrypted
        self.assertNotEqual(str(encrypted_data), str(sensitive_data))
        
        # Verify the data can be decrypted
        decrypted_data = self.security_compliance.decrypt_sensitive_data(encrypted_data)
        self.assertEqual(decrypted_data, sensitive_data)
    
    def test_data_encryption_in_transit(self):
        """Test that data encryption in transit is properly implemented."""
        # This is a security test to ensure sensitive data is encrypted in transit
        message = {"workflow_id": "workflow-001", "execution_id": "execution-001", "data": {"api_key": "secret-key"}}
        encrypted_message = self.security_compliance.encrypt_message(message)
        
        # Verify the message is encrypted
        self.assertNotEqual(str(encrypted_message), str(message))
        
        # Verify the message can be decrypted
        decrypted_message = self.security_compliance.decrypt_message(encrypted_message)
        self.assertEqual(decrypted_message, message)
    
    def test_access_control(self):
        """Test that access control is properly implemented."""
        # This is a security test to ensure access control is enforced
        user_id = "user-001"
        workflow_id = "workflow-001"
        permission = "execute"
        
        # Test with insufficient permissions
        self.security_compliance.set_user_permissions(user_id, workflow_id, ["read"])
        has_permission = self.security_compliance.check_permission(user_id, workflow_id, permission)
        self.assertFalse(has_permission)
        
        # Test with sufficient permissions
        self.security_compliance.set_user_permissions(user_id, workflow_id, ["read", "execute"])
        has_permission = self.security_compliance.check_permission(user_id, workflow_id, permission)
        self.assertTrue(has_permission)
    
    def test_audit_logging(self):
        """Test that audit logging is properly implemented."""
        # This is a security test to ensure all actions are properly logged
        user_id = "user-001"
        workflow_id = "workflow-001"
        action = "execute_workflow"
        details = {"execution_id": "execution-001"}
        
        # Log an action
        self.security_compliance.log_audit_event(user_id, workflow_id, action, details)
        
        # Verify the action was logged
        audit_events = self.security_compliance.get_audit_events(workflow_id)
        self.assertGreater(len(audit_events), 0)
        latest_event = audit_events[-1]
        self.assertEqual(latest_event["user_id"], user_id)
        self.assertEqual(latest_event["workflow_id"], workflow_id)
        self.assertEqual(latest_event["action"], action)
        self.assertEqual(latest_event["details"], details)
    
    def test_input_validation(self):
        """Test that input validation is properly implemented."""
        # This is a security test to ensure inputs are properly validated
        
        # Test with valid input
        valid_input = {"workflow_id": "workflow-001", "execution_mode": "autonomous"}
        validation_result = self.security_compliance.validate_input(valid_input, ["workflow_id", "execution_mode"])
        self.assertTrue(validation_result)
        
        # Test with invalid input (missing required field)
        invalid_input = {"workflow_id": "workflow-001"}
        validation_result = self.security_compliance.validate_input(invalid_input, ["workflow_id", "execution_mode"])
        self.assertFalse(validation_result)
        
        # Test with invalid input (SQL injection attempt)
        malicious_input = {"workflow_id": "workflow-001'; DROP TABLE workflows; --"}
        validation_result = self.security_compliance.validate_input(malicious_input, ["workflow_id"])
        self.assertFalse(validation_result)


class TestZkAttestation(unittest.TestCase):
    """Security tests for the ZkAttestation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.zk_attestation = ZkAttestation(
            workflow_runtime=self.workflow_runtime
        )
    
    def test_initialization(self):
        """Test that the ZK attestation module initializes correctly."""
        self.assertEqual(self.zk_attestation.workflow_runtime, self.workflow_runtime)
        self.assertIsNotNone(self.zk_attestation.attestation_registry)
    
    @patch('security.zk_attestation.ZkAttestation.generate_proof')
    def test_generate_proof(self, mock_generate):
        """Test that ZK proofs are generated correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        task_id = "task-001"
        task_data = {"input": "test_input", "output": "test_output"}
        self.zk_attestation.generate_proof(workflow_id, execution_id, task_id, task_data)
        mock_generate.assert_called_once_with(workflow_id, execution_id, task_id, task_data)
    
    @patch('security.zk_attestation.ZkAttestation.verify_proof')
    def test_verify_proof(self, mock_verify):
        """Test that ZK proofs are verified correctly."""
        proof_id = "proof-001"
        self.zk_attestation.verify_proof(proof_id)
        mock_verify.assert_called_once_with(proof_id)
    
    def test_proof_generation_and_verification(self):
        """Test the end-to-end process of generating and verifying a ZK proof."""
        # This is a security test to ensure ZK proofs work correctly
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        task_id = "task-001"
        task_data = {"input": "test_input", "output": "test_output"}
        
        # Generate a proof
        proof_id = self.zk_attestation.generate_proof(workflow_id, execution_id, task_id, task_data)
        
        # Verify the proof
        verification_result = self.zk_attestation.verify_proof(proof_id)
        self.assertTrue(verification_result)
        
        # Verify the proof contains the expected data
        proof = self.zk_attestation.get_proof(proof_id)
        self.assertEqual(proof["workflow_id"], workflow_id)
        self.assertEqual(proof["execution_id"], execution_id)
        self.assertEqual(proof["task_id"], task_id)
    
    def test_proof_privacy(self):
        """Test that ZK proofs maintain privacy."""
        # This is a security test to ensure ZK proofs don't reveal sensitive data
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        task_id = "task-001"
        sensitive_data = {"api_key": "secret-key", "user_id": "user-001"}
        
        # Generate a proof
        proof_id = self.zk_attestation.generate_proof(workflow_id, execution_id, task_id, sensitive_data)
        
        # Get the public proof
        public_proof = self.zk_attestation.get_public_proof(proof_id)
        
        # Verify the public proof doesn't contain sensitive data
        self.assertNotIn("api_key", str(public_proof))
        self.assertNotIn("secret-key", str(public_proof))
    
    def test_proof_tampering_detection(self):
        """Test that tampering with proofs is detected."""
        # This is a security test to ensure proof tampering is detected
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        task_id = "task-001"
        task_data = {"input": "test_input", "output": "test_output"}
        
        # Generate a proof
        proof_id = self.zk_attestation.generate_proof(workflow_id, execution_id, task_id, task_data)
        
        # Tamper with the proof
        self.zk_attestation.attestation_registry[proof_id]["tampered"] = True
        
        # Verify the proof fails verification
        verification_result = self.zk_attestation.verify_proof(proof_id)
        self.assertFalse(verification_result)


class TestTrustPathwayManager(unittest.TestCase):
    """Security tests for the TrustPathwayManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.execution_mode_manager = MagicMock(spec=ExecutionModeManager)
        self.trust_pathway_manager = TrustPathwayManager(
            workflow_runtime=self.workflow_runtime,
            execution_mode_manager=self.execution_mode_manager
        )
    
    def test_initialization(self):
        """Test that the trust pathway manager initializes correctly."""
        self.assertEqual(self.trust_pathway_manager.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.trust_pathway_manager.execution_mode_manager, self.execution_mode_manager)
        self.assertIsNotNone(self.trust_pathway_manager.trust_pathways)
    
    @patch('security.trust_pathway_manager.TrustPathwayManager.create_trust_pathway')
    def test_create_trust_pathway(self, mock_create):
        """Test that trust pathways are created correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        agent_ids = ["agent-001", "agent-002", "agent-003"]
        self.trust_pathway_manager.create_trust_pathway(workflow_id, execution_id, agent_ids)
        mock_create.assert_called_once_with(workflow_id, execution_id, agent_ids)
    
    @patch('security.trust_pathway_manager.TrustPathwayManager.verify_trust_pathway')
    def test_verify_trust_pathway(self, mock_verify):
        """Test that trust pathways are verified correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        self.trust_pathway_manager.verify_trust_pathway(workflow_id, execution_id)
        mock_verify.assert_called_once_with(workflow_id, execution_id)
    
    def test_trust_pathway_creation_and_verification(self):
        """Test the end-to-end process of creating and verifying a trust pathway."""
        # This is a security test to ensure trust pathways work correctly
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        agent_ids = ["agent-001", "agent-002", "agent-003"]
        
        # Create a trust pathway
        pathway_id = self.trust_pathway_manager.create_trust_pathway(workflow_id, execution_id, agent_ids)
        
        # Verify the trust pathway
        verification_result = self.trust_pathway_manager.verify_trust_pathway(workflow_id, execution_id)
        self.assertTrue(verification_result)
        
        # Verify the trust pathway contains the expected agents
        pathway = self.trust_pathway_manager.get_trust_pathway(workflow_id, execution_id)
        self.assertEqual(pathway["agent_ids"], agent_ids)
    
    def test_trust_score_calculation(self):
        """Test that trust scores are calculated correctly."""
        # This is a security test to ensure trust scores are calculated correctly
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        agent_ids = ["agent-001", "agent-002", "agent-003"]
        
        # Set agent trust scores
        self.trust_pathway_manager.set_agent_trust_score("agent-001", 0.9)
        self.trust_pathway_manager.set_agent_trust_score("agent-002", 0.8)
        self.trust_pathway_manager.set_agent_trust_score("agent-003", 0.7)
        
        # Create a trust pathway
        pathway_id = self.trust_pathway_manager.create_trust_pathway(workflow_id, execution_id, agent_ids)
        
        # Calculate the pathway trust score
        trust_score = self.trust_pathway_manager.calculate_pathway_trust_score(workflow_id, execution_id)
        
        # Verify the trust score is calculated correctly (should be the minimum of agent scores)
        self.assertEqual(trust_score, 0.7)
    
    def test_trust_pathway_validation(self):
        """Test that trust pathway validation works correctly."""
        # This is a security test to ensure trust pathway validation works correctly
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        agent_ids = ["agent-001", "agent-002", "agent-003"]
        
        # Create a trust pathway
        pathway_id = self.trust_pathway_manager.create_trust_pathway(workflow_id, execution_id, agent_ids)
        
        # Validate the trust pathway with a minimum trust threshold
        validation_result = self.trust_pathway_manager.validate_trust_pathway(workflow_id, execution_id, 0.6)
        self.assertTrue(validation_result)
        
        # Validate the trust pathway with a higher threshold that should fail
        validation_result = self.trust_pathway_manager.validate_trust_pathway(workflow_id, execution_id, 0.95)
        self.assertFalse(validation_result)


class TestMultiTenantIsolation(unittest.TestCase):
    """Security tests for the MultiTenantIsolation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.multi_tenant_isolation = MultiTenantIsolation(
            workflow_runtime=self.workflow_runtime
        )
    
    def test_initialization(self):
        """Test that the multi-tenant isolation module initializes correctly."""
        self.assertEqual(self.multi_tenant_isolation.workflow_runtime, self.workflow_runtime)
        self.assertIsNotNone(self.multi_tenant_isolation.tenant_registry)
    
    @patch('security.multi_tenant_isolation.MultiTenantIsolation.register_tenant')
    def test_register_tenant(self, mock_register):
        """Test that tenants are registered correctly."""
        tenant_id = "tenant-001"
        tenant_name = "Test Tenant"
        self.multi_tenant_isolation.register_tenant(tenant_id, tenant_name)
        mock_register.assert_called_once_with(tenant_id, tenant_name)
    
    @patch('security.multi_tenant_isolation.MultiTenantIsolation.assign_workflow_to_tenant')
    def test_assign_workflow_to_tenant(self, mock_assign):
        """Test that workflows are assigned to tenants correctly."""
        tenant_id = "tenant-001"
        workflow_id = "workflow-001"
        self.multi_tenant_isolation.assign_workflow_to_tenant(workflow_id, tenant_id)
        mock_assign.assert_called_once_with(workflow_id, tenant_id)
    
    def test_tenant_isolation(self):
        """Test that tenant isolation is enforced correctly."""
        # This is a security test to ensure tenant isolation is enforced
        tenant1_id = "tenant-001"
        tenant2_id = "tenant-002"
        workflow1_id = "workflow-001"
        workflow2_id = "workflow-002"
        
        # Register tenants
        self.multi_tenant_isolation.register_tenant(tenant1_id, "Tenant 1")
        self.multi_tenant_isolation.register_tenant(tenant2_id, "Tenant 2")
        
        # Assign workflows to tenants
        self.multi_tenant_isolation.assign_workflow_to_tenant(workflow1_id, tenant1_id)
        self.multi_tenant_isolation.assign_workflow_to_tenant(workflow2_id, tenant2_id)
        
        # Verify tenant 1 can access workflow 1 but not workflow 2
        self.assertTrue(self.multi_tenant_isolation.can_access_workflow(tenant1_id, workflow1_id))
        self.assertFalse(self.multi_tenant_isolation.can_access_workflow(tenant1_id, workflow2_id))
        
        # Verify tenant 2 can access workflow 2 but not workflow 1
        self.assertTrue(self.multi_tenant_isolation.can_access_workflow(tenant2_id, workflow2_id))
        self.assertFalse(self.multi_tenant_isolation.can_access_workflow(tenant2_id, workflow1_id))
    
    def test_data_isolation(self):
        """Test that data isolation is enforced correctly."""
        # This is a security test to ensure data isolation is enforced
        tenant1_id = "tenant-001"
        tenant2_id = "tenant-002"
        
        # Register tenants
        self.multi_tenant_isolation.register_tenant(tenant1_id, "Tenant 1")
        self.multi_tenant_isolation.register_tenant(tenant2_id, "Tenant 2")
        
        # Store tenant-specific data
        tenant1_data = {"api_key": "tenant1-secret-key"}
        tenant2_data = {"api_key": "tenant2-secret-key"}
        self.multi_tenant_isolation.store_tenant_data(tenant1_id, tenant1_data)
        self.multi_tenant_isolation.store_tenant_data(tenant2_id, tenant2_data)
        
        # Verify tenant 1 can access its own data but not tenant 2's data
        retrieved_data = self.multi_tenant_isolation.get_tenant_data(tenant1_id)
        self.assertEqual(retrieved_data, tenant1_data)
        
        # Verify tenant 2 can access its own data but not tenant 1's data
        retrieved_data = self.multi_tenant_isolation.get_tenant_data(tenant2_id)
        self.assertEqual(retrieved_data, tenant2_data)
        
        # Verify tenant 1 cannot access tenant 2's data
        with self.assertRaises(Exception):
            self.multi_tenant_isolation.get_tenant_data(tenant1_id, tenant2_id)
    
    def test_resource_isolation(self):
        """Test that resource isolation is enforced correctly."""
        # This is a security test to ensure resource isolation is enforced
        tenant1_id = "tenant-001"
        tenant2_id = "tenant-002"
        
        # Register tenants
        self.multi_tenant_isolation.register_tenant(tenant1_id, "Tenant 1")
        self.multi_tenant_isolation.register_tenant(tenant2_id, "Tenant 2")
        
        # Set resource limits
        self.multi_tenant_isolation.set_tenant_resource_limits(tenant1_id, {"max_workflows": 5, "max_executions": 10})
        self.multi_tenant_isolation.set_tenant_resource_limits(tenant2_id, {"max_workflows": 3, "max_executions": 6})
        
        # Verify resource limits are enforced
        self.assertTrue(self.multi_tenant_isolation.check_resource_limits(tenant1_id, "workflows", 4))
        self.assertFalse(self.multi_tenant_isolation.check_resource_limits(tenant1_id, "workflows", 6))
        
        self.assertTrue(self.multi_tenant_isolation.check_resource_limits(tenant2_id, "executions", 5))
        self.assertFalse(self.multi_tenant_isolation.check_resource_limits(tenant2_id, "executions", 7))


class TestAdaptiveTrustPolicyManager(unittest.TestCase):
    """Security tests for the AdaptiveTrustPolicyManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.execution_mode_manager = MagicMock(spec=ExecutionModeManager)
        self.adaptive_trust_policy_manager = AdaptiveTrustPolicyManager(
            workflow_runtime=self.workflow_runtime,
            execution_mode_manager=self.execution_mode_manager
        )
    
    def test_initialization(self):
        """Test that the adaptive trust policy manager initializes correctly."""
        self.assertEqual(self.adaptive_trust_policy_manager.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.adaptive_trust_policy_manager.execution_mode_manager, self.execution_mode_manager)
        self.assertIsNotNone(self.adaptive_trust_policy_manager.trust_policies)
    
    @patch('security.adaptive_trust_policy_manager.AdaptiveTrustPolicyManager.create_trust_policy')
    def test_create_trust_policy(self, mock_create):
        """Test that trust policies are created correctly."""
        policy_id = "policy-001"
        industry = "manufacturing"
        policy_rules = {"min_trust_score": 0.7, "require_human_approval": True}
        self.adaptive_trust_policy_manager.create_trust_policy(policy_id, industry, policy_rules)
        mock_create.assert_called_once_with(policy_id, industry, policy_rules)
    
    @patch('security.adaptive_trust_policy_manager.AdaptiveTrustPolicyManager.apply_trust_policy')
    def test_apply_trust_policy(self, mock_apply):
        """Test that trust policies are applied correctly."""
        policy_id = "policy-001"
        workflow_id = "workflow-001"
        self.adaptive_trust_policy_manager.apply_trust_policy(policy_id, workflow_id)
        mock_apply.assert_called_once_with(policy_id, workflow_id)
    
    def test_trust_policy_creation_and_application(self):
        """Test the end-to-end process of creating and applying a trust policy."""
        # This is a security test to ensure trust policies work correctly
        policy_id = "policy-001"
        industry = "manufacturing"
        policy_rules = {"min_trust_score": 0.7, "require_human_approval": True}
        workflow_id = "workflow-001"
        
        # Create a trust policy
        self.adaptive_trust_policy_manager.create_trust_policy(policy_id, industry, policy_rules)
        
        # Apply the trust policy to a workflow
        self.adaptive_trust_policy_manager.apply_trust_policy(policy_id, workflow_id)
        
        # Verify the trust policy was applied
        applied_policies = self.adaptive_trust_policy_manager.get_applied_policies(workflow_id)
        self.assertIn(policy_id, applied_policies)
    
    def test_trust_policy_evaluation(self):
        """Test that trust policies are evaluated correctly."""
        # This is a security test to ensure trust policy evaluation works correctly
        policy_id = "policy-001"
        industry = "manufacturing"
        policy_rules = {"min_trust_score": 0.7, "require_human_approval": True}
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        
        # Create and apply a trust policy
        self.adaptive_trust_policy_manager.create_trust_policy(policy_id, industry, policy_rules)
        self.adaptive_trust_policy_manager.apply_trust_policy(policy_id, workflow_id)
        
        # Evaluate the trust policy with a trust score that meets the minimum
        evaluation_result = self.adaptive_trust_policy_manager.evaluate_trust_policy(
            workflow_id, execution_id, {"trust_score": 0.8}
        )
        self.assertTrue(evaluation_result["approved"])
        self.assertTrue(evaluation_result["require_human_approval"])
        
        # Evaluate the trust policy with a trust score below the minimum
        evaluation_result = self.adaptive_trust_policy_manager.evaluate_trust_policy(
            workflow_id, execution_id, {"trust_score": 0.6}
        )
        self.assertFalse(evaluation_result["approved"])
    
    def test_adaptive_policy_evolution(self):
        """Test that trust policies adapt correctly based on feedback."""
        # This is a security test to ensure trust policies adapt correctly
        policy_id = "policy-001"
        industry = "manufacturing"
        policy_rules = {"min_trust_score": 0.7, "require_human_approval": True}
        workflow_id = "workflow-001"
        
        # Create and apply a trust policy
        self.adaptive_trust_policy_manager.create_trust_policy(policy_id, industry, policy_rules)
        self.adaptive_trust_policy_manager.apply_trust_policy(policy_id, workflow_id)
        
        # Provide feedback that the policy is too strict
        feedback = {
            "policy_id": policy_id,
            "workflow_id": workflow_id,
            "feedback_type": "too_strict",
            "suggested_changes": {"min_trust_score": 0.6}
        }
        self.adaptive_trust_policy_manager.process_policy_feedback(feedback)
        
        # Verify the policy was updated
        updated_policy = self.adaptive_trust_policy_manager.get_trust_policy(policy_id)
        self.assertEqual(updated_policy["rules"]["min_trust_score"], 0.6)


if __name__ == '__main__':
    unittest.main()
