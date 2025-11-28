# /home/ubuntu/core_ai_layer_extracted/home/ubuntu/final_structure/base/core_ai_layer/llm_service/token_usage_tracking_service.py
"""
Token Usage Tracking Service for the Industriverse Core AI Layer.

This service is responsible for monitoring, recording, and analyzing token
consumption by Large Language Models (LLMs) within the Industriverse platform.
It provides crucial data for cost management, resource allocation, usage pattern
analysis, API monitoring, and potentially for implementing quotas and billing.

Security and Privacy Considerations:
- All API endpoints must be protected by authentication and authorization mechanisms.
- Sensitive data within usage records (if any, e.g., in custom_metadata) should be
  handled according to privacy policies, potentially requiring masking or anonymization.
- Data should be encrypted in transit (e.g., via TLS/SSL for API calls) and at rest
  (e.g., database-level encryption).
- Audit trails should be maintained for access to usage data and administrative actions.
"""

import datetime
import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Union
from collections import defaultdict

# Assuming a common logger setup for the Core AI Layer
# from ..utils.common_ai_utils import get_core_ai_logger
# logger = get_core_ai_logger(__name__)
# For now, using a standard logger:
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# In-memory store for simulation if no data_layer_client is provided.
SIMULATED_DB: List[Dict[str, Any]] = []

class AuthenticationError(Exception):
    "Custom exception for authentication failures."
    pass

class AuthorizationError(Exception):
    "Custom exception for authorization failures."
    pass

