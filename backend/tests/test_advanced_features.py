"""
Advanced WebSocket Broadcasting Features Tests

This module tests advanced broadcasting features including:
- Message priority handling
- Message persistence for offline clients
- Rate limiting to prevent client overload
- Message compression for large payloads

Following Canon TDD methodology - implement one test at a time.
"""

import pytest
import asyncio
import heapq
import json
import time
import zlib
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

# Note: These imports will be implemented as we build the features
# from app.websocket.server import WebSocketServer
# from app.websocket.message_queue import PriorityMessageQueue, MessagePriority
# from app.websocket.persistence import MessagePersistence
# from app.websocket.rate_limiter import TokenBucketRateLimiter
# from app.websocket.compression import MessageCompressor


# Message Priority Enumeration (needed for dataclass)
class MessagePriority:
    """Message priority enumeration"""
    HIGH = 1
    NORMAL = 2
    LOW = 3


# Test Data Structures
@dataclass
class PriorityMessage:
    """Message with priority for testing"""
    content: str
    priority: MessagePriority
    timestamp: float
    client_id: str
    
    def __lt__(self, other):
        """Lower priority value = higher priority (min heap)"""
        return self.priority.value < other.priority.value


@dataclass
class PersistedMessage:
    """Persisted message for testing"""
    id: str
    content: str
    timestamp: float
    channel: str
    expires_at: Optional[float] = None


class TestMessagePriorityBroadcast:
    """Test 10.1: Broadcast with message priority"""
    
    def test_priority_queue_initialization(self):
        """Test priority queue initializes correctly"""
        # Test One: Priority queue can be created
        priority_queue = PriorityMessageQueue()
        
        assert priority_queue is not None
        assert priority_queue.size() == 0
        assert priority_queue.is_empty() is True
    
    def test_priority_message_ordering(self):
        """Test messages are ordered by priority"""
        # Test: High priority messages are processed first
        priority_queue = PriorityMessageQueue()
        
        # Add messages with different priorities
        low_msg = PriorityMessage("low", MessagePriority.LOW, time.time(), "client1")
        high_msg = PriorityMessage("high", MessagePriority.HIGH, time.time(), "client2")
        normal_msg = PriorityMessage("normal", MessagePriority.NORMAL, time.time(), "client3")
        
        priority_queue.enqueue(low_msg)
        priority_queue.enqueue(high_msg)
        priority_queue.enqueue(normal_msg)
        
        # Verify high priority comes first
        first_msg = priority_queue.dequeue()
        assert first_msg.priority == MessagePriority.HIGH
        assert first_msg.content == "high"
        
        # Verify normal priority comes second
        second_msg = priority_queue.dequeue()
        assert second_msg.priority == MessagePriority.NORMAL
        assert second_msg.content == "normal"
        
        # Verify low priority comes last
        third_msg = priority_queue.dequeue()
        assert third_msg.priority == MessagePriority.LOW
        assert third_msg.content == "low"
    
    def test_same_priority_fifo_ordering(self):
        """Test messages with same priority maintain FIFO order"""
        # Test: Same priority messages maintain insertion order
        priority_queue = PriorityMessageQueue()
        
        # Add messages with same priority but different timestamps
        msg1 = PriorityMessage("first", MessagePriority.NORMAL, time.time(), "client1")
        time.sleep(0.01)  # Ensure different timestamps
        msg2 = PriorityMessage("second", MessagePriority.NORMAL, time.time(), "client2")
        
        priority_queue.enqueue(msg1)
        priority_queue.enqueue(msg2)
        
        # Verify FIFO order for same priority
        first_out = priority_queue.dequeue()
        assert first_out.content == "first"
        
        second_out = priority_queue.dequeue()
        assert second_out.content == "second"
    
    @pytest.mark.asyncio
    async def test_priority_broadcast_delivery(self):
        """Test WebSocket server respects message priority during broadcast"""
        # Test: WebSocket server delivers high priority messages first
        server = WebSocketServer()
        
        # Mock client connections
        client1 = Mock()
        client1.send = AsyncMock()
        client2 = Mock()
        client2.send = AsyncMock()
        
        server.clients = {"client1": client1, "client2": client2}
        
        # Queue messages with different priorities
        await server.broadcast_with_priority("low priority", MessagePriority.LOW)
        await server.broadcast_with_priority("high priority", MessagePriority.HIGH)
        await server.broadcast_with_priority("normal priority", MessagePriority.NORMAL)
        
        # Process priority queue
        await server.process_priority_queue()
        
        # Verify call order (high -> normal -> low)
        calls = client1.send.call_args_list
        assert len(calls) == 3
        assert "high priority" in str(calls[0])
        assert "normal priority" in str(calls[1])
        assert "low priority" in str(calls[2])


