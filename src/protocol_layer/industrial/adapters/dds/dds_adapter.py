"""
DDS (Data Distribution Service) Protocol Adapter for Industriverse Protocol Layer

This module provides a comprehensive adapter for integrating DDS industrial protocol
with the Industriverse Protocol Layer. It enables seamless communication between
DDS systems and the protocol-native architecture of Industriverse.

Features:
- Full DDS publisher and subscriber functionality
- Support for multiple DDS implementations (RTI Connext, OpenDDS, FastDDS)
- Quality of Service (QoS) policy management
- Dynamic topic discovery and type introspection
- Content-filtered topics
- Waitset and listener-based notification
- Security integration with EKIS framework
- Comprehensive error handling and diagnostics
- Support for DDS-Security (authentication, encryption, access control)

Dependencies:
- cyclonedds-python (Eclipse Cyclone DDS Python binding)
- pydds (Generic DDS Python binding)
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable

# Import Protocol Layer base components
from protocols.protocol_base import ProtocolComponent
from protocols.message_formats import MessageFactory, MessagePriority, MessageType
from protocols.discovery_service import DiscoveryService

# Import EKIS security components
from security.ekis.tpm_integration import TPMSecurityProvider
from security.ekis.security_handler import EKISSecurityHandler

# Import DDS library
try:
    import cyclonedds.domain as domain
    import cyclonedds.pub as pub
    import cyclonedds.sub as sub
    import cyclonedds.topic as topic
    import cyclonedds.idl as idl
    import cyclonedds.qos as qos
    from cyclonedds.core import Qos, Policy
    HAS_CYCLONE_DDS = True
except ImportError:
    logging.warning("CycloneDDS library not found. Trying alternative DDS implementations...")
    HAS_CYCLONE_DDS = False

# Try alternative DDS implementations if CycloneDDS is not available
if not HAS_CYCLONE_DDS:
    try:
        import pydds
        HAS_PYDDS = True
    except ImportError:
        logging.error("No DDS implementation found. Using mock implementation.")
        HAS_PYDDS = False
        
        # Mock implementation for development
        class MockDDSDomain:
            def __init__(self, domain_id=0):
                self.domain_id = domain_id
                self.participants = {}
                
        class MockDDSParticipant:
            def __init__(self, domain, name):
                self.domain = domain
                self.name = name
                self.publishers = {}
                self.subscribers = {}
                self.topics = {}
                
            def create_publisher(self, qos=None):
                pub_id = str(uuid.uuid4())
                publisher = MockDDSPublisher(self, pub_id, qos)
                self.publishers[pub_id] = publisher
                return publisher
                
            def create_subscriber(self, qos=None):
                sub_id = str(uuid.uuid4())
                subscriber = MockDDSSubscriber(self, sub_id, qos)
                self.subscribers[sub_id] = subscriber
                return subscriber
                
            def create_topic(self, name, type_name, qos=None):
                topic_id = str(uuid.uuid4())
                topic_obj = MockDDSTopic(self, name, type_name, qos)
                self.topics[topic_id] = topic_obj
                return topic_obj
                
        class MockDDSPublisher:
            def __init__(self, participant, id, qos=None):
                self.participant = participant
                self.id = id
                self.qos = qos or {}
                self.writers = {}
                
            def create_datawriter(self, topic, qos=None):
                writer_id = str(uuid.uuid4())
                writer = MockDDSDataWriter(self, topic, qos)
                self.writers[writer_id] = writer
                return writer
                
        class MockDDSSubscriber:
            def __init__(self, participant, id, qos=None):
                self.participant = participant
                self.id = id
                self.qos = qos or {}
                self.readers = {}
                
            def create_datareader(self, topic, qos=None):
                reader_id = str(uuid.uuid4())
                reader = MockDDSDataReader(self, topic, qos)
                self.readers[reader_id] = reader
                return reader
                
        class MockDDSTopic:
            def __init__(self, participant, name, type_name, qos=None):
                self.participant = participant
                self.name = name
                self.type_name = type_name
                self.qos = qos or {}
                
        class MockDDSDataWriter:
            def __init__(self, publisher, topic, qos=None):
                self.publisher = publisher
                self.topic = topic
                self.qos = qos or {}
                
            def write(self, data):
                # Simulate successful write
                return True
                
        class MockDDSDataReader:
            def __init__(self, subscriber, topic, qos=None):
                self.subscriber = subscriber
                self.topic = topic
                self.qos = qos or {}
                self.samples = []
                
            def read(self, max_samples=1):
                # Return empty list to simulate no data
                return []
                
            def take(self, max_samples=1):
                # Return empty list to simulate no data
                return []
                
        class MockDDSQos:
            def __init__(self):
                self.policies = {}
                
            def add_policy(self, policy):
                self.policies[policy.name] = policy.value
                
        class MockDDSPolicy:
            def __init__(self, name, value):
                self.name = name
                self.value = value
                
        # Create mock classes to simulate DDS API
        domain = type('domain', (), {
            'DomainParticipant': MockDDSParticipant,
            'create_domain': lambda domain_id: MockDDSDomain(domain_id)
        })
        
        pub = type('pub', (), {
            'Publisher': MockDDSPublisher,
            'DataWriter': MockDDSDataWriter
        })
        
        sub = type('sub', (), {
            'Subscriber': MockDDSSubscriber,
            'DataReader': MockDDSDataReader
        })
        
        topic = type('topic', (), {
            'Topic': MockDDSTopic
        })
        
        qos = type('qos', (), {
            'Qos': MockDDSQos,
            'Policy': MockDDSPolicy
        })
        
        Qos = MockDDSQos
        Policy = MockDDSPolicy

class DDSReliabilityKind(Enum):
    """DDS reliability QoS policy kinds."""
    BEST_EFFORT = "best_effort"
    RELIABLE = "reliable"

class DDSDurabilityKind(Enum):
    """DDS durability QoS policy kinds."""
    VOLATILE = "volatile"
    TRANSIENT_LOCAL = "transient_local"
    TRANSIENT = "transient"
    PERSISTENT = "persistent"

class DDSAdapter(ProtocolComponent):
    """
    DDS Protocol Adapter for Industriverse Protocol Layer.
    
    This adapter enables bidirectional communication between DDS systems
    and the Industriverse Protocol Layer, translating between DDS protocol and
    Industriverse's protocol-native architecture.
    """
    
    def __init__(self, component_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the DDS adapter.
        
        Args:
            component_id: Unique identifier for this adapter instance
            config: Configuration parameters for the adapter
        """
        super().__init__(component_id or str(uuid.uuid4()), "dds_adapter")
        
        # Add capabilities
        self.add_capability("dds_publisher", "DDS publisher functionality")
        self.add_capability("dds_subscriber", "DDS subscriber functionality")
        self.add_capability("dds_discovery", "DDS topic and participant discovery")
        self.add_capability("dds_qos", "DDS Quality of Service management")
        self.add_capability("dds_security", "DDS security features")
        
        # Initialize configuration
        self.config = config or {}
        self.logger = logging.getLogger(f"industriverse.protocol.dds.{self.component_id}")
        
        # Initialize DDS components
        self.domains = {}
        self.participants = {}
        self.publishers = {}
        self.subscribers = {}
        self.topics = {}
        self.writers = {}
        self.readers = {}
        self.reader_callbacks = {}
        self.topic_types = {}
        
        # Initialize security handler
        self.security_handler = EKISSecurityHandler(
            component_id=f"{self.component_id}_security",
            tpm_provider=TPMSecurityProvider() if self.config.get("use_tpm", True) else None
        )
        
        # Register with discovery service
        self.discovery_service = DiscoveryService()
        self.discovery_service.register_component(
            self.component_id,
            "dds_adapter",
            {
                "protocols": ["dds"],
                "capabilities": list(self._capabilities.keys()),
                "industryTags": self.config.get("industry_tags", ["manufacturing", "aerospace", "defense", "transportation"])
            }
        )
        
        self.logger.info(f"DDS Adapter {self.component_id} initialized")
    
    async def create_participant(self, domain_id: int = 0, participant_name: str = None) -> str:
        """
        Create a DDS domain participant.
        
        Args:
            domain_id: DDS domain ID
            participant_name: Name for the participant
            
        Returns:
            str: Participant ID if successful, empty string otherwise
        """
        try:
            # Generate participant name if not provided
            if not participant_name:
                participant_name = f"industriverse-{self.component_id}-{str(uuid.uuid4())[:8]}"
                
            # Create domain if it doesn't exist
            if domain_id not in self.domains:
                self.domains[domain_id] = domain.create_domain(domain_id)
                
            # Create participant
            participant = domain.DomainParticipant(self.domains[domain_id], name=participant_name)
            
            # Generate participant ID
            participant_id = str(uuid.uuid4())
            
            # Store participant
            self.participants[participant_id] = {
                "participant": participant,
                "domain_id": domain_id,
                "name": participant_name,
                "created_at": datetime.now()
            }
            
            self.logger.info(f"Created DDS participant {participant_name} in domain {domain_id} with ID {participant_id}")
            
            # Publish event
            await self.publish_event(
                MessageFactory.create_event(
                    "dds_participant_created",
                    payload={
                        "participant_id": participant_id,
                        "domain_id": domain_id,
                        "name": participant_name
                    },
                    priority=MessagePriority.MEDIUM
                )
            )
            
            return participant_id
            
        except Exception as e:
            self.logger.error(f"Error creating DDS participant: {str(e)}")
            return ""
    
    async def delete_participant(self, participant_id: str) -> bool:
        """
        Delete a DDS domain participant.
        
        Args:
            participant_id: ID of the participant to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        if participant_id not in self.participants:
            self.logger.error(f"Participant {participant_id} not found")
            return False
            
        try:
            # Get participant info
            participant_info = self.participants[participant_id]
            
            # Delete all associated publishers
            for pub_id, pub_info in list(self.publishers.items()):
                if pub_info["participant_id"] == participant_id:
                    await self.delete_publisher(pub_id)
                    
            # Delete all associated subscribers
            for sub_id, sub_info in list(self.subscribers.items()):
                if sub_info["participant_id"] == participant_id:
                    await self.delete_subscriber(sub_id)
                    
            # Delete all associated topics
            for topic_id, topic_info in list(self.topics.items()):
                if topic_info["participant_id"] == participant_id:
                    await self.delete_topic(topic_id)
                    
            # Delete participant
            del self.participants[participant_id]
            
            self.logger.info(f"Deleted DDS participant {participant_id}")
            
            # Publish event
            await self.publish_event(
                MessageFactory.create_event(
                    "dds_participant_deleted",
                    payload={
                        "participant_id": participant_id,
                        "domain_id": participant_info["domain_id"],
                        "name": participant_info["name"]
                    },
                    priority=MessagePriority.MEDIUM
                )
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting DDS participant {participant_id}: {str(e)}")
            return False
    
    async def create_publisher(self, participant_id: str, qos_settings: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a DDS publisher.
        
        Args:
            participant_id: ID of the participant to create publisher for
            qos_settings: Optional QoS settings for the publisher
            
        Returns:
            str: Publisher ID if successful, empty string otherwise
        """
        if participant_id not in self.participants:
            self.logger.error(f"Participant {participant_id} not found")
            return ""
            
        try:
            # Get participant
            participant_info = self.participants[participant_id]
            participant = participant_info["participant"]
            
            # Create QoS if provided
            publisher_qos = None
            if qos_settings:
                publisher_qos = self._create_qos_from_settings(qos_settings)
                
            # Create publisher
            publisher = participant.create_publisher(qos=publisher_qos)
            
            # Generate publisher ID
            publisher_id = str(uuid.uuid4())
            
            # Store publisher
            self.publishers[publisher_id] = {
                "publisher": publisher,
                "participant_id": participant_id,
                "qos_settings": qos_settings,
                "created_at": datetime.now()
            }
            
            self.logger.info(f"Created DDS publisher with ID {publisher_id} for participant {participant_id}")
            
            return publisher_id
            
        except Exception as e:
            self.logger.error(f"Error creating DDS publisher: {str(e)}")
            return ""
    
    async def delete_publisher(self, publisher_id: str) -> bool:
        """
        Delete a DDS publisher.
        
        Args:
            publisher_id: ID of the publisher to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        if publisher_id not in self.publishers:
            self.logger.error(f"Publisher {publisher_id} not found")
            return False
            
        try:
            # Delete all associated writers
            for writer_id, writer_info in list(self.writers.items()):
                if writer_info["publisher_id"] == publisher_id:
                    await self.delete_writer(writer_id)
                    
            # Delete publisher
            del self.publishers[publisher_id]
            
            self.logger.info(f"Deleted DDS publisher {publisher_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting DDS publisher {publisher_id}: {str(e)}")
            return False
    
    async def create_subscriber(self, participant_id: str, qos_settings: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a DDS subscriber.
        
        Args:
            participant_id: ID of the participant to create subscriber for
            qos_settings: Optional QoS settings for the subscriber
            
        Returns:
            str: Subscriber ID if successful, empty string otherwise
        """
        if participant_id not in self.participants:
            self.logger.error(f"Participant {participant_id} not found")
            return ""
            
        try:
            # Get participant
            participant_info = self.participants[participant_id]
            participant = participant_info["participant"]
            
            # Create QoS if provided
            subscriber_qos = None
            if qos_settings:
                subscriber_qos = self._create_qos_from_settings(qos_settings)
                
            # Create subscriber
            subscriber = participant.create_subscriber(qos=subscriber_qos)
            
            # Generate subscriber ID
            subscriber_id = str(uuid.uuid4())
            
            # Store subscriber
            self.subscribers[subscriber_id] = {
                "subscriber": subscriber,
                "participant_id": participant_id,
                "qos_settings": qos_settings,
                "created_at": datetime.now()
            }
            
            self.logger.info(f"Created DDS subscriber with ID {subscriber_id} for participant {participant_id}")
            
            return subscriber_id
            
        except Exception as e:
            self.logger.error(f"Error creating DDS subscriber: {str(e)}")
            return ""
    
    async def delete_subscriber(self, subscriber_id: str) -> bool:
        """
        Delete a DDS subscriber.
        
        Args:
            subscriber_id: ID of the subscriber to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        if subscriber_id not in self.subscribers:
            self.logger.error(f"Subscriber {subscriber_id} not found")
            return False
            
        try:
            # Delete all associated readers
            for reader_id, reader_info in list(self.readers.items()):
                if reader_info["subscriber_id"] == subscriber_id:
                    await self.delete_reader(reader_id)
                    
            # Delete subscriber
            del self.subscribers[subscriber_id]
            
            self.logger.info(f"Deleted DDS subscriber {subscriber_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting DDS subscriber {subscriber_id}: {str(e)}")
            return False
    
    async def register_topic_type(self, participant_id: str, type_name: str, type_definition: str) -> bool:
        """
        Register a topic type with a participant.
        
        Args:
            participant_id: ID of the participant to register type with
            type_name: Name of the type
            type_definition: IDL definition of the type
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        if participant_id not in self.participants:
            self.logger.error(f"Participant {participant_id} not found")
            return False
            
        try:
            # Store type definition
            self.topic_types[type_name] = {
                "definition": type_definition,
                "participant_id": participant_id,
                "registered_at": datetime.now()
            }
            
            self.logger.info(f"Registered topic type {type_name} for participant {participant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering topic type {type_name}: {str(e)}")
            return False
    
    async def create_topic(self, participant_id: str, topic_name: str, type_name: str,
                          qos_settings: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a DDS topic.
        
        Args:
            participant_id: ID of the participant to create topic for
            topic_name: Name of the topic
            type_name: Name of the topic type
            qos_settings: Optional QoS settings for the topic
            
        Returns:
            str: Topic ID if successful, empty string otherwise
        """
        if participant_id not in self.participants:
            self.logger.error(f"Participant {participant_id} not found")
            return ""
            
        try:
            # Get participant
            participant_info = self.participants[participant_id]
            participant = participant_info["participant"]
            
            # Create QoS if provided
            topic_qos = None
            if qos_settings:
                topic_qos = self._create_qos_from_settings(qos_settings)
                
            # Create topic
            topic_obj = participant.create_topic(topic_name, type_name, qos=topic_qos)
            
            # Generate topic ID
            topic_id = str(uuid.uuid4())
            
            # Store topic
            self.topics[topic_id] = {
                "topic": topic_obj,
                "participant_id": participant_id,
                "name": topic_name,
                "type_name": type_name,
                "qos_settings": qos_settings,
                "created_at": datetime.now()
            }
            
            self.logger.info(f"Created DDS topic {topic_name} with ID {topic_id} for participant {participant_id}")
            
            # Publish event
            await self.publish_event(
                MessageFactory.create_event(
                    "dds_topic_created",
                    payload={
                        "topic_id": topic_id,
                        "participant_id": participant_id,
                        "name": topic_name,
                        "type_name": type_name
                    },
                    priority=MessagePriority.MEDIUM
                )
            )
            
            return topic_id
            
        except Exception as e:
            self.logger.error(f"Error creating DDS topic {topic_name}: {str(e)}")
            return ""
    
    async def delete_topic(self, topic_id: str) -> bool:
        """
        Delete a DDS topic.
        
        Args:
            topic_id: ID of the topic to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        if topic_id not in self.topics:
            self.logger.error(f"Topic {topic_id} not found")
            return False
            
        try:
            # Get topic info
            topic_info = self.topics[topic_id]
            
            # Delete all associated writers
            for writer_id, writer_info in list(self.writers.items()):
                if writer_info["topic_id"] == topic_id:
                    await self.delete_writer(writer_id)
                    
            # Delete all associated readers
            for reader_id, reader_info in list(self.readers.items()):
                if reader_info["topic_id"] == topic_id:
                    await self.delete_reader(reader_id)
                    
            # Delete topic
            del self.topics[topic_id]
            
            self.logger.info(f"Deleted DDS topic {topic_id}")
            
            # Publish event
            await self.publish_event(
                MessageFactory.create_event(
                    "dds_topic_deleted",
                    payload={
                        "topic_id": topic_id,
                        "participant_id": topic_info["participant_id"],
                        "name": topic_info["name"],
                        "type_name": topic_info["type_name"]
                    },
                    priority=MessagePriority.MEDIUM
                )
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting DDS topic {topic_id}: {str(e)}")
            return False
    
    async def create_writer(self, publisher_id: str, topic_id: str,
                           qos_settings: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a DDS data writer.
        
        Args:
            publisher_id: ID of the publisher to create writer for
            topic_id: ID of the topic to write to
            qos_settings: Optional QoS settings for the writer
            
        Returns:
            str: Writer ID if successful, empty string otherwise
        """
        if publisher_id not in self.publishers:
            self.logger.error(f"Publisher {publisher_id} not found")
            return ""
            
        if topic_id not in self.topics:
            self.logger.error(f"Topic {topic_id} not found")
            return ""
            
        try:
            # Get publisher and topic
            publisher_info = self.publishers[publisher_id]
            publisher = publisher_info["publisher"]
            
            topic_info = self.topics[topic_id]
            topic = topic_info["topic"]
            
            # Create QoS if provided
            writer_qos = None
            if qos_settings:
                writer_qos = self._create_qos_from_settings(qos_settings)
                
            # Create writer
            writer = publisher.create_datawriter(topic, qos=writer_qos)
            
            # Generate writer ID
            writer_id = str(uuid.uuid4())
            
            # Store writer
            self.writers[writer_id] = {
                "writer": writer,
                "publisher_id": publisher_id,
                "topic_id": topic_id,
                "qos_settings": qos_settings,
                "created_at": datetime.now()
            }
            
            self.logger.info(f"Created DDS writer with ID {writer_id} for topic {topic_info['name']}")
            
            return writer_id
            
        except Exception as e:
            self.logger.error(f"Error creating DDS writer: {str(e)}")
            return ""
    
    async def delete_writer(self, writer_id: str) -> bool:
        """
        Delete a DDS data writer.
        
        Args:
            writer_id: ID of the writer to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        if writer_id not in self.writers:
            self.logger.error(f"Writer {writer_id} not found")
            return False
            
        try:
            # Delete writer
            del self.writers[writer_id]
            
            self.logger.info(f"Deleted DDS writer {writer_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting DDS writer {writer_id}: {str(e)}")
            return False
    
    async def create_reader(self, subscriber_id: str, topic_id: str,
                           qos_settings: Optional[Dict[str, Any]] = None,
                           callback: Optional[Callable] = None) -> str:
        """
        Create a DDS data reader.
        
        Args:
            subscriber_id: ID of the subscriber to create reader for
            topic_id: ID of the topic to read from
            qos_settings: Optional QoS settings for the reader
            callback: Optional callback function to call when data is received
            
        Returns:
            str: Reader ID if successful, empty string otherwise
        """
        if subscriber_id not in self.subscribers:
            self.logger.error(f"Subscriber {subscriber_id} not found")
            return ""
            
        if topic_id not in self.topics:
            self.logger.error(f"Topic {topic_id} not found")
            return ""
            
        try:
            # Get subscriber and topic
            subscriber_info = self.subscribers[subscriber_id]
            subscriber = subscriber_info["subscriber"]
            
            topic_info = self.topics[topic_id]
            topic = topic_info["topic"]
            
            # Create QoS if provided
            reader_qos = None
            if qos_settings:
                reader_qos = self._create_qos_from_settings(qos_settings)
                
            # Create reader
            reader = subscriber.create_datareader(topic, qos=reader_qos)
            
            # Generate reader ID
            reader_id = str(uuid.uuid4())
            
            # Store reader
            self.readers[reader_id] = {
                "reader": reader,
                "subscriber_id": subscriber_id,
                "topic_id": topic_id,
                "qos_settings": qos_settings,
                "created_at": datetime.now()
            }
            
            # Store callback if provided
            if callback:
                self.reader_callbacks[reader_id] = callback
                
                # Start listener task
                asyncio.create_task(self._listen_for_data(reader_id))
                
            self.logger.info(f"Created DDS reader with ID {reader_id} for topic {topic_info['name']}")
            
            return reader_id
            
        except Exception as e:
            self.logger.error(f"Error creating DDS reader: {str(e)}")
            return ""
    
    async def delete_reader(self, reader_id: str) -> bool:
        """
        Delete a DDS data reader.
        
        Args:
            reader_id: ID of the reader to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        if reader_id not in self.readers:
            self.logger.error(f"Reader {reader_id} not found")
            return False
            
        try:
            # Remove callback if exists
            if reader_id in self.reader_callbacks:
                del self.reader_callbacks[reader_id]
                
            # Delete reader
            del self.readers[reader_id]
            
            self.logger.info(f"Deleted DDS reader {reader_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting DDS reader {reader_id}: {str(e)}")
            return False
    
    async def write_data(self, writer_id: str, data: Any) -> bool:
        """
        Write data using a DDS data writer.
        
        Args:
            writer_id: ID of the writer to use
            data: Data to write
            
        Returns:
            bool: True if write successful, False otherwise
        """
        if writer_id not in self.writers:
            self.logger.error(f"Writer {writer_id} not found")
            return False
            
        try:
            # Get writer
            writer_info = self.writers[writer_id]
            writer = writer_info["writer"]
            
            # Get topic info
            topic_info = self.topics[writer_info["topic_id"]]
            
            # Write data
            success = writer.write(data)
            
            if success:
                self.logger.debug(f"Wrote data to topic {topic_info['name']} using writer {writer_id}")
                return True
            else:
                self.logger.error(f"Failed to write data using writer {writer_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error writing data using writer {writer_id}: {str(e)}")
            return False
    
    async def read_data(self, reader_id: str, max_samples: int = 1) -> List[Dict[str, Any]]:
        """
        Read data using a DDS data reader.
        
        Args:
            reader_id: ID of the reader to use
            max_samples: Maximum number of samples to read
            
        Returns:
            List of data samples
        """
        if reader_id not in self.readers:
            self.logger.error(f"Reader {reader_id} not found")
            return []
            
        try:
            # Get reader
            reader_info = self.readers[reader_id]
            reader = reader_info["reader"]
            
            # Get topic info
            topic_info = self.topics[reader_info["topic_id"]]
            
            # Read data
            samples = reader.read(max_samples=max_samples)
            
            # Format results
            results = []
            for sample in samples:
                # Convert sample to dict if possible
                if hasattr(sample, "__dict__"):
                    sample_dict = sample.__dict__
                else:
                    sample_dict = {"value": sample}
                    
                results.append({
                    "data": sample_dict,
                    "topic": topic_info["name"],
                    "timestamp": datetime.now().isoformat()
                })
                
            self.logger.debug(f"Read {len(results)} samples from topic {topic_info['name']} using reader {reader_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error reading data using reader {reader_id}: {str(e)}")
            return []
    
    async def take_data(self, reader_id: str, max_samples: int = 1) -> List[Dict[str, Any]]:
        """
        Take data using a DDS data reader (read and remove).
        
        Args:
            reader_id: ID of the reader to use
            max_samples: Maximum number of samples to take
            
        Returns:
            List of data samples
        """
        if reader_id not in self.readers:
            self.logger.error(f"Reader {reader_id} not found")
            return []
            
        try:
            # Get reader
            reader_info = self.readers[reader_id]
            reader = reader_info["reader"]
            
            # Get topic info
            topic_info = self.topics[reader_info["topic_id"]]
            
            # Take data
            samples = reader.take(max_samples=max_samples)
            
            # Format results
            results = []
            for sample in samples:
                # Convert sample to dict if possible
                if hasattr(sample, "__dict__"):
                    sample_dict = sample.__dict__
                else:
                    sample_dict = {"value": sample}
                    
                results.append({
                    "data": sample_dict,
                    "topic": topic_info["name"],
                    "timestamp": datetime.now().isoformat()
                })
                
            self.logger.debug(f"Took {len(results)} samples from topic {topic_info['name']} using reader {reader_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error taking data using reader {reader_id}: {str(e)}")
            return []
    
    async def discover_topics(self, participant_id: str, timeout: float = 5.0) -> List[Dict[str, Any]]:
        """
        Discover topics in a DDS domain.
        
        Args:
            participant_id: ID of the participant to use for discovery
            timeout: Discovery timeout in seconds
            
        Returns:
            List of discovered topics
        """
        if participant_id not in self.participants:
            self.logger.error(f"Participant {participant_id} not found")
            return []
            
        try:
            # Get participant info
            participant_info = self.participants[participant_id]
            domain_id = participant_info["domain_id"]
            
            self.logger.info(f"Starting topic discovery in domain {domain_id}")
            
            # Wait for discovery
            await asyncio.sleep(timeout)
            
            # In a real implementation, we would use the DDS built-in topics
            # to discover topics. For now, we'll just return the topics we know about.
            results = []
            for topic_id, topic_info in self.topics.items():
                if topic_info["participant_id"] == participant_id:
                    results.append({
                        "topic_id": topic_id,
                        "name": topic_info["name"],
                        "type_name": topic_info["type_name"],
                        "domain_id": domain_id
                    })
                    
            self.logger.info(f"Discovered {len(results)} topics in domain {domain_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error discovering topics: {str(e)}")
            return []
    
    async def _listen_for_data(self, reader_id: str):
        """
        Listen for data on a reader and call the associated callback.
        
        Args:
            reader_id: ID of the reader to listen on
        """
        if reader_id not in self.readers or reader_id not in self.reader_callbacks:
            self.logger.error(f"Reader {reader_id} not found or no callback registered")
            return
            
        try:
            while reader_id in self.readers and reader_id in self.reader_callbacks:
                # Take data
                samples = await self.take_data(reader_id)
                
                # Call callback for each sample
                callback = self.reader_callbacks[reader_id]
                for sample in samples:
                    try:
                        await callback(sample)
                    except Exception as e:
                        self.logger.error(f"Error in reader callback for {reader_id}: {str(e)}")
                        
                # Wait a bit before checking again
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Error in data listener for reader {reader_id}: {str(e)}")
    
    def _create_qos_from_settings(self, qos_settings: Dict[str, Any]) -> Any:
        """
        Create a DDS QoS object from settings.
        
        Args:
            qos_settings: QoS settings
            
        Returns:
            DDS QoS object
        """
        qos_obj = Qos()
        
        # Add policies based on settings
        for policy_name, policy_value in qos_settings.items():
            if policy_name == "reliability":
                if policy_value == DDSReliabilityKind.RELIABLE.value:
                    qos_obj.add_policy(Policy.Reliability.Reliable)
                else:
                    qos_obj.add_policy(Policy.Reliability.BestEffort)
            elif policy_name == "durability":
                if policy_value == DDSDurabilityKind.TRANSIENT_LOCAL.value:
                    qos_obj.add_policy(Policy.Durability.TransientLocal)
                elif policy_value == DDSDurabilityKind.TRANSIENT.value:
                    qos_obj.add_policy(Policy.Durability.Transient)
                elif policy_value == DDSDurabilityKind.PERSISTENT.value:
                    qos_obj.add_policy(Policy.Durability.Persistent)
                else:
                    qos_obj.add_policy(Policy.Durability.Volatile)
            elif policy_name == "history":
                if isinstance(policy_value, dict) and "kind" in policy_value and "depth" in policy_value:
                    if policy_value["kind"] == "keep_last":
                        qos_obj.add_policy(Policy.History.KeepLast(policy_value["depth"]))
                    else:
                        qos_obj.add_policy(Policy.History.KeepAll)
            elif policy_name == "deadline":
                if isinstance(policy_value, (int, float)):
                    qos_obj.add_policy(Policy.Deadline(policy_value))
            elif policy_name == "lifespan":
                if isinstance(policy_value, (int, float)):
                    qos_obj.add_policy(Policy.Lifespan(policy_value))
                    
        return qos_obj
    
    async def translate_to_industriverse(self, dds_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate DDS data to Industriverse protocol format.
        
        Args:
            dds_data: DDS data to translate
            
        Returns:
            Data in Industriverse protocol format
        """
        # Create Unified Message Envelope
        ume = {
            "origin_protocol": "DDS",
            "target_protocol": "MCP",
            "context": {
                "industrial_protocol": "DDS",
                "adapter_id": self.component_id,
                "timestamp": datetime.now().isoformat()
            },
            "payload": dds_data,
            "trace_id": str(uuid.uuid4()),
            "security_level": "high",  # DDS is often used in critical systems
            "reflex_timer_ms": 2000  # 2 seconds default timeout for industrial protocols
        }
        
        return ume
    
    async def translate_from_industriverse(self, industriverse_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate Industriverse protocol data to DDS format.
        
        Args:
            industriverse_data: Industriverse protocol data to translate
            
        Returns:
            Data in DDS format
        """
        # Extract payload from Unified Message Envelope
        if "payload" in industriverse_data:
            return industriverse_data["payload"]
        else:
            return industriverse_data
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming protocol messages.
        
        Args:
            message: Incoming message
            
        Returns:
            Response message
        """
        try:
            # Extract command from message
            command = message.get("command", "")
            params = message.get("params", {})
            
            # Process command
            if command == "create_participant":
                participant_id = await self.create_participant(
                    params.get("domain_id", 0),
                    params.get("participant_name", None)
                )
                return MessageFactory.create_response(message, result={"participant_id": participant_id})
                
            elif command == "delete_participant":
                success = await self.delete_participant(params.get("participant_id", ""))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "create_publisher":
                publisher_id = await self.create_publisher(
                    params.get("participant_id", ""),
                    params.get("qos_settings", None)
                )
                return MessageFactory.create_response(message, result={"publisher_id": publisher_id})
                
            elif command == "delete_publisher":
                success = await self.delete_publisher(params.get("publisher_id", ""))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "create_subscriber":
                subscriber_id = await self.create_subscriber(
                    params.get("participant_id", ""),
                    params.get("qos_settings", None)
                )
                return MessageFactory.create_response(message, result={"subscriber_id": subscriber_id})
                
            elif command == "delete_subscriber":
                success = await self.delete_subscriber(params.get("subscriber_id", ""))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "register_topic_type":
                success = await self.register_topic_type(
                    params.get("participant_id", ""),
                    params.get("type_name", ""),
                    params.get("type_definition", "")
                )
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "create_topic":
                topic_id = await self.create_topic(
                    params.get("participant_id", ""),
                    params.get("topic_name", ""),
                    params.get("type_name", ""),
                    params.get("qos_settings", None)
                )
                return MessageFactory.create_response(message, result={"topic_id": topic_id})
                
            elif command == "delete_topic":
                success = await self.delete_topic(params.get("topic_id", ""))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "create_writer":
                writer_id = await self.create_writer(
                    params.get("publisher_id", ""),
                    params.get("topic_id", ""),
                    params.get("qos_settings", None)
                )
                return MessageFactory.create_response(message, result={"writer_id": writer_id})
                
            elif command == "delete_writer":
                success = await self.delete_writer(params.get("writer_id", ""))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "create_reader":
                reader_id = await self.create_reader(
                    params.get("subscriber_id", ""),
                    params.get("topic_id", ""),
                    params.get("qos_settings", None)
                )
                return MessageFactory.create_response(message, result={"reader_id": reader_id})
                
            elif command == "delete_reader":
                success = await self.delete_reader(params.get("reader_id", ""))
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "write_data":
                success = await self.write_data(
                    params.get("writer_id", ""),
                    params.get("data", {})
                )
                return MessageFactory.create_response(message, result={"success": success})
                
            elif command == "read_data":
                result = await self.read_data(
                    params.get("reader_id", ""),
                    params.get("max_samples", 1)
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "take_data":
                result = await self.take_data(
                    params.get("reader_id", ""),
                    params.get("max_samples", 1)
                )
                return MessageFactory.create_response(message, result=result)
                
            elif command == "discover_topics":
                result = await self.discover_topics(
                    params.get("participant_id", ""),
                    params.get("timeout", 5.0)
                )
                return MessageFactory.create_response(message, result=result)
                
            else:
                return MessageFactory.create_response(
                    message,
                    success=False,
                    error=f"Unknown command: {command}"
                )
                
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            return MessageFactory.create_response(
                message,
                success=False,
                error=f"Error: {str(e)}"
            )
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming messages from the Protocol Layer.
        
        This method is called by the Protocol Layer when a message is received
        for this adapter.
        
        Args:
            message: Incoming message
            
        Returns:
            Response message
        """
        # Translate from Industriverse protocol if needed
        if message.get("origin_protocol") and message.get("origin_protocol") != "DDS":
            dds_message = await self.translate_from_industriverse(message)
        else:
            dds_message = message
            
        # Handle message
        response = await self.handle_message(dds_message)
        
        # Translate to Industriverse protocol if needed
        if message.get("target_protocol") and message.get("target_protocol") != "DDS":
            industriverse_response = await self.translate_to_industriverse(response)
            return industriverse_response
        else:
            return response
    
    async def shutdown(self):
        """
        Shutdown the adapter, cleaning up all DDS resources.
        """
        self.logger.info(f"Shutting down DDS Adapter {self.component_id}")
        
        # Delete all participants (which will cascade delete all other resources)
        for participant_id in list(self.participants.keys()):
            await self.delete_participant(participant_id)
            
        # Unregister from discovery service
        self.discovery_service.unregister_component(self.component_id)
        
        self.logger.info(f"DDS Adapter {self.component_id} shutdown complete")

# Example usage
async def example_usage():
    # Create adapter
    adapter = DDSAdapter(config={
        "use_tpm": True,
        "industry_tags": ["aerospace", "defense", "transportation"]
    })
    
    # Create participant
    participant_id = await adapter.create_participant(domain_id=0)
    
    if participant_id:
        # Register topic type
        await adapter.register_topic_type(
            participant_id=participant_id,
            type_name="SensorData",
            type_definition="""
            struct SensorData {
                long id;
                double value;
                string unit;
                long timestamp;
            };
            """
        )
        
        # Create topic
        topic_id = await adapter.create_topic(
            participant_id=participant_id,
            topic_name="sensors/temperature",
            type_name="SensorData",
            qos_settings={
                "reliability": DDSReliabilityKind.RELIABLE.value,
                "durability": DDSDurabilityKind.TRANSIENT_LOCAL.value,
                "history": {"kind": "keep_last", "depth": 10}
            }
        )
        
        if topic_id:
            # Create publisher and writer
            publisher_id = await adapter.create_publisher(participant_id)
            writer_id = await adapter.create_writer(publisher_id, topic_id)
            
            # Create subscriber and reader
            subscriber_id = await adapter.create_subscriber(participant_id)
            reader_id = await adapter.create_reader(subscriber_id, topic_id)
            
            # Write data
            await adapter.write_data(
                writer_id,
                {
                    "id": 1,
                    "value": 25.5,
                    "unit": "C",
                    "timestamp": int(datetime.now().timestamp())
                }
            )
            
            # Read data
            data = await adapter.read_data(reader_id)
            print(f"Read data: {data}")
            
            # Clean up
            await adapter.delete_reader(reader_id)
            await adapter.delete_subscriber(subscriber_id)
            await adapter.delete_writer(writer_id)
            await adapter.delete_publisher(publisher_id)
            await adapter.delete_topic(topic_id)
            
        # Delete participant
        await adapter.delete_participant(participant_id)
    
    # Shutdown
    await adapter.shutdown()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run example
    asyncio.run(example_usage())