class TokenUsageTrackingService:
    """
    Manages the tracking of LLM token usage with security and privacy considerations.
    """

    def __init__(self, 
                 data_layer_client: Optional[Any] = None, 
                 message_queue_client: Optional[Any] = None, 
                 identity_service_client: Optional[Any] = None, # For authN/authZ
                 config: Optional[Dict[str, Any]] = None):
        """
        Initializes the TokenUsageTrackingService.

        Args:
            data_layer_client: Client for Data Layer interaction.
            message_queue_client: Client for message queue interaction.
            identity_service_client: Client for Identity Management Service (for authN/authZ).
            config: Service configuration.
        """
        self.data_layer_client = data_layer_client
        self.message_queue_client = message_queue_client
        self.identity_service_client = identity_service_client # Placeholder for actual client
        self.config = config if config else {}
        self._simulated_event_store: List[Dict[str, Any]] = SIMULATED_DB if not self.data_layer_client else []
        logger.info("TokenUsageTrackingService initialized with security considerations.")

    def _generate_request_id(self) -> str:
        return str(uuid.uuid4())

    def _get_current_timestamp(self) -> str:
        return datetime.datetime.utcnow().isoformat()

    def _validate_usage_event(self, event_data: Dict[str, Any]) -> bool:
        required_fields = ["user_id", "model_id", "input_tokens", "output_tokens"]
        for field in required_fields:
            if field not in event_data:
                logger.error(f"Validation failed: Missing required field \'{field}\' in usage event: {event_data}")
                return False
        if not isinstance(event_data["input_tokens"], int) or event_data["input_tokens"] < 0:
            logger.error(f"Validation failed: \'input_tokens\' must be a non-negative integer in event: {event_data}")
            return False
        if not isinstance(event_data["output_tokens"], int) or event_data["output_tokens"] < 0:
            logger.error(f"Validation failed: \'output_tokens\' must be a non-negative integer in event: {event_data}")
            return False
        return True

    def _enrich_usage_event(self, event_data: Dict[str, Any], calling_user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        enriched_event = event_data.copy()
        if "request_id" not in enriched_event:
            enriched_event["request_id"] = self._generate_request_id()
        if "timestamp" not in enriched_event:
            enriched_event["timestamp"] = self._get_current_timestamp()
        
        enriched_event["total_tokens"] = enriched_event.get("input_tokens", 0) + enriched_event.get("output_tokens", 0)
        
        cost_models = self.config.get("cost_models", {})
        model_specific_cost = cost_models.get(enriched_event.get("model_id", ""), {})
        input_cost_per_token = model_specific_cost.get("input_per_token", 0)
        output_cost_per_token = model_specific_cost.get("output_per_token", model_specific_cost.get("per_token", 0))
        
        estimated_cost = (enriched_event.get("input_tokens", 0) * input_cost_per_token) + \
                         (enriched_event.get("output_tokens", 0) * output_cost_per_token)
                         
        enriched_event["estimated_cost"] = round(estimated_cost, 6)
        enriched_event["currency"] = model_specific_cost.get("currency", "USD")

        # Placeholder: Enrich with verified user/tenant info from identity_service_client if context is available
        if calling_user_context and self.identity_service_client:
            # enriched_event["verified_user_id"] = calling_user_context.get("user_id")
            # enriched_event["verified_tenant_id"] = calling_user_context.get("tenant_id")
            pass # Actual enrichment logic here

        # Placeholder: Data masking/anonymization for sensitive custom_metadata fields
        if "custom_metadata" in enriched_event and isinstance(enriched_event["custom_metadata"], dict):
            # Example: if enriched_event["custom_metadata"].get("potentially_sensitive_field"):
            #     enriched_event["custom_metadata"]["potentially_sensitive_field"] = "***MASKED***"
            pass # Actual masking logic here based on policy

        logger.debug(f"Enriched usage event: {enriched_event}")
        return enriched_event

    async def _authorize_action(self, user_context: Dict[str, Any], action: str, resource: Optional[Dict[str, Any]] = None) -> bool:
        """Placeholder for authorization logic using IdentityManagementService."""
        if not self.identity_service_client:
            logger.warning("Identity service client not configured. Skipping authorization (NOT FOR PRODUCTION).")
            return True # Default to allow if no identity client for simulation
        
        # try:
        #     is_authorized = await self.identity_service_client.check_permission(user_context, action, resource)
        #     if not is_authorized:
        #         logger.warning(f"User {user_context.get(\'user_id\')} not authorized for action \'{action}\'.")
        #         return False
        #     return True
        # except Exception as e:
        #     logger.error(f"Authorization check failed: {e}", exc_info=True)
        #     return False
        logger.info(f"(Placeholder) Authorizing user {user_context.get('user_id')} for action '{action}'.")
        return True # Simulate authorization pass

    async def publish_usage_event_async(self, usage_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> bool:
        logger.info(f"Attempting to publish usage event: {usage_data}")
        # In a real scenario, user_context would be derived from the authenticated request to LLMInferenceService
        # For now, it can be passed in. If not, some operations might be restricted or use default/system identity.
        
        # Authorization: Check if the entity (user/service) is allowed to publish usage events
        # This might be a general permission or tied to the resources in usage_data (e.g., specific model_id)
        # For simplicity, assuming a general publish permission here.
        # if user_context and not await self._authorize_action(user_context, "publish_token_usage"): 
        #     raise AuthorizationError("Not authorized to publish token usage events.")

        if not self._validate_usage_event(usage_data):
            return False

        event_to_process = self._enrich_usage_event(usage_data, user_context)

        if self.message_queue_client:
            try:
                # await self.message_queue_client.publish("token_usage_topic", json.dumps(event_to_process))
                logger.info(f"Event (conceptually) published to message queue: {event_to_process}")
                return True 
            except Exception as e:
                logger.error(f"Failed to publish usage event to message queue: {e}", exc_info=True)
                return False
        else:
            logger.warning("Message queue client not configured. Processing event directly (synchronously for simulation).")
            return await self.process_usage_event_from_queue(event_to_process, user_context)

    async def process_usage_event_from_queue(self, event_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> bool:
        logger.info(f"Processing usage event: {event_data}")
        processed_event = self._enrich_usage_event(event_data, user_context) # Pass context for enrichment if needed

        # Data Layer interaction should also consider security (e.g., connection security)
        if self.data_layer_client:
            try:
                # await self.data_layer_client.store_token_usage(processed_event)
                logger.info(f"Usage event (conceptually) stored in data layer: {processed_event}")
                # Placeholder: Audit log for data storage
                # await self.audit_log_action(user_context or {"system_user": "token_tracker_processor"}, "store_token_usage_record", {"request_id": processed_event["request_id"]})
                return True
            except Exception as e:
                logger.error(f"Failed to store usage event in data layer: {e}", exc_info=True)
                return False
        else:
            logger.warning("Data layer client not configured. Storing event in simulated in-memory DB.")
            self._simulated_event_store.append(processed_event)
            return True

    async def get_usage_summary(self, 
                                user_context: Dict[str, Any], # User context for authorization
                                user_id_filter: Optional[str] = None, 
                                application_id_filter: Optional[str] = None, 
                                model_id_filter: Optional[str] = None, 
                                tenant_id_filter: Optional[str] = None,
                                start_time: Optional[str] = None, 
                                end_time: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"User {user_context.get('user_id')} attempting to get usage summary.")
        
        # Authorization: Check if user can access usage summaries.
        # Potentially, restrict filters based on user role (e.g., user can only see their own usage).
        if not await self._authorize_action(user_context, "get_token_usage_summary", 
                                          resource={"filters": {"user_id": user_id_filter, "tenant_id": tenant_id_filter}}):
            raise AuthorizationError("Not authorized to get usage summary with specified filters.")

        # If user is not an admin, they might only be allowed to query their own data
        # effective_user_id_filter = user_id_filter
        # if not user_context.get("is_admin"): # Assuming admin status in context
        #     effective_user_id_filter = user_context.get("user_id")
        #     if user_id_filter and user_id_filter != effective_user_id_filter:
        #        raise AuthorizationError("Users can only query their own usage data.")

        filters = {
            "user_id": user_id_filter, # Use effective_user_id_filter in a real scenario
            "application_id": application_id_filter,
            "model_id": model_id_filter,
            "tenant_id": tenant_id_filter,
            "start_time": start_time,
            "end_time": end_time
        }

        if self.data_layer_client:
            logger.info("(Placeholder) Real data_layer_client would query the database, respecting authZ.")

        logger.info("Using simulated in-memory store for usage summary.")
        summary = {
            "total_requests": 0, "total_input_tokens": 0, "total_output_tokens": 0,
            "total_tokens_sum": 0, "estimated_total_cost": 0.0, "currency": "USD",
            "filters_applied": {k: v for k, v in filters.items() if v is not None}
        }
        
        applicable_records = []
        for record in self._simulated_event_store:
            match = True
            # Apply filters (ensure user_id_filter respects authorization)
            # Example: if filters["user_id"] and record.get("user_id") != filters["user_id"]: match = False
            # (Simplified for placeholder)
            if filters["user_id"] and record.get("user_id") != filters["user_id"]: match = False
            if filters["application_id"] and record.get("application_id") != filters["application_id"]: match = False
            if filters["model_id"] and record.get("model_id") != filters["model_id"]: match = False
            if filters["tenant_id"] and record.get("tenant_id") != filters["tenant_id"]: match = False
            if filters["start_time"] and record.get("timestamp", "") < filters["start_time"]: match = False
            if filters["end_time"] and record.get("timestamp", "") > filters["end_time"]: match = False
            if match:
                applicable_records.append(record)
        
        if not applicable_records: return summary

        summary["total_requests"] = len(applicable_records)
        summary["total_input_tokens"] = sum(r.get("input_tokens", 0) for r in applicable_records)
        summary["total_output_tokens"] = sum(r.get("output_tokens", 0) for r in applicable_records)
        summary["total_tokens_sum"] = sum(r.get("total_tokens", 0) for r in applicable_records)
        summary["estimated_total_cost"] = round(sum(r.get("estimated_cost", 0.0) for r in applicable_records), 6)
        if applicable_records: summary["currency"] = applicable_records[0].get("currency", "USD") 

        # Placeholder: Audit log for data access
        # await self.audit_log_action(user_context, "get_token_usage_summary_access", {"filters": filters, "num_results": len(applicable_records)})
        logger.info(f"Returning summary: {summary}")
        return summary

    async def get_detailed_usage_records(self, 
                                         user_context: Dict[str, Any], # User context for authorization
                                         user_id_filter: Optional[str] = None, 
                                         application_id_filter: Optional[str] = None,
                                         model_id_filter: Optional[str] = None,
                                         tenant_id_filter: Optional[str] = None,
                                         request_id_filter: Optional[str] = None,
                                         start_time: Optional[str] = None, 
                                         end_time: Optional[str] = None,
                                         limit: int = 100, 
                                         offset: int = 0) -> List[Dict[str, Any]]:
        logger.info(f"User {user_context.get('user_id')} attempting to get detailed usage records.")

        if not await self._authorize_action(user_context, "get_detailed_token_usage", 
                                          resource={"filters": {"user_id": user_id_filter, "tenant_id": tenant_id_filter}}):
            raise AuthorizationError("Not authorized to get detailed usage records with specified filters.")

        # Similar logic for effective_user_id_filter as in get_usage_summary

        filters = {
            "user_id": user_id_filter,
            "application_id": application_id_filter,
            "model_id": model_id_filter,
            "tenant_id": tenant_id_filter,
            "request_id": request_id_filter,
            "start_time": start_time,
            "end_time": end_time
        }

        if self.data_layer_client:
            logger.info("(Placeholder) Real data_layer_client would query the database, respecting authZ.")

        logger.info("Using simulated in-memory store for detailed records.")
        filtered_records = []
        for record in self._simulated_event_store:
            match = True
            # Apply filters (ensure user_id_filter respects authorization)
            if filters["user_id"] and record.get("user_id") != filters["user_id"]: match = False
            if filters["application_id"] and record.get("application_id") != filters["application_id"]: match = False
            # ... (all other filters)
            if match:
                filtered_records.append(record)
        
        filtered_records.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
        paginated_records = filtered_records[offset : offset + limit]

        # Placeholder: Audit log for data access
        # await self.audit_log_action(user_context, "get_detailed_token_usage_access", {"filters": filters, "num_results": len(paginated_records)})
        logger.info(f"Returning {len(paginated_records)} detailed records.")
        return paginated_records

    async def audit_log_action(self, user_context: Dict[str, Any], action: str, details: Dict[str, Any]):
        """Placeholder for logging actions to an audit trail."""
        # This would typically integrate with a dedicated Audit Logging Service
        log_message = f"AUDIT: User '{user_context.get('user_id', 'system')}' performed action '{action}'. Details: {json.dumps(details)}"
        logger.info(log_message) # Replace with actual audit logging call

# Example Usage
async def main_example():
    SIMULATED_DB.clear()
    service_config = {
        "cost_models": {
            "gpt-4-turbo": {"input_per_token": 0.00001, "output_per_token": 0.00003, "currency": "USD"},
            "claude-3-opus": {"input_per_token": 0.000015, "output_per_token": 0.000075, "currency": "USD"}
        }
    }
    # Simulated identity client and user contexts
    mock_identity_client = object() # Placeholder
    admin_user_context = {"user_id": "admin-001", "roles": ["admin"], "tenant_id": "system"}
    regular_user_context = {"user_id": "user-123", "roles": ["user"], "tenant_id": "tenant-a"}

    token_tracker = TokenUsageTrackingService(config=service_config, identity_service_client=mock_identity_client)

    usage_event_1 = {
        "user_id": "user-123", "application_id": "app-xyz", "tenant_id": "tenant-a",
        "model_id": "gpt-4-turbo", "input_tokens": 100, "output_tokens": 50
    }
    # Publishing usually done by system/LLMInferenceService, context might be simpler or system-level
    await token_tracker.publish_usage_event_async(usage_event_1, user_context=regular_user_context) 

    print("\n--- Testing Get Usage Summary (as admin) ---")
    try:
        summary_admin = await token_tracker.get_usage_summary(user_context=admin_user_context, tenant_id_filter="tenant-a")
        print(f"Admin Summary for tenant-a: {json.dumps(summary_admin, indent=2)}")
    except AuthorizationError as e:
        print(f"Authorization Error: {e}")

    print("\n--- Testing Get Usage Summary (as regular user, for own data) ---")
    try:
        # In a real system, the service might enforce user_id_filter to be same as user_context["user_id"]
        # or the _authorize_action would handle this restriction.
        summary_user = await token_tracker.get_usage_summary(user_context=regular_user_context, user_id_filter="user-123")
        print(f"User Summary for user-123: {json.dumps(summary_user, indent=2)}")
    except AuthorizationError as e:
        print(f"Authorization Error: {e}")

    print("\n--- Testing Get Usage Summary (as regular user, attempting to access other user data - should be handled by authZ) ---")
    try:
        # This call might be blocked by _authorize_action if it checks that user_id_filter matches context or if user is not admin
        summary_other_user_attempt = await token_tracker.get_usage_summary(user_context=regular_user_context, user_id_filter="user-admin-should-not-see")
        print(f"User Summary for other user (attempt): {json.dumps(summary_other_user_attempt, indent=2)}")
    except AuthorizationError as e:
        print(f"Authorization Error (expected for other user): {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main_example()) 