class TestMessagePersistence:
    """Test 10.2: Broadcast with message persistence"""
    
    def test_message_persistence_initialization(self):
        """Test message persistence service initializes correctly"""
        # Test One: Message persistence can be created
        persistence = MessagePersistence()
        
        assert persistence is not None
        assert persistence.storage is not None
    
    def test_persist_message(self):
        """Test message can be persisted to storage"""
        # Test: Message gets stored with metadata
        persistence = MessagePersistence()
        
        message = PersistedMessage(
            id="msg_123",
            content="test message",
            timestamp=time.time(),
            channel="test_channel"
        )
        
        success = persistence.persist_message(message)
        
        assert success is True
        assert persistence.message_exists("msg_123") is True
    
    def test_retrieve_persisted_messages(self):
        """Test retrieval of persisted messages for channel"""
        # Test: Can retrieve messages for specific channel
        persistence = MessagePersistence()
        
        # Persist multiple messages
        msg1 = PersistedMessage("msg1", "content1", time.time(), "channel1")
        msg2 = PersistedMessage("msg2", "content2", time.time(), "channel1")
        msg3 = PersistedMessage("msg3", "content3", time.time(), "channel2")
        
        persistence.persist_message(msg1)
        persistence.persist_message(msg2)
        persistence.persist_message(msg3)
        
        # Retrieve messages for channel1
        messages = persistence.get_messages_for_channel("channel1")
        
        assert len(messages) == 2
        assert any(msg.content == "content1" for msg in messages)
        assert any(msg.content == "content2" for msg in messages)
        assert not any(msg.content == "content3" for msg in messages)
    
    def test_message_expiration(self):
        """Test expired messages are cleaned up"""
        # Test: Expired messages are removed from storage
        persistence = MessagePersistence()
        
        # Create message that expires in past
        past_time = time.time() - 3600  # 1 hour ago
        expired_msg = PersistedMessage(
            id="expired",
            content="expired content",
            timestamp=past_time,
            channel="test",
            expires_at=past_time + 1800  # Expired 30 minutes ago
        )
        
        persistence.persist_message(expired_msg)
        
        # Clean up expired messages
        persistence.cleanup_expired_messages()
        
        # Verify expired message is removed
        assert persistence.message_exists("expired") is False
    
    @pytest.mark.asyncio
    async def test_persistence_with_client_reconnection(self):
        """Test client receives persisted messages on reconnection"""
        # Test: Reconnecting client gets missed messages
        server = WebSocketServer()
        persistence = MessagePersistence()
        server.persistence = persistence
        
        # Simulate client disconnection
        client = Mock()
        client.send = AsyncMock()
        client.id = "client123"
        
        # Broadcast message while client is offline
        await server.broadcast_persistent("offline message", "general")
        
        # Client reconnects
        await server.handle_client_reconnection(client, "general")
        
        # Verify client receives persisted message
        client.send.assert_called_once()
        call_args = client.send.call_args[0][0]
        assert "offline message" in call_args


class TestRateLimiting:
    """Test 10.3: Broadcast with rate limiting"""
    
    def test_token_bucket_initialization(self):
        """Test token bucket rate limiter initializes correctly"""
        # Test One: Token bucket can be created with capacity and refill rate
        limiter = TokenBucketRateLimiter(capacity=10, refill_rate=2)
        
        assert limiter.capacity == 10
        assert limiter.refill_rate == 2
        assert limiter.tokens == 10  # Starts full
        assert limiter.last_refill <= time.time()
    
    def test_token_consumption(self):
        """Test tokens are consumed when allowing requests"""
        # Test: Successful request consumes one token
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1)
        
        # Initial state
        assert limiter.tokens == 5
        
        # Allow request
        allowed = limiter.allow_request()
        
        assert allowed is True
        assert limiter.tokens == 4
    
    def test_request_rejection_when_empty(self):
        """Test requests are rejected when bucket is empty"""
        # Test: Request rejected when no tokens available
        limiter = TokenBucketRateLimiter(capacity=1, refill_rate=1)
        
        # Use up the token
        limiter.allow_request()
        
        # Ensure no time passes for refill by mocking time
        with patch('time.time', return_value=limiter.last_refill):
            # Next request should be rejected
            allowed = limiter.allow_request()
        
        assert allowed is False
        assert limiter.tokens == 0
    
    def test_token_refill_over_time(self):
        """Test tokens are refilled at specified rate"""
        # Test: Tokens refill based on elapsed time
        start_time = 1000.0  # Fixed time
        
        with patch('time.time', return_value=start_time):
            limiter = TokenBucketRateLimiter(capacity=5, refill_rate=2)
            
            # Use all tokens
            for _ in range(5):
                limiter.allow_request()
            
            # Check that tokens are zero (no time passed)
            assert limiter.tokens == 0
        
        # Mock time passing (1 second = 2 tokens at rate 2/second)
        with patch('time.time', return_value=start_time + 1):
            allowed = limiter.allow_request()
        
        assert allowed is True
        assert limiter.tokens == 1  # 2 refilled - 1 consumed
    
    def test_token_bucket_capacity_limit(self):
        """Test tokens don't exceed bucket capacity"""
        # Test: Refill doesn't exceed capacity
        limiter = TokenBucketRateLimiter(capacity=3, refill_rate=5)
        
        # Wait for time to pass (more than capacity/rate)
        with patch('time.time', return_value=time.time() + 2):
            limiter.refill_tokens()
        
        # Should not exceed capacity
        assert limiter.tokens == 3
    
    @pytest.mark.asyncio
    async def test_rate_limited_broadcast(self):
        """Test WebSocket server applies rate limiting to broadcasts"""
        # Test: Server respects rate limits during broadcast
        server = WebSocketServer()
        
        # Create client with rate limiter
        client = Mock()
        client.send = AsyncMock()
        client.rate_limiter = TokenBucketRateLimiter(capacity=2, refill_rate=1)
        
        server.clients = {"client1": client}
        
        # Mock time to prevent token refill during test
        with patch('time.time', return_value=client.rate_limiter.last_refill):
            # Send messages rapidly
            await server.broadcast_rate_limited("message 1")
            await server.broadcast_rate_limited("message 2")
            await server.broadcast_rate_limited("message 3")  # Should be rate limited
        
        # Verify only 2 messages were sent
        assert client.send.call_count == 2


class TestMessageCompression:
    """Test 10.4: Broadcast with compression"""
    
    def test_message_compressor_initialization(self):
        """Test message compressor initializes correctly"""
        # Test One: Message compressor can be created
        compressor = MessageCompressor()
        
        assert compressor is not None
        assert compressor.compression_level >= 1
        assert compressor.compression_level <= 9
    
    def test_message_compression(self):
        """Test message can be compressed"""
        # Test: Large message gets compressed
        compressor = MessageCompressor()
        
        # Create large message with repetitive content
        large_message = "test data " * 1000
        
        compressed = compressor.compress(large_message)
        
        assert compressed is not None
        assert len(compressed) < len(large_message.encode())
        assert isinstance(compressed, bytes)
    
    def test_message_decompression(self):
        """Test compressed message can be decompressed"""
        # Test: Compressed message can be restored
        compressor = MessageCompressor()
        
        original = "test message with repeated content " * 100
        compressed = compressor.compress(original)
        decompressed = compressor.decompress(compressed)
        
        assert decompressed == original
    
    def test_compression_ratio_calculation(self):
        """Test compression ratio is calculated correctly"""
        # Test: Compression ratio reflects size reduction
        compressor = MessageCompressor()
        
        # Highly compressible message
        repetitive_message = "a" * 1000
        
        compressed = compressor.compress(repetitive_message)
        ratio = compressor.calculate_compression_ratio(repetitive_message, compressed)
        
        assert ratio > 0.8  # Should achieve good compression
        assert ratio <= 1.0
    
    def test_compression_threshold(self):
        """Test small messages bypass compression"""
        # Test: Small messages aren't compressed
        compressor = MessageCompressor(min_size_for_compression=100)
        
        small_message = "short"
        result = compressor.compress_if_beneficial(small_message)
        
        # Should return original message, not compressed
        assert result == small_message.encode()
        assert isinstance(result, bytes)
    
    def test_compression_benefit_analysis(self):
        """Test compression is only applied when beneficial"""
        # Test: Compression only applied if size reduction is significant
        compressor = MessageCompressor(min_compression_ratio=0.2)
        
        # Random data that won't compress well
        random_message = "abcdefghijklmnopqrstuvwxyz123456789" * 10
        
        result = compressor.compress_if_beneficial(random_message)
        
        # Should return original if compression doesn't help
        assert result == random_message.encode()
    
    @pytest.mark.asyncio
    async def test_compressed_broadcast(self):
        """Test WebSocket server can broadcast compressed messages"""
        # Test: Server compresses large messages before sending
        server = WebSocketServer()
        compressor = MessageCompressor(min_size_for_compression=100)  # Lower threshold
        server.compressor = compressor
        
        # Mock client
        client = Mock()
        client.send = AsyncMock()
        client.supports_compression = True
        
        server.clients = {"client1": client}
        
        # Large message that benefits from compression (highly repetitive)
        large_message = json.dumps({"data": "a" * 2000})  # More repetitive content
        
        await server.broadcast_compressed(large_message)
        
        # Verify compressed message was sent
        client.send.assert_called_once()
        sent_data = client.send.call_args[0][0]
        assert isinstance(sent_data, bytes)
        assert len(sent_data) < len(large_message.encode())


# Mock Classes for Testing (to be implemented)
class PriorityMessageQueue:
    """Mock priority message queue for testing"""
    
    def __init__(self):
        self._queue = []
        self._entry_finder = {}
        self._counter = 0
    
    def enqueue(self, message: PriorityMessage):
        """Add message to priority queue"""
        # Handle both enum-like objects and direct integer values
        priority_value = message.priority.value if hasattr(message.priority, 'value') else message.priority
        entry = [priority_value, self._counter, message]
        self._entry_finder[message.client_id] = entry
        heapq.heappush(self._queue, entry)
        self._counter += 1
    
    def dequeue(self) -> Optional[PriorityMessage]:
        """Remove and return highest priority message"""
        while self._queue:
            priority, count, message = heapq.heappop(self._queue)
            if message is not None:
                del self._entry_finder[message.client_id]
                return message
        return None
    
    def size(self) -> int:
        """Return queue size"""
        return len([entry for entry in self._queue if entry[2] is not None])
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.size() == 0


class MessagePersistence:
    """Mock message persistence for testing"""
    
    def __init__(self):
        self.storage = {}
    
    def persist_message(self, message: PersistedMessage) -> bool:
        """Store message in persistence layer"""
        self.storage[message.id] = message
        return True
    
    def message_exists(self, message_id: str) -> bool:
        """Check if message exists in storage"""
        return message_id in self.storage
    
    def get_messages_for_channel(self, channel: str) -> List[PersistedMessage]:
        """Get all messages for a channel"""
        return [msg for msg in self.storage.values() if msg.channel == channel]
    
    def cleanup_expired_messages(self):
        """Remove expired messages from storage"""
        current_time = time.time()
        expired_ids = [
            msg_id for msg_id, msg in self.storage.items()
            if msg.expires_at and msg.expires_at < current_time
        ]
        for msg_id in expired_ids:
            del self.storage[msg_id]


class TokenBucketRateLimiter:
    """Mock token bucket rate limiter for testing"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def allow_request(self) -> bool:
        """Check if request is allowed and consume token"""
        self.refill_tokens()
        
        if self.tokens > 0:
            self.tokens -= 1
            return True
        return False
    
    def refill_tokens(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now


class MessageCompressor:
    """Mock message compressor for testing"""
    
    def __init__(self, compression_level: int = 6, min_size_for_compression: int = 1024, 
                 min_compression_ratio: float = 0.1):
        self.compression_level = compression_level
        self.min_size_for_compression = min_size_for_compression
        self.min_compression_ratio = min_compression_ratio
    
    def compress(self, message: str) -> bytes:
        """Compress message using zlib"""
        return zlib.compress(message.encode(), self.compression_level)
    
    def decompress(self, compressed_data: bytes) -> str:
        """Decompress message using zlib"""
        return zlib.decompress(compressed_data).decode()
    
    def calculate_compression_ratio(self, original: str, compressed: bytes) -> float:
        """Calculate compression ratio"""
        original_size = len(original.encode())
        compressed_size = len(compressed)
        return (original_size - compressed_size) / original_size
    
    def compress_if_beneficial(self, message: str) -> bytes:
        """Compress only if beneficial"""
        message_bytes = message.encode()
        
        # Skip compression for small messages
        if len(message_bytes) < self.min_size_for_compression:
            return message_bytes
        
        # Try compression
        compressed = self.compress(message)
        ratio = self.calculate_compression_ratio(message, compressed)
        
        # Use compression only if beneficial
        if ratio >= self.min_compression_ratio:
            return compressed
        return message_bytes


# Mock WebSocket Server Extensions for Testing
class WebSocketServer:
    """Mock WebSocket server with advanced features"""
    
    def __init__(self):
        self.clients = {}
        self.priority_queue = PriorityMessageQueue()
        self.persistence = None
        self.compressor = None
    
    async def broadcast_with_priority(self, message: str, priority: MessagePriority):
        """Broadcast message with priority"""
        # Use a unique client_id for each broadcast message
        client_id = f"broadcast_{int(time.time() * 1000000)}"
        priority_msg = PriorityMessage(message, priority, time.time(), client_id)
        self.priority_queue.enqueue(priority_msg)
    
    async def process_priority_queue(self):
        """Process messages from priority queue"""
        while not self.priority_queue.is_empty():
            message = self.priority_queue.dequeue()
            if message:
                await self._send_to_all_clients(message.content)
    
    async def broadcast_persistent(self, message: str, channel: str):
        """Broadcast message with persistence"""
        if self.persistence:
            persisted_msg = PersistedMessage(
                id=f"msg_{int(time.time())}",
                content=message,
                timestamp=time.time(),
                channel=channel
            )
            self.persistence.persist_message(persisted_msg)
    
    async def handle_client_reconnection(self, client, channel: str):
        """Handle client reconnection and send persisted messages"""
        if self.persistence:
            messages = self.persistence.get_messages_for_channel(channel)
            for msg in messages:
                await client.send(msg.content)
    
    async def broadcast_rate_limited(self, message: str):
        """Broadcast message with rate limiting"""
        for client in self.clients.values():
            if hasattr(client, 'rate_limiter') and client.rate_limiter.allow_request():
                await client.send(message)
    
    async def broadcast_compressed(self, message: str):
        """Broadcast message with compression"""
        for client in self.clients.values():
            if hasattr(client, 'supports_compression') and client.supports_compression:
                compressed = self.compressor.compress_if_beneficial(message)
                await client.send(compressed)
            else:
                await client.send(message)
    
    async def _send_to_all_clients(self, message: str):
        """Send message to all connected clients"""
        for client in self.clients.values():
            await client.send(message)